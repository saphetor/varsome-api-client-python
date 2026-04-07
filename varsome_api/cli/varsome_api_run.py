#!/usr/bin/env python3
"""CLI tool for performing single or batch lookups (variants, genes,
or CNVs) via the VarSome API."""

import argparse
import asyncio
import sys
import time
from collections.abc import AsyncGenerator, AsyncIterable
from typing import Any

from varsome_api.cli.utils import (
    build_base_parser,
    configure_logging,
    parse_request_parameters,
    stream_json_output,
    validate_batch_args,
    validate_file_args,
)
from varsome_api.client import VarSomeAPIClient
from varsome_api.constants import (
    DEFAULT_QUERY_TYPE,
    DEFAULT_REF_GENOME,
    QUERY_TYPES,
    QueryType,
    RefGenome,
)
from varsome_api.log import logger


def build_parser() -> argparse.ArgumentParser:
    """Build and return the argument parser for ``varsome_api_run``.

    Extends the shared base parser with lookup-specific arguments:
    ``-q`` (query), ``-i`` (input file), ``-o`` (output file), and
    ``-y`` (query type).

    Returns:
        Configured ``ArgumentParser`` ready for ``parse_args()``.
    """
    parser = build_base_parser("Sample VarSome API calls")
    parser.add_argument(
        "-q",
        help=(
            "Query to lookup in the API. Format depends on query type (-y): "
            "variants: chr19:20082943:1:G or chr15-73027478-T-C; "
            "genes: BRCA1 or TP53; cnvs: chr1:122:5235:DEL. "
            "For batch requests, use multiple values. "
            "Don't use it together with the -i option"
        ),
        type=str,
        metavar="Query",
        required=False,
        nargs="+",
    )
    parser.add_argument(
        "-i",
        help=(
            "Path to text file with queries (one per line). "
            "Format depends on query type (-y): variants, genes, or CNV queries. "
            "Don't use it together with the -q option"
        ),
        type=str,
        metavar="Text/CSV File one line per query",
        required=False,
    )
    parser.add_argument(
        "-o",
        help="Path to output file to store results",
        type=str,
        metavar="Output File with json entries",
        required=False,
    )
    parser.add_argument(
        "-y",
        help=(
            "Query type: 'variants', 'genes', or 'cnvs'. "
            "Note: CNV queries do not support batch mode, each "
            "CNV is looked up individually. "
            "Check documentation for batch limits per environment"
        ),
        type=str,
        choices=QUERY_TYPES,
        metavar="Query Type",
        required=False,
        default=DEFAULT_QUERY_TYPE,
    )
    return parser


def validate_args(args: argparse.Namespace) -> None:
    """Validate mutually-exclusive and required argument constraints.

    Args:
        args: Parsed CLI arguments.

    Raises:
        SystemExit: When any validation check fails.
    """
    if args.q and args.i:
        sys.stderr.write(
            "Don't specify -i and -q options together. Use only one of them\n"
        )
        sys.exit(1)
    if not args.q and not args.i:
        sys.stderr.write("Please either specify -i or -q options\n")
        sys.exit(1)
    validate_batch_args(args)
    validate_file_args(input_file=args.i, output_file=args.o)


async def _stream_batch_results(
    api: VarSomeAPIClient,
    queries: list[str] | AsyncIterable[str],
    *,
    query_type: QueryType,
    request_parameters: dict[str, str] | None,
    ref_genome: RefGenome = DEFAULT_REF_GENOME,
    max_requests: int = 5,
) -> AsyncGenerator[dict[str, Any], None]:
    """Stream annotation results as they arrive, logging warnings and errors.

    Yields individual response items as they come in from the API, avoiding
    accumulation of large result sets in memory.

    Args:
        api: An initialised VarSome API client.
        queries: Query strings (variants, genes, or CNV queries).
        query_type: Type of query: 'variants', 'genes', or 'cnvs'.
        request_parameters: Optional additional API query parameters.
        ref_genome: Reference genome identifier (``"hg19"`` or ``"hg38"``).
        max_requests: Maximum number of concurrent API requests.

    Yields:
        Individual annotation result dicts as they arrive.
    """
    if query_type == "cnvs":
        # CNVs don't support batch mode, process each one individually
        async for query in _ensure_async_iterable(queries):
            try:
                yield await api.alookup(
                    query,
                    params=request_parameters,
                    ref_genome=ref_genome,
                    query_type="cnvs",
                )
            except Exception as e:
                logger.error("Error for CNV %s: %s", query, str(e))
    else:
        # Variants and genes use batch mode
        async for batch_result in api.abatch_lookup(
            queries,
            params=request_parameters,
            ref_genome=ref_genome,
            max_requests=max_requests,
            query_type=query_type,
        ):
            item_type = "Gene" if query_type == "genes" else "Variant"
            for idx, response_item in enumerate(batch_result.response):
                query_string = batch_result.queries[idx]
                if "filtered_out" in response_item:
                    logger.warning(
                        "%s filtered out: %s — %s",
                        item_type,
                        query_string,
                        response_item.get("filtered_out"),
                    )
                elif "error" in response_item:
                    logger.error(
                        "Error for %s %s: %s",
                        item_type.lower(),
                        query_string,
                        response_item.get("error"),
                    )
                yield response_item


