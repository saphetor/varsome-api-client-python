import asyncio
from collections.abc import AsyncGenerator, Callable
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import pytest

from varsome_api.client import (
    DEFAULT_API_URL,
    DEFAULT_HEADERS,
    BatchResult,
    VarSomeAPIClient,
    VarSomeAPIClientBase,
)
from varsome_api.exceptions import VarSomeAPIException


def _build_mock_session(status: int, json_data: Any) -> MagicMock:
    """Return a ``MagicMock`` aiohttp session whose request yields *json_data*.
    Args:
        status: HTTP status code the mock response should report.
        json_data: The value returned by ``response.json()``.
    Returns:
        A ``MagicMock`` that mimics an ``aiohttp.ClientSession``.
    """
    mock_resp = AsyncMock()
    mock_resp.status = status
    mock_resp.json = AsyncMock(return_value=json_data)
    cm = MagicMock()
    cm.__aenter__ = AsyncMock(return_value=mock_resp)
    cm.__aexit__ = AsyncMock(return_value=False)
    session = MagicMock()
    session.request = MagicMock(return_value=cm)
    return session


class TestBatchResult:
    """Verify the ``BatchResult`` dataclass behaviour."""

    def test_stores_variants_and_response(self) -> None:
        variants = ["chr1:100:A:T", "chr2:200:G:C"]
        response = [{"chromosome": "chr1"}, {"chromosome": "chr2"}]
        result = BatchResult(variants=variants, response=response)
        assert result.variants == variants
        assert result.response == response

    def test_correlates_errors_with_input(self) -> None:
        """When the API returns an error without the original variant,
        callers can still identify the batch that caused it."""
        variants = ["chr1:100:A:T", "chr7:BAD:X:Y"]
        response = [
            {"chromosome": "chr1", "original_variant": "chr1:100:A:T"},
            {"error": "Invalid variant format"},
        ]
        result = BatchResult(variants=variants, response=response)
        errors = [r for r in result.response if "error" in r]
        assert len(errors) == 1
        assert result.variants == variants


class TestVarSomeAPIClientBaseInit:
    """Verify ``VarSomeAPIClientBase`` initialization and header configuration."""

    def test_default_api_url(self) -> None:
        client = VarSomeAPIClientBase(api_key="key123")
        assert client.api_url == DEFAULT_API_URL

    def test_custom_api_url(self) -> None:
        client = VarSomeAPIClientBase(api_key="key123", api_url="https://custom.api")
        assert client.api_url == "https://custom.api"

    def test_auth_header_set_when_key_provided(self) -> None:
        client = VarSomeAPIClientBase(api_key="mytoken")
        assert client._headers["Authorization"] == "Token mytoken"

    def test_no_auth_header_without_key(self) -> None:
        client = VarSomeAPIClientBase()
        assert "Authorization" not in client._headers

    def test_headers_contain_defaults(self) -> None:
        client = VarSomeAPIClientBase()
        for key, value in DEFAULT_HEADERS.items():
            assert client._headers[key] == value


class TestVarSomeAPIClientBaseContextManager:
    """Verify ``VarSomeAPIClientBase`` async context manager behaviour."""

    async def test_aenter_creates_session(self) -> None:
        """``__aenter__`` must create an open ``aiohttp.ClientSession``."""
        client = VarSomeAPIClientBase(api_key="test")
        await client.__aenter__()
        try:
            assert client._session is not None
            assert not client._session.closed
        finally:
            await client.__aexit__(None, None, None)

    async def test_aexit_closes_and_clears_session(self) -> None:
        """``__aexit__`` must close the session and set ``_session`` to ``None``."""
        async with VarSomeAPIClientBase(api_key="test") as client:
            assert client._session is not None
        assert client._session is None

    async def test_aexit_noop_when_session_is_none(self) -> None:
        """``__aexit__`` must be a no-op when ``_session`` is already ``None``."""
        client = VarSomeAPIClientBase()
        assert client._session is None
        await client.__aexit__(None, None, None)  # must not raise
        assert client._session is None


