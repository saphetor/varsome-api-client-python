import argparse
import json
import logging
import os
import sys
from collections.abc import AsyncIterable
from typing import IO, Any

from varsome_api.constants import REFERENCE_GENOMES
from varsome_api.log import logger

MAX_CONCURRENT_REQUESTS = 20
DEFAULT_REQUESTS = 5
DEFAULT_VARIANTS_PER_BATCH = 100
VARSOME_API_URL_CHOICES = [
    "https://api.varsome.com",
    "https://stable-api.varsome.com",
    "https://staging-api.varsome.com",
]
DEFAULT_PARAMETER = ["add-ACMG-annotation=1"]


def build_base_parser(description: str) -> argparse.ArgumentParser:
    """Build an argument parser pre-loaded with common VarSome API CLI flags.

    Adds the following arguments common to all VarSome CLI tools:

    * ``-k`` — API key (required)
    * ``-g`` — reference genome (default ``hg19``)
    * ``-p`` — request parameters (``key=value`` pairs)
    * ``-u`` — custom API host URL
    * ``-t`` — max concurrent API requests (default ``5``)
    * ``-m`` — max items per batch request (default ``100``)
    * ``-v`` / ``--verbose`` — enable debug logging

    Callers should extend the returned parser with command-specific arguments
    before calling ``parse_args()``.

    Args:
        description: Description text shown in ``--help`` output.

    Returns:
        An ``ArgumentParser`` with common arguments already registered.
    """
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "-k",
        help="Your key to the API",
        type=str,
        metavar="API Key",
        required=True,
    )
    parser.add_argument(
        "-g",
        help="Reference genome either hg19 or hg38",
        type=str,
        choices=REFERENCE_GENOMES,
        metavar="Reference Genome",
        required=False,
        default=REFERENCE_GENOMES[0],
    )
    parser.add_argument(
        "-p",
        help=(
            "Request parameters e.g. add-ACMG-annotation=1. "
            "Check https://api.varsome.com/docs/variants/ query parameters "
            "for available parameters"
        ),
        type=str,
        metavar="Request Params",
        required=False,
        default=DEFAULT_PARAMETER,
        nargs="+",
    )
    parser.add_argument(
        "-u",
        help=(
            f"Use specific VarSome API host url "
            f"among: {', '.join(VARSOME_API_URL_CHOICES)}"
        ),
        type=str,
        choices=VARSOME_API_URL_CHOICES,
        required=False,
        metavar="VarSome API host url",
    )
    parser.add_argument(
        "-t",
        help="Maximum number of concurrent API requests",
        type=int,
        default=DEFAULT_REQUESTS,
        required=False,
        metavar="Max concurrent requests",
    )
    parser.add_argument(
        "-m",
        help="Maximum number of items to send per batch request",
        type=int,
        default=DEFAULT_VARIANTS_PER_BATCH,
        required=False,
        metavar="Max items per batch",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help="Enable verbose (debug) logging output",
        action="store_true",
        default=False,
    )
    return parser


def validate_file_args(
    *,
    input_file: str | None = None,
    output_file: str | None = None,
) -> None:
    """Validate input and output file arguments common to all CLI tools.

    Exits the process with an error message when validation fails.

    Args:
        input_file: Path to an input file. When provided, the file must
            exist on disk.
        output_file: Path to an output file. When provided, the file must
            **not** already exist (to avoid accidental overwrites).

    Raises:
        SystemExit: When any file validation check fails.
    """
    if input_file is not None and not os.path.exists(input_file):
        sys.stderr.write(f"File {input_file} does not exist\n")
        sys.exit(1)
    if output_file is not None and os.path.exists(output_file):
        sys.stderr.write(f"File {output_file} already exists\n")
        sys.exit(1)


def validate_batch_args(args: argparse.Namespace) -> None:
    """Validate and clamp the ``-t`` batch argument in-place.

    Ensures ``-t`` (max concurrent requests) is between 1 and
    :data:`MAX_CONCURRENT_REQUESTS`.  Values outside the allowed range
    are clamped with a logged warning.

    Args:
        args: Parsed CLI arguments (modified in-place).
    """
    if args.t < 1:
        logger.warning("Concurrency must be at least 1, setting it to 1.")
        args.t = 1
    if args.t > MAX_CONCURRENT_REQUESTS:
        logger.warning(
            "Maximum number of concurrent requests is capped at %d. "
            "Setting it to %d.",
            MAX_CONCURRENT_REQUESTS,
            MAX_CONCURRENT_REQUESTS,
        )
        args.t = MAX_CONCURRENT_REQUESTS


def configure_logging(*, verbose: bool = False) -> None:
    """Configure logging for CLI entry points.

    Sets up a ``StreamHandler`` on the ``varsome_api_client`` logger with a
    human-readable format.  The level defaults to ``INFO`` and switches to
    ``DEBUG`` when *verbose* is ``True``.

    Args:
        verbose: When ``True``, set the log level to ``DEBUG``.
    """
    level = logging.DEBUG if verbose else logging.INFO
    logger = logging.getLogger("varsome_api_client")
    logger.setLevel(level)
    handler = logging.StreamHandler()
    handler.setLevel(level)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def parse_request_parameters(raw_params: list[str] | None) -> dict[str, str] | None:
    """Parse key=value CLI parameters into a dictionary.

    Each element in *raw_params* is expected to be a string of the form
    ``"key=value"``.  Malformed entries (missing ``=``) are reported and skipped.

    Args:
        raw_params: List of ``"key=value"`` strings as collected by
            argparse ``nargs="+"``, or ``None`` if the flag was not used.

    Returns:
        A dict mapping parameter names to their values, or ``None`` when
        *raw_params* is ``None`` or empty.
    """
    if not raw_params:
        return None
    parameters: dict[str, str] = {}
    for param in raw_params:
        parts = param.split("=", maxsplit=1)
        if len(parts) != 2:
            logger.warning(
                "Ignoring malformed parameter (expected key=value): %s", param
            )
            continue
        parameters[parts[0]] = parts[1]
    return parameters or None


async def stream_json_output(
    results: AsyncIterable[dict[str, Any]],
    output_file: str | None = None,
    *,
    stream: IO[str] | None = None,
) -> None:
    """Stream JSON Lines output (one JSON object per line) from an async iterable.

    Writes results immediately as they arrive from the async iterable,
    avoiding accumulation of large result sets in memory.

    Args:
        results: Async iterable of JSON-serializable dicts.
        output_file: When provided, write to this file path. Otherwise use stream.
        stream: Writable text stream. Defaults to ``sys.stdout``.
    """
    if output_file:
        with open(output_file, "w") as fp:
            async for item in results:
                fp.write(json.dumps(item, sort_keys=True))
                fp.write("\n")
    else:
        stream = stream or sys.stdout
        async for item in results:
            stream.write(json.dumps(item, sort_keys=True))
            stream.write("\n")
