import argparse
import logging
import os
import sys
import time
from pathlib import Path

from varsome_api.client import VarSomeAPIClient
from varsome_api.constants import DEFAULT_REF_GENOME, REFERENCE_GENOMES, RefGenome
from varsome_api.exceptions import VarSomeAPIException
from varsome_api.log import logger
from varsome_api.models.slim.annotation import AnnotatedVariant

from writer import ParquetWriter

DEFAULT_INPUT = Path(__file__).parent / "variants.csv"
DEFAULT_OUTPUT = Path(__file__).parent / "annotated_variants.parquet"



def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Annotate variants from a CSV file and write to Parquet.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--api-key",
        default=os.environ.get("VARSOME_API_KEY"),
        help=(
            "VarSome API key. Falls back to the VARSOME_API_KEY environment "
            "variable."
        ),
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help="Path to the input CSV file (one variant per line, no header).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Path for the output Parquet file.",
    )
    parser.add_argument(
        "--genome",
        choices=REFERENCE_GENOMES,
        default=DEFAULT_REF_GENOME,
        help="Reference genome assembly.",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=100,
        help="Maximum number of variants per API batch request.",
    )
    parser.add_argument(
        "--max-requests",
        type=int,
        default=10,
        help="Maximum number of concurrent HTTP requests.",
    )
    return parser


def load_variants(path: Path) -> list[str]:
    with path.open() as fh:
        return [line.strip() for line in fh]


def annotate_and_write(
    variants: list[str],
    *,
    api_key: str | None,
    ref_genome: RefGenome,
    batch_size: int,
    max_requests: int,
    output_path: Path,
) -> tuple[int, int, int]:
    api = VarSomeAPIClient(
        api_key=api_key,
        max_variants_per_batch=batch_size,
    )

    written = 0
    filtered = 0
    errors = 0

    with ParquetWriter(str(output_path)) as pw:
        batch_results = api.batch_lookup(
            variants,
            params={"add-ACMG-annotation": "1"},
            ref_genome=ref_genome,
            max_requests=max_requests,
        )

        for batch in batch_results:
            for i, variant_str in enumerate(batch.variants):
                raw: dict = batch.response[i]

                if "error" in raw:
                    logger.error(
                        "API error for variant %s: %s",
                        variant_str,
                        raw["error"],
                    )
                    errors += 1
                    continue

                if "filtered_out" in raw:
                    logger.warning(
                        "Variant filtered: %s — %s",
                        variant_str,
                        raw["filtered_out"],
                    )
                    filtered += 1
                    continue

                annotated = AnnotatedVariant(**raw)
                pw.add(annotated)
                written += 1

    return written, filtered, errors


def _configure_logging() -> None:
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "%(asctime)s — %(name)s — %(levelname)s — %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)


def main() -> None:
    _configure_logging()

    parser = _build_arg_parser()
    args = parser.parse_args()

    logger.info("Loading variants from %s …", args.input)
    variants = load_variants(args.input)

    logger.info("%d variant(s) loaded", len(variants))

    logger.info(
        "Annotating against %s (batch size=%d, concurrency=%d) …",
        args.genome,
        args.batch_size,
        args.max_requests,
    )

    start_time = time.monotonic()

    try:
        written, filtered, errors = annotate_and_write(
            variants,
            api_key=args.api_key,
            ref_genome=args.genome,
            batch_size=args.batch_size,
            max_requests=args.max_requests,
            output_path=args.output,
        )
    except VarSomeAPIException as exc:
        logger.exception("API error: %s", exc)
        sys.exit(1)

    elapsed_time = time.monotonic() - start_time

    logger.info(
        "Done. Written: %d row(s) → %s, Filtered: %d variant(s), Errors: %d variant(s)",
        written,
        args.output,
        filtered,
        errors,
    )
    logger.info("Total time: %.2f seconds", elapsed_time)


if __name__ == "__main__":
    main()