class TestVarSomeAPIClientBaseMakeRequest:
    """Verify ``VarSomeAPIClientBase._make_request`` HTTP handling."""

    async def test_get_returns_json_response(self) -> None:
        session = _build_mock_session(200, {"chromosome": "chr1"})
        result = await VarSomeAPIClientBase._make_request(
            session, path="/lookup/chr1:100:A:T", method="GET"
        )
        assert result == {"chromosome": "chr1"}
        session.request.assert_called_once_with(
            "GET", url="/lookup/chr1:100:A:T", params=None
        )

    async def test_post_forwards_json_and_headers(self) -> None:
        """POST with json body and custom headers passes them through correctly."""
        session = _build_mock_session(200, [{"id": "v1"}])
        result = await VarSomeAPIClientBase._make_request(
            session,
            path="/lookup/batch/hg19",
            method="POST",
            json={"variants": ["v1"]},
            headers={"Content-Type": "application/json"},
        )
        assert result == [{"id": "v1"}]
        _, call_kwargs = session.request.call_args
        assert call_kwargs["json"] == {"variants": ["v1"]}
        assert call_kwargs["headers"] == {"Content-Type": "application/json"}

    async def test_optional_json_and_headers_omitted_when_not_supplied(self) -> None:
        """``json`` and ``headers`` must not appear in the request when absent."""
        session = _build_mock_session(200, {})
        await VarSomeAPIClientBase._make_request(session, path="/lookup/chr1:100:A:T")
        _, call_kwargs = session.request.call_args
        assert "json" not in call_kwargs
        assert "headers" not in call_kwargs

    async def test_error_status_raises_varsome_exception(self) -> None:
        """HTTP 4xx/5xx responses must raise ``VarSomeAPIException``."""
        session = _build_mock_session(400, {"detail": "bad request"})
        with pytest.raises(VarSomeAPIException) as exc_info:
            await VarSomeAPIClientBase._make_request(
                session, path="/lookup/bad", method="GET"
            )
        assert exc_info.value.status == 400

    @pytest.mark.parametrize(
        ("exc_class", "expected_fragment"),
        [
            (aiohttp.ServerTimeoutError, "timed out"),
            (aiohttp.ClientConnectionError, "Connection failure"),
            (aiohttp.ClientError, "Unknown error"),
        ],
        ids=["timeout", "connection_error", "generic_client_error"],
    )
    async def test_aiohttp_transport_errors_wrapped(
        self,
        exc_class: type[aiohttp.ClientError],
        expected_fragment: str,
    ) -> None:
        """aiohttp transport errors must be re-raised as ``VarSomeAPIException``."""
        session = MagicMock()
        session.request = MagicMock(side_effect=exc_class())
        with pytest.raises(VarSomeAPIException) as exc_info:
            await VarSomeAPIClientBase._make_request(
                session, path="/lookup/chr1:100:A:T", method="GET"
            )
        assert expected_fragment in str(exc_info.value)


class TestVarSomeAPIClientBaseGet:
    """Verify ``VarSomeAPIClientBase.get``."""

    async def test_returns_response(self) -> None:
        """``get`` must delegate to ``_make_request`` and return its result."""
        expected: dict[str, Any] = {"chromosome": "chr1"}
        client = VarSomeAPIClientBase(api_key="test")
        with patch.object(
            type(client), "_make_request", new=AsyncMock(return_value=expected)
        ):
            result = await client.get("/lookup/chr1:100:A:T")
        assert result == expected

    async def test_passes_params(self) -> None:
        """Query parameters must be forwarded to ``_make_request``."""
        client = VarSomeAPIClientBase(api_key="test")
        mock_request = AsyncMock(return_value={})
        with patch.object(type(client), "_make_request", new=mock_request):
            await client.get("/lookup/chr1:100:A:T", params={"expand": "1"})
        _, kwargs = mock_request.call_args
        assert kwargs.get("params") == {"expand": "1"}
        assert kwargs.get("method") == "GET"