async def _ensure_async_iterable(
    queries: list[str] | AsyncIterable[str],
) -> AsyncGenerator[str, None]:
    """Ensure that queries are yielded as an async iterable."""
    if isinstance(queries, list):
        for query in queries:
            yield query
    else:
        async for query in queries:
            yield query


def lookup_query(
    api: VarSomeAPIClient,
    query: list[str],
    *,
    query_type: QueryType,
    request_parameters: dict[str, str] | None,
    ref_genome: RefGenome = DEFAULT_REF_GENOME,
    max_requests: int = 5,
) -> AsyncGenerator[dict[str, Any], None]:
    """Perform a single or batch lookup from CLI query arguments.

    Args:
        api: An initialised VarSome API client.
        query: One or more query strings.
        query_type: Type of query: 'variants', 'genes', or 'cnvs'.
        request_parameters: Optional additional API query parameters.
        ref_genome: Reference genome identifier (``"hg19"`` or ``"hg38"``).
        max_requests: Maximum number of concurrent API requests.

    Returns:
        An async generator that yields result dicts.
    """

    return _stream_batch_results(
        api,
        query,
        query_type=query_type,
        request_parameters=request_parameters,
        ref_genome=ref_genome,
        max_requests=max_requests,
    )


async def lookup_from_file(
    api: VarSomeAPIClient,
    input_file: str,
    *,
    query_type: QueryType,
    request_parameters: dict[str, str] | None,
    ref_genome: RefGenome = DEFAULT_REF_GENOME,
    max_requests: int = 5,
) -> AsyncGenerator[dict[str, Any], None]:
    """Stream results for queries read from a text file.

    Queries are streamed from the file line by line to avoid loading the
    entire file into memory. Results are yielded as they arrive from the API.

    Args:
        api: An initialised VarSome API client.
        input_file: Path to a text file with one query per line.
        query_type: Type of query: 'variants', 'genes', or 'cnvs'.
        request_parameters: Optional additional API query parameters.
        ref_genome: Reference genome identifier.
        max_requests: Maximum number of concurrent API requests.

    Yields:
        Result dicts as they arrive from the API.
    """

    async for result in _stream_batch_results(
        api,
        _iter_queries_from_file(input_file),
        query_type=query_type,
        request_parameters=request_parameters,
        ref_genome=ref_genome,
        max_requests=max_requests,
    ):
        yield result


async def _iter_queries_from_file(input_file: str) -> AsyncGenerator[str, None]:
    """Yield non-empty query strings from a text file one line at a time.

    Args:
        input_file: Path to a text file with one query per line.

    Yields:
        Stripped, non-empty query strings in file order.
    """
    with open(input_file) as f:
        for line in f:
            if stripped := line.strip():
                yield stripped


async def run() -> None:
    """Async entry point that drives the full CLI workflow.

    Parses command-line arguments, performs lookups via the VarSome API,
    and streams JSON results to stdout or an output file.
    """
    parser = build_parser()
    args = parser.parse_args()
    configure_logging(verbose=args.verbose)
    validate_args(args)

    request_parameters = parse_request_parameters(args.p)

    async with VarSomeAPIClient(
        args.k, api_url=args.u, max_variants_per_batch=args.m
    ) as api:
        try:
            start = time.monotonic()
            result_stream = (
                lookup_query(
                    api,
                    args.q,
                    query_type=args.y,
                    request_parameters=request_parameters,
                    ref_genome=args.g,
                    max_requests=args.t,
                )
                if args.q
                else lookup_from_file(
                    api,
                    args.i,
                    query_type=args.y,
                    request_parameters=request_parameters,
                    ref_genome=args.g,
                    max_requests=args.t,
                )
            )
            await stream_json_output(result_stream, args.o)

            elapsed = time.monotonic() - start
            logger.info("Lookup completed in %.2f seconds", elapsed)
        except Exception as e:
            sys.stderr.write(f"{e}\n")
            sys.exit(1)


def main() -> None:
    """Entry point for the ``varsome_api_run`` CLI command."""
    asyncio.run(run())
