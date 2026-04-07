import asyncio
import contextlib
import functools
import time
from collections.abc import AsyncGenerator, Callable
from dataclasses import dataclass
from typing import Any, AsyncIterable, Iterable, Literal

import aiohttp

from varsome_api import __version__
from varsome_api._sync import run_sync, sync_wrapper
from varsome_api.constants import (
    DEFAULT_QUERY_TYPE,
    DEFAULT_REF_GENOME,
    QueryType,
    RefGenome,
)
from varsome_api.exceptions import VarSomeAPIException
from varsome_api.log import logger

DEFAULT_HEADERS = {
    "Accept": "application/json",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "User-Agent": f"VarSomeApiClientPython/{__version__}",
}

DEFAULT_API_URL = "https://api.varsome.com"


@dataclass(frozen=True, slots=True, kw_only=True)
class BatchResult:
    """Pairs a batch of queries with the corresponding API response.

    Allows callers to correlate which queries (variants, genes, CNVs, etc.)
    were sent in a particular batch request with the response returned by
    the API. This is especially useful when the response contains errors
    that omit the original query identifier.

    Attributes:
        queries: The query strings sent in this batch request (variants,
            genes, CNVs, or other query types).
        response: The parsed JSON response from the API for this batch.
    """

    queries: list[str]
    response: list[dict[str, Any]]


def _log_request_time(func: Callable) -> Callable:
    """Decorator that logs the wall-clock time of an async request.

    Expects the wrapped function to receive ``path`` and ``method`` keyword
    arguments.  For POST requests carrying a ``json`` payload with a
    ``"variants"`` key the number of variants in the batch is logged;
    GET requests are logged as a single-variant lookup.

    Args:
        func: The async function to wrap.

    Returns:
        An async wrapper that logs elapsed time and variant count after
        the call completes.
    """

    @functools.wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.monotonic()
        path = kwargs.get("path", "<unknown path>")
        method = kwargs.get("method", "GET")
        json_body = kwargs.get("json")
        if method == "POST" and isinstance(json_body, dict):
            variant_count = len(json_body.get("variants", []))
        else:
            variant_count = 1
        try:
            return await func(*args, **kwargs)
        finally:
            elapsed = time.monotonic() - start_time
            logger.debug(
                "Request on %s took %.2f seconds (%d variant(s))",
                path,
                elapsed,
                variant_count,
            )

    return wrapper