class TestVarSomeAPIClientBasePost:
    """Verify ``VarSomeAPIClientBase.post``."""

    async def test_returns_response(self) -> None:
        """``post`` must delegate to ``_make_request`` and return its result."""
        expected: dict[str, Any] = {"ok": True}
        client = VarSomeAPIClientBase(api_key="test")
        with patch.object(
            type(client), "_make_request", new=AsyncMock(return_value=expected)
        ):
            result = await client.post(
                "/lookup/batch/hg19", json_data={"variants": ["v1"]}
            )
        assert result == expected

    async def test_forwards_json_data(self) -> None:
        """``json_data`` must be passed as ``json`` with a JSON content-type header."""
        client = VarSomeAPIClientBase(api_key="test")
        mock_request = AsyncMock(return_value={})
        with patch.object(type(client), "_make_request", new=mock_request):
            await client.post("/lookup/batch/hg19", json_data={"variants": ["v1"]})
        _, kwargs = mock_request.call_args
        assert kwargs.get("method") == "POST"
        assert kwargs.get("json") == {"variants": ["v1"]}
        assert kwargs.get("headers") == {"Content-Type": "application/json"}


class TestVarSomeAPIClientInit:
    """Verify ``VarSomeAPIClient``-specific initialisation."""

    def test_default_max_variants_per_batch(self) -> None:
        client = VarSomeAPIClient()
        assert client.max_variants_per_batch == 200

    def test_custom_max_variants_per_batch(self) -> None:
        client = VarSomeAPIClient(max_variants_per_batch=50)
        assert client.max_variants_per_batch == 50

    def test_inherits_base_auth_header(self) -> None:
        client = VarSomeAPIClient(api_key="mytoken")
        assert client._headers["Authorization"] == "Token mytoken"

    def test_inherits_base_api_url(self) -> None:
        client = VarSomeAPIClient(api_url="https://custom.api")
        assert client.api_url == "https://custom.api"


class TestVarSomeAPIClientLookup:
    """Verify ``VarSomeAPIClient.alookup`` and its sync wrapper ``lookup``."""

    async def test_alookup_returns_annotation(self) -> None:
        """``alookup`` must return the JSON annotation dict from the API."""
        expected: dict[str, Any] = {"chromosome": "chr1", "position": 100}
        client = VarSomeAPIClient(api_key="test")
        with patch.object(client, "get", new=AsyncMock(return_value=expected)):
            result = await client.alookup("chr1:100:A:T", ref_genome="hg19")
        assert result == expected

    async def test_alookup_constructs_correct_url(self) -> None:
        """URL must follow the pattern ``/lookup/<query>/<ref_genome>``."""
        client = VarSomeAPIClient(api_key="test")
        mock_get = AsyncMock(return_value={})
        with patch.object(client, "get", new=mock_get):
            await client.alookup("chr1:100:A:T", ref_genome="hg19")
        mock_get.assert_called_once_with("/lookup/chr1:100:A:T/hg19", params=None)

    async def test_alookup_forwards_params(self) -> None:
        """Optional query params must be forwarded unchanged to ``get``."""
        client = VarSomeAPIClient(api_key="test")
        mock_get = AsyncMock(return_value={})
        with patch.object(client, "get", new=mock_get):
            await client.alookup(
                "chr1:100:A:T",
                params={"exclude-source-databases": "gnomad-genomes"},
                ref_genome="hg38",
            )
        _, kwargs = mock_get.call_args
        assert kwargs.get("params") == {"exclude-source-databases": "gnomad-genomes"}

    def test_lookup_is_sync_wrapper_around_alookup(self) -> None:
        """``lookup`` must block and return the same result as ``alookup``."""
        expected: dict[str, Any] = {"chromosome": "chr19"}
        client = VarSomeAPIClient(api_key="test")
        with patch.object(client, "get", new=AsyncMock(return_value=expected)):
            result = client.lookup("chr19:20082943:1:G", ref_genome="hg19")
        assert result == expected


