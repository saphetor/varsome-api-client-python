#!/usr/bin/env python3
"""CLI tool for annotating a VCF file via the VarSome API."""

import argparse
import asyncio
import time

from varsome_api.cli.utils import (
    build_base_parser,
    configure_logging,
    parse_request_parameters,
    validate_batch_args,
    validate_file_args,
)
from varsome_api.log import logger
from varsome_api.vcf import VCFAnnotator


def build_parser() -> argparse.ArgumentParser:
    """Build and return the argument parser for ``varsome_api_annotate_vcf``.

    Extends the shared base parser with VCF-annotation-specific arguments:
    ``-i`` (input VCF) and ``-o`` (output VCF).

    Returns:
        Configured ``ArgumentParser`` ready for ``parse_args()``.
    """
    parser = build_base_parser("VCF Annotator command line")
    parser.add_argument(
        "-i",
        help="Path to vcf file",
        type=str,
        metavar="Input VCF File",
        required=True,
    )
    parser.add_argument(
        "-o",
        help="Path to output vcf file",
        type=str,
        metavar="Output VCF File",
        required=False,
    )
    return parser


def validate_args(args: argparse.Namespace) -> None:
    """Validate file-related and batch argument constraints for VCF annotation.

    Args:
        args: Parsed CLI arguments.

    Raises:
        SystemExit: When any validation check fails.
    """
    validate_batch_args(args)
    validate_file_args(input_file=args.i, output_file=args.o)


async def annotate() -> None:
    """Parse CLI arguments and run the async VCF annotation pipeline."""
    args = build_parser().parse_args()
    configure_logging(verbose=args.verbose)
    validate_args(args)
    request_parameters = parse_request_parameters(args.p)

    vcf_annotator = VCFAnnotator(
        api_key=args.k,
        api_url=args.u,
        ref_genome=args.g,
        request_parameters=request_parameters,
        max_requests=args.t,
        max_variants_per_batch=args.m,
    )
    async with vcf_annotator:
        start = time.monotonic()
        result = await vcf_annotator.aannotate(args.i, args.o)
        elapsed = time.monotonic() - start
    for variant, filtered in result.filtered_out_variants:
        logger.info(
            "Filtered out variant %s: %s",
            variant,
            filtered.get("filtered_out", filtered),
        )
    for variant, errored in result.variants_with_errors:
        logger.error(
            "Error for variant %s: %s",
            variant,
            errored.get("error", errored),
        )
    logger.info(
        "Annotated %d variant(s) in %.2f seconds. "
        "Filtered out %d variant(s). Errors in %d variant(s)",
        result.total_variants,
        elapsed,
        len(result.filtered_out_variants),
        len(result.variants_with_errors),
    )


def main() -> None:
    asyncio.run(annotate())