class VarSomeAPIClientBase:
    """Base client for the VarSome API providing HTTP session and request handling.

    Can be used as an async context manager to maintain a persistent session
    across multiple requests::

        async with VarSomeAPIClientBase(api_key="...") as client:
            await client.get("/lookup/chr7-140453136-A-T")
            await client.get("/lookup/chr19-20082943-1-G")

    When used without the context manager, each ``get``/``post`` call creates
    and closes its own session automatically.
    """

    def __init__(
        self,
        api_key: str | None = None,
        api_url: str | None = None,
    ) -> None:
        self.api_url = api_url or DEFAULT_API_URL
        self._headers = DEFAULT_HEADERS.copy()
        if api_key is not None:
            self._headers["Authorization"] = f"Token {api_key}"
        self._session: aiohttp.ClientSession | None = None

    async def __aenter__(self) -> "VarSomeAPIClientBase":
        self._session = aiohttp.ClientSession(self.api_url, headers=self._headers)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> None:
        if self._session is not None:
            await self._session.close()
            self._session = None

    def _create_session(self) -> aiohttp.ClientSession:
        """Create a new ``aiohttp.ClientSession`` bound to the API base URL."""
        return aiohttp.ClientSession(self.api_url, headers=self._headers)

    @contextlib.asynccontextmanager
    async def _ensure_session(self) -> AsyncGenerator[aiohttp.ClientSession, None]:
        """Yield the persistent session if open, otherwise a temporary one.

        When the client is used as an async context manager, the existing
        session is reused.  Otherwise, a fresh session is created and closed
        at the end of the ``async with`` block.
        """
        if self._session is not None and not self._session.closed:
            yield self._session
        else:
            async with self._create_session() as session:
                yield session

    @staticmethod
    @_log_request_time
    async def _make_request(
        session: aiohttp.ClientSession,
        *,
        path: str,
        method: Literal["GET", "POST"] = "GET",
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Execute an HTTP request against the VarSome API.

        This is a generic request executor. Callers are responsible for
        passing method-specific arguments (e.g. ``json`` and ``headers``
        for POST requests).

        Args:
            session: An active aiohttp client session.
            path: The API endpoint path (appended to the session base URL).
            method: HTTP method, either ``"GET"`` or ``"POST"``.
            params: Optional query-string parameters.
            json: Optional JSON-serializable body payload.
            headers: Optional extra headers to merge into the request.

        Returns:
            The parsed JSON response as a dictionary.

        Raises:
            VarSomeAPIException: On HTTP error status codes, timeouts, or
                connection failures.
        """
        request_kwargs: dict[str, Any] = {
            "url": path,
            "params": params,
        }
        if json is not None:
            request_kwargs["json"] = json
        if headers is not None:
            request_kwargs["headers"] = headers
        try:
            async with session.request(method, **request_kwargs) as response:
                if response.status in VarSomeAPIException.ERROR_CODES:
                    error_message = await response.json()
                    raise VarSomeAPIException(response.status, error_message)
                return await response.json()
        except aiohttp.ServerTimeoutError as e:
            raise VarSomeAPIException(None, f"Request timed out {e}") from e
        except aiohttp.ClientConnectionError as e:
            raise VarSomeAPIException(
                None, f"Connection failure or connection refused {e}"
            ) from e
        except aiohttp.ClientError as e:
            raise VarSomeAPIException(None, f"Unknown error {e}") from e

    async def get(
        self,
        path: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Perform an async GET request against the API.

        Args:
            path: The API endpoint path.
            params: Optional query-string parameters.

        Returns:
            The parsed JSON response as a dictionary.

        Raises:
            VarSomeAPIException: On HTTP error status codes, timeouts, or
                connection failures.
        """
        async with self._ensure_session() as session:
            return await self._make_request(
                session,
                path=path,
                method="GET",
                params=params,
            )

    async def post(
        self,
        path: str,
        params: dict[str, Any] | None = None,
        json_data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Perform an async POST request against the API.

        Args:
            path: The API endpoint path.
            params: Optional query-string parameters.
            json_data: Optional JSON body payload.

        Returns:
            The parsed JSON response as a dictionary.

        Raises:
            VarSomeAPIException: On HTTP error status codes, timeouts, or
                connection failures.
        """
        async with self._ensure_session() as session:
            return await self._make_request(
                session,
                path=path,
                method="POST",
                params=params,
                json=json_data,
                headers={"Content-Type": "application/json"},
            )


class VarSomeAPIClient(VarSomeAPIClientBase):
    """High-level client for single and batch lookups (variants, genes, or CNVs) via the VarSome API.

    Supports querying variants, genes, and CNVs with a unified interface.
    The query_type parameter controls endpoint selection and request/response handling.
    """

    # API endpoint paths
    _ENDPOINTS = {
        "variants": {
            "single": "/lookup/%s/%s",  # query, ref_genome
            "batch": "/lookup/batch/%s",  # ref_genome
            "batch_key": "variants",
        },
        "genes": {
            "single": "/lookup/gene/%s/%s",  # gene_symbol, ref_genome
            "batch": "/lookup/genes/batch/%s",  # ref_genome
            "batch_key": "genes",
        },
        "cnvs": {
            "single": "/lookup/cnv/%s/%s",  # query, ref_genome
            "batch": None,  # CNVs don't support batch
            "batch_key": None,
        },
    }

    def __init__(
        self,
        api_key: str | None = None,
        api_url: str | None = None,
        max_variants_per_batch: int = 200,
    ) -> None:
        """Initialise the lookup client.

        Args:
            api_key: Optional API authentication token.
            api_url: Optional custom API base URL.
            max_variants_per_batch: Maximum number of items sent in a
                single batch POST request. Must be a positive integer.
        """
        super().__init__(api_key, api_url)
        self.max_variants_per_batch = max_variants_per_batch

    @staticmethod
    def _get_single_url(
        query_type: QueryType, query: str, ref_genome: RefGenome
    ) -> str:
        """Build the single-item lookup URL for the given query type.

        Args:
            query_type: Type of query: 'variants', 'genes', or 'cnvs'.
            query: The query string (variant, gene symbol, or CNV query).
            ref_genome: Reference genome identifier.

        Returns:
            The formatted URL path.
        """
        return VarSomeAPIClient._ENDPOINTS[query_type]["single"] % (query, ref_genome)

    @staticmethod
    def _get_batch_url(query_type: QueryType, ref_genome: RefGenome) -> str | None:
        """Build the batch lookup URL for the given query type.

        Args:
            query_type: Type of query: 'variants', 'genes', or 'cnvs'.
            ref_genome: Reference genome identifier.

        Returns:
            The formatted URL path, or None if batch is not supported.
        """
        batch_path = VarSomeAPIClient._ENDPOINTS[query_type]["batch"]
        return batch_path % ref_genome if batch_path else None

    @staticmethod
    def _get_batch_key(query_type: QueryType) -> str | None:
        """Get the JSON key name for batch request payloads.

        Args:
            query_type: Type of query: 'variants', 'genes', or 'cnvs'.

        Returns:
            The key name (e.g., 'variants' or 'genes'), or None if batch is not supported.
        """
        return VarSomeAPIClient._ENDPOINTS[query_type]["batch_key"]

    async def alookup(
        self,
        query: str,
        params: dict[str, Any] | None = None,
        ref_genome: RefGenome = DEFAULT_REF_GENOME,
        query_type: QueryType = DEFAULT_QUERY_TYPE,
    ) -> dict[str, Any]:
        """Look up annotations for a single item (variant, gene, or CNV) asynchronously.

        Args:
            query: The query string (variant representation, gene symbol, or CNV query).
            params: Optional HTTP GET parameters.
            ref_genome: Reference genome (``"hg19"`` or ``"hg38"``).
            query_type: Type of query: 'variants', 'genes', or 'cnvs'.

        Returns:
            A dictionary of annotations.
        """
        url = self._get_single_url(query_type, query, ref_genome)
        return await self.get(url, params=params)

    lookup = sync_wrapper(alookup)

    async def _batch_producer(
        self, items: Iterable[str] | AsyncIterable[str], queue: asyncio.Queue
    ) -> None:
        """Add batches of items to the request queue."""
        batch = []
        if isinstance(items, AsyncIterable):
            async for item in items:
                batch.append(item)
                if len(batch) >= self.max_variants_per_batch:
                    await queue.put(batch)
                    batch = []
        else:
            for item in items:
                batch.append(item)
                if len(batch) >= self.max_variants_per_batch:
                    await queue.put(batch)
                    batch = []
        if batch:
            await queue.put(batch)
        await queue.put(None)

    async def _batch_worker(
        self,
        session: aiohttp.ClientSession,
        request_queue: asyncio.Queue,
        result_queue: asyncio.Queue,
        url: str,
        params: dict[str, Any] | None,
        batch_key: str,
    ) -> None:
        """Consume batches from the request queue and send them to the API.

        Args:
            session: Active aiohttp client session.
            request_queue: Queue of batches to process.
            result_queue: Queue to put results/exceptions into.
            url: The API endpoint URL.
            params: Optional query parameters.
            batch_key: The JSON key for the batch payload (e.g., 'variants' or 'genes').
        """
        while True:
            batch = await request_queue.get()
            if batch is None:
                request_queue.task_done()
                break
            try:
                response = await self._make_request(
                    session,
                    path=url,
                    method="POST",
                    params=params,
                    json={batch_key: batch},
                    headers={"Content-Type": "application/json"},
                )
                await result_queue.put(BatchResult(queries=batch, response=response))
            except VarSomeAPIException as e:
                await result_queue.put(e)
            finally:
                request_queue.task_done()

    async def abatch_lookup(
        self,
        items: Iterable[str] | AsyncIterable[str] | AsyncGenerator[Any, None],
        params: dict[str, Any] | None = None,
        ref_genome: RefGenome = DEFAULT_REF_GENOME,
        max_requests: int = 5,
        query_type: QueryType = DEFAULT_QUERY_TYPE,
    ) -> AsyncGenerator[BatchResult, None]:
        """Look up annotations for a list of items asynchronously in batches.

        Supports variants, genes, and CNVs (though CNVs don't support batch mode).
        Splits items into batches of *max_variants_per_batch* and sends them
        concurrently via POST requests. Concurrency is bounded by *max_requests*
        worker tasks — at most that many HTTP requests are in-flight at any given time.

        Each yielded ``BatchResult`` pairs the original query strings with
        the API response, allowing callers to correlate inputs with outputs.

        Args:
            items: Query strings to look up (sync or async iterable).
            params: Optional dictionary of query parameters.
            ref_genome: Reference genome, either ``"hg19"`` or ``"hg38"``.
            max_requests: Maximum number of concurrent HTTP requests.
            query_type: Type of query: 'variants', 'genes', or 'cnvs'.

        Yields:
            A ``BatchResult`` for each batch, in completion order.

        Raises:
            VarSomeAPIException: If any batch request fails. All remaining
                in-flight requests are cancelled, and the exception is propagated.
        """
        batch_url = self._get_batch_url(query_type, ref_genome)
        batch_key = self._get_batch_key(query_type)

        if batch_url is None or batch_key is None:
            raise ValueError(
                f"Query type '{query_type}' does not support batch operations. "
                "Use single item lookups instead."
            )

        request_queue = asyncio.Queue(maxsize=max_requests * 2)
        response_queue: asyncio.Queue[BatchResult | Exception | None] = asyncio.Queue()

        async with self._ensure_session() as session:
            producer_task = asyncio.create_task(
                self._batch_producer(items, request_queue)
            )
            workers = [
                asyncio.create_task(
                    self._batch_worker(
                        session,
                        request_queue,
                        response_queue,
                        batch_url,
                        params,
                        batch_key,
                    )
                )
                for _ in range(max_requests)
            ]

            async def wrap_up():
                await producer_task
                await request_queue.join()
                await response_queue.put(None)

            wrap_up_task = asyncio.create_task(wrap_up())

            try:
                while True:
                    result = await response_queue.get()
                    if result is None:
                        break
                    if isinstance(result, Exception):
                        raise result
                    yield result
            finally:
                producer_task.cancel()
                wrap_up_task.cancel()
                for w in workers:
                    w.cancel()
                await asyncio.gather(
                    producer_task, wrap_up_task, *workers, return_exceptions=True
                )

    def batch_lookup(
        self,
        items: list[str],
        params: dict[str, Any] | None = None,
        ref_genome: RefGenome = DEFAULT_REF_GENOME,
        max_requests: int = 5,
        query_type: QueryType = DEFAULT_QUERY_TYPE,
    ) -> list[BatchResult]:
        """Synchronous wrapper around :meth:`abatch_lookup`.

        Collects every batch result into a list and returns it.

        Args:
            items: List of query strings to look up (variants, genes, etc.).
            params: Optional dictionary of query parameters.
            ref_genome: Reference genome, either "hg19" or "hg38".
            max_requests: Maximum number of concurrent requests.
            query_type: Type of query: 'variants', 'genes', or 'cnvs'.

        Returns:
            A list of ``BatchResult`` objects, one per batch.

        Raises:
            VarSomeAPIException: If any batch request fails.
        """

        async def _collect() -> list[BatchResult]:
            return [
                result
                async for result in self.abatch_lookup(
                    items,
                    params=params,
                    ref_genome=ref_genome,
                    max_requests=max_requests,
                    query_type=query_type,
                )
            ]

        return run_sync(_collect())