class TestVarSomeAPIClientBatchProducer:
    """Verify ``VarSomeAPIClient._batch_producer`` chunking behaviour."""

    @pytest.mark.parametrize(
        ("batch_size", "items", "expected"),
        [
            (2, ["v1", "v2", "v3", "v4"], [["v1", "v2"], ["v3", "v4"]]),
            (2, ["v1", "v2", "v3"], [["v1", "v2"], ["v3"]]),
            (10, [], []),
            (10, ["v1"], [["v1"]]),
            (3, ["v1", "v2", "v3"], [["v1", "v2", "v3"]]),
        ],
        ids=[
            "exact_multiples",
            "remainder",
            "empty_list",
            "single_element",
            "batch_equals_length",
        ],
    )
    async def test_sync_iterable_chunking(
        self,
        batch_size: int,
        items: list[str],
        expected: list[list[str]],
    ) -> None:
        """Sync iterables are split into batches of at most *batch_size* items."""
        client = VarSomeAPIClient(max_variants_per_batch=batch_size)
        queue: asyncio.Queue = asyncio.Queue()
        await client._batch_producer(items, queue)
        batches: list[list[str]] = []
        while not queue.empty():
            item = queue.get_nowait()
            if item is None:
                break
            batches.append(list(item))
        assert batches == expected

    async def test_async_iterable_chunked_correctly(self) -> None:
        """Async generators are chunked identically to sync iterables."""

        async def async_variants() -> AsyncGenerator[str, None]:
            for v in ["v1", "v2", "v3", "v4", "v5"]:
                yield v

        client = VarSomeAPIClient(max_variants_per_batch=2)
        queue: asyncio.Queue = asyncio.Queue()
        await client._batch_producer(async_variants(), queue)
        batches: list[list[str]] = []
        while not queue.empty():
            item = queue.get_nowait()
            if item is None:
                break
            batches.append(list(item))
        assert batches == [["v1", "v2"], ["v3", "v4"], ["v5"]]

    async def test_async_iterable_final_partial_batch_flushed(self) -> None:
        """The trailing partial batch must always be put on the queue."""

        async def async_variants() -> AsyncGenerator[str, None]:
            for v in ["a", "b", "c"]:
                yield v

        client = VarSomeAPIClient(max_variants_per_batch=10)
        queue: asyncio.Queue = asyncio.Queue()
        await client._batch_producer(async_variants(), queue)
        items: list[Any] = []
        while not queue.empty():
            items.append(queue.get_nowait())
        assert items[-1] is None
        assert items[:-1] == [["a", "b", "c"]]


class TestVarSomeAPIClientBatchWorker:
    """Verify ``VarSomeAPIClient._batch_worker`` request dispatching."""

    async def test_successful_batch_put_on_result_queue(
        self, make_fake_request: Callable
    ) -> None:
        """A successful request must place a ``BatchResult`` on the result queue."""
        fake = make_fake_request(lambda batch: [{"id": v} for v in batch])
        client = VarSomeAPIClient(api_key="test")
        session = MagicMock()
        request_queue: asyncio.Queue = asyncio.Queue()
        result_queue: asyncio.Queue = asyncio.Queue()
        await request_queue.put(["v1", "v2"])
        await request_queue.put(None)
        with patch.object(type(client), "_make_request", side_effect=fake):
            await client._batch_worker(
                session, request_queue, result_queue, "/lookup/batch/hg19", None
            )
        result = result_queue.get_nowait()
        assert isinstance(result, BatchResult)
        assert result.variants == ["v1", "v2"]

    async def test_failed_batch_puts_exception_on_result_queue(self) -> None:
        """On ``VarSomeAPIException``, the exception must be enqueued, not re-raised."""
        exc = VarSomeAPIException(500, "Server Error")

        async def failing_request(_session: Any, **kwargs: Any) -> Any:
            raise exc

        client = VarSomeAPIClient(api_key="test")
        session = MagicMock()
        request_queue: asyncio.Queue = asyncio.Queue()
        result_queue: asyncio.Queue = asyncio.Queue()
        await request_queue.put(["v1", "v2"])
        await request_queue.put(None)
        with patch.object(type(client), "_make_request", side_effect=failing_request):
            await client._batch_worker(
                session, request_queue, result_queue, "/lookup/batch/hg19", None
            )
        queued = result_queue.get_nowait()
        assert isinstance(queued, VarSomeAPIException)
        assert queued is exc


class TestVarSomeAPIClientBatchLookup:
    """Verify ``VarSomeAPIClient.abatch_lookup`` and its sync wrapper ``batch_lookup``."""

    async def test_yields_batch_results(self, make_fake_request: Callable) -> None:
        """Each yielded item must be a ``BatchResult`` covering at most *batch_size* variants."""
        variants = ["v1", "v2", "v3", "v4", "v5"]
        mock_responses = {
            ("v1", "v2"): [{"id": "1"}, {"id": "2"}],
            ("v3", "v4"): [{"id": "3"}, {"id": "4"}],
            ("v5",): [{"id": "5"}],
        }
        fake = make_fake_request(lambda batch: mock_responses[tuple(batch)])
        client = VarSomeAPIClient(api_key="test", max_variants_per_batch=2)
        async with client:
            with patch.object(type(client), "_make_request", side_effect=fake):
                results = [
                    r
                    async for r in client.abatch_lookup(
                        variants, ref_genome="hg19", max_requests=1
                    )
                ]
        assert len(results) == 3
        for result in results:
            assert isinstance(result, BatchResult)
            assert len(result.variants) <= 2
        all_variants = [v for r in results for v in r.variants]
        assert sorted(all_variants) == sorted(variants)

    async def test_batch_response_paired_with_input(
        self, make_fake_request: Callable
    ) -> None:
        """Each ``BatchResult.response`` must correspond to its ``.variants``."""
        variants = ["chr1:100:A:T", "chr2:200:G:C"]
        fake = make_fake_request(lambda batch: [{"original_variant": v} for v in batch])
        client = VarSomeAPIClient(api_key="test", max_variants_per_batch=10)
        async with client:
            with patch.object(type(client), "_make_request", side_effect=fake):
                results = [
                    r async for r in client.abatch_lookup(variants, ref_genome="hg19")
                ]
        assert len(results) == 1
        assert results[0].variants == variants
        assert results[0].response == [
            {"original_variant": "chr1:100:A:T"},
            {"original_variant": "chr2:200:G:C"},
        ]

    async def test_accepts_async_generator(self, make_fake_request: Callable) -> None:
        """``abatch_lookup`` must accept an async generator in place of a list."""

        async def async_variants() -> AsyncGenerator[str, None]:
            for v in ["v1", "v2", "v3"]:
                yield v

        fake = make_fake_request(lambda batch: [{"id": v} for v in batch])
        client = VarSomeAPIClient(api_key="test", max_variants_per_batch=2)
        with patch.object(type(client), "_make_request", side_effect=fake):
            results = [
                r
                async for r in client.abatch_lookup(async_variants(), ref_genome="hg19")
            ]
        all_variants = [v for r in results for v in r.variants]
        assert sorted(all_variants) == ["v1", "v2", "v3"]

    async def test_propagates_batch_exception(self) -> None:
        """A failed batch must raise ``VarSomeAPIException`` to the caller."""

        async def failing_request(_session: Any, **kwargs: Any) -> Any:
            raise VarSomeAPIException(500, "Server Error")

        client = VarSomeAPIClient(api_key="test", max_variants_per_batch=10)
        with patch.object(type(client), "_make_request", side_effect=failing_request):
            with pytest.raises(VarSomeAPIException):
                async for _ in client.abatch_lookup(["v1", "v2"], ref_genome="hg19"):
                    pass

    def test_batch_lookup_sync_collects_all_results(
        self, make_fake_request: Callable
    ) -> None:
        """``batch_lookup`` must return a flat list of all ``BatchResult`` objects."""
        variants = ["v1", "v2"]
        fake = make_fake_request(lambda batch: [{"id": v} for v in batch])
        client = VarSomeAPIClient(api_key="test", max_variants_per_batch=10)
        with patch.object(type(client), "_make_request", side_effect=fake):
            results = client.batch_lookup(variants, ref_genome="hg19")
        assert len(results) == 1
        assert isinstance(results[0], BatchResult)
        assert results[0].variants == variants
        assert results[0].response == [{"id": "v1"}, {"id": "v2"}]
