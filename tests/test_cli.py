import argparse
import logging
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from varsome_api.cli.utils import (
    build_base_parser,
    configure_logging,
    parse_request_parameters,
    validate_batch_args,
    validate_file_args,
)
from varsome_api.cli.varsome_api_annotate_vcf import (
    build_parser as build_annotate_parser,
)
from varsome_api.cli.varsome_api_annotate_vcf import (
    validate_args as validate_annotate_args,
)
from varsome_api.cli.varsome_api_run import (
    _iter_variants_from_file,
    build_parser,
    lookup_from_file,
    lookup_query,
    validate_args,
)
from varsome_api.client import BatchResult


class TestParseRequestParameters:
    """Verify ``parse_request_parameters`` behaviour."""

    def test_returns_none_when_input_is_none(self) -> None:
        assert parse_request_parameters(None) is None

    def test_returns_none_for_empty_list(self) -> None:
        assert parse_request_parameters([]) is None

    def test_parses_single_key_value_pair(self) -> None:
        result = parse_request_parameters(["add-all-data=1"])
        assert result == {"add-all-data": "1"}

    def test_parses_multiple_key_value_pairs(self) -> None:
        result = parse_request_parameters(
            ["add-all-data=1", "expand-pubmed-articles=0"]
        )
        assert result == {"add-all-data": "1", "expand-pubmed-articles": "0"}

    def test_skips_malformed_entries_and_warns(self) -> None:
        """Entries without ``=`` are skipped with a logged warning."""
        with patch("varsome_api.cli.utils.logger") as mock_logger:
            result = parse_request_parameters(["bad_param", "good=1"])
        assert result == {"good": "1"}
        mock_logger.warning.assert_called_once()
        assert "bad_param" in mock_logger.warning.call_args[0][1]

    def test_returns_none_when_all_entries_malformed(self) -> None:
        with patch("varsome_api.cli.utils.logger"):
            result = parse_request_parameters(["nope", "alsobad"])
        assert result is None


class TestBuildBaseParser:
    """Verify the shared base argument parser is configured correctly."""

    def test_requires_api_key(self) -> None:
        parser = build_base_parser("test")
        with pytest.raises(SystemExit):
            parser.parse_args([])

    def test_defaults_with_api_key(self) -> None:
        parser = build_base_parser("test")
        args = parser.parse_args(["-k", "mykey"])
        assert args.k == "mykey"
        assert args.g == "hg19"
        assert args.p == ["add-ACMG-annotation=1"]
        assert args.u is None
        assert args.t == 5
        assert args.m == 100
        assert args.verbose is False

    def test_all_base_flags(self) -> None:
        parser = build_base_parser("test")
        args = parser.parse_args(
            [
                "-k",
                "mykey",
                "-g",
                "hg38",
                "-p",
                "add-all-data=1",
                "-u",
                "https://staging-api.varsome.com",
                "-t",
                "10",
                "-m",
                "150",
                "-v",
            ]
        )
        assert args.k == "mykey"
        assert args.g == "hg38"
        assert args.p == ["add-all-data=1"]
        assert args.u == "https://staging-api.varsome.com"
        assert args.t == 10
        assert args.m == 150
        assert args.verbose is True

    def test_multiple_request_parameters(self) -> None:
        parser = build_base_parser("test")
        args = parser.parse_args(
            ["-k", "mykey", "-p", "add-all-data=1", "expand-pubmed=0"]
        )
        assert args.p == ["add-all-data=1", "expand-pubmed=0"]


class TestBuildParser:
    """Verify the argument parser is configured correctly."""

    def test_requires_api_key(self) -> None:
        parser = build_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(["-q", "chr1:100:A:T"])

    def test_defaults(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["-k", "mykey", "-q", "chr1:100:A:T"])
        assert args.g == "hg19"
        assert args.q == ["chr1:100:A:T"]
        assert args.k == "mykey"
        assert args.i is None
        assert args.o is None
        assert args.t == 5
        assert args.m == 100
        assert args.p == ["add-ACMG-annotation=1"]

    def test_all_flags(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "-k",
                "mykey",
                "-g",
                "hg38",
                "-q",
                "v1",
                "v2",
                "-p",
                "add-all-data=1",
                "-o",
                "out.json",
                "-u",
                "https://staging-api.varsome.com",
                "-t",
                "10",
                "-m",
                "150",
            ]
        )
        assert args.k == "mykey"
        assert args.g == "hg38"
        assert args.q == ["v1", "v2"]
        assert args.p == ["add-all-data=1"]
        assert args.o == "out.json"
        assert args.u == "https://staging-api.varsome.com"
        assert args.t == 10
        assert args.m == 150


class TestValidateArgs:
    """Verify CLI argument validation."""

    def test_both_q_and_i_exits(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            ["-k", "mykey", "-q", "chr1:100:A:T", "-i", "file.txt"]
        )
        with pytest.raises(SystemExit):
            validate_args(args)

    def test_neither_q_nor_i_exits(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["-k", "mykey"])
        with pytest.raises(SystemExit):
            validate_args(args)

    def test_missing_input_file_exits(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["-k", "mykey", "-i", "/nonexistent/file.txt"])
        with pytest.raises(SystemExit):
            validate_args(args)

    def test_output_file_already_exists_exits(self, tmp_path: Any) -> None:
        existing = tmp_path / "exists.json"
        existing.write_text("{}")
        parser = build_parser()
        args = parser.parse_args(["-k", "mykey", "-q", "v1", "-o", str(existing)])
        with pytest.raises(SystemExit):
            validate_args(args)

    def test_valid_query_passes(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["-k", "mykey", "-q", "chr1:100:A:T"])
        validate_args(args)  # should not raise

    def test_valid_input_file_passes(self, tmp_path: Any) -> None:
        f = tmp_path / "variants.txt"
        f.write_text("chr1:100:A:T\n")
        parser = build_parser()
        args = parser.parse_args(["-k", "mykey", "-i", str(f)])
        validate_args(args)  # should not raise


async def _async_gen_from_list(items: list[Any]) -> Any:
    """Yield items from a list as an async generator."""
    for item in items:
        yield item


class TestIterVariantsFromFile:
    """Verify ``_iter_variants_from_file`` streams lines correctly."""

    async def test_yields_all_non_empty_lines(self, tmp_path: Any) -> None:
        f = tmp_path / "variants.txt"
        f.write_text("v1\nv2\nv3\n")

        result = [v async for v in _iter_variants_from_file(str(f))]

        assert result == ["v1", "v2", "v3"]

    async def test_skips_blank_lines(self, tmp_path: Any) -> None:
        f = tmp_path / "variants.txt"
        f.write_text("v1\n\nv2\n\n\nv3\n")

        result = [v async for v in _iter_variants_from_file(str(f))]

        assert result == ["v1", "v2", "v3"]

    async def test_strips_leading_and_trailing_whitespace(self, tmp_path: Any) -> None:
        f = tmp_path / "variants.txt"
        f.write_text("  v1  \n\tv2\t\n v3\n")

        result = [v async for v in _iter_variants_from_file(str(f))]

        assert result == ["v1", "v2", "v3"]

    async def test_yields_nothing_for_blank_only_file(self, tmp_path: Any) -> None:
        f = tmp_path / "blank.txt"
        f.write_text("\n\n   \n")

        result = [v async for v in _iter_variants_from_file(str(f))]

        assert not result

    async def test_yields_nothing_for_empty_file(self, tmp_path: Any) -> None:
        f = tmp_path / "empty.txt"
        f.write_text("")

        result = [v async for v in _iter_variants_from_file(str(f))]

        assert not result

    async def test_preserves_file_order(self, tmp_path: Any) -> None:
        variants = [f"chr{i}:100:A:T" for i in range(1, 6)]
        f = tmp_path / "ordered.txt"
        f.write_text("\n".join(variants) + "\n")

        result = [v async for v in _iter_variants_from_file(str(f))]

        assert result == variants


class TestLookupQuery:
    """Verify ``lookup_query`` delegates correctly to the async API."""

    async def test_single_query_calls_alookup(self) -> None:
        api = MagicMock()
        api.abatch_lookup = MagicMock(
            return_value=_async_gen_from_list(
                [
                    BatchResult(
                        variants=["chr1:100:A:T"],
                        response=[{"variant_id": "123"}],
                    )
                ]
            )
        )

        result = lookup_query(
            api,
            ["chr1:100:A:T"],
            request_parameters=None,
            ref_genome="hg19",
            max_requests=5,
        )

        result_list = [item async for item in result]

        api.abatch_lookup.assert_called_once_with(
            ["chr1:100:A:T"], params=None, ref_genome="hg19", max_requests=5
        )
        assert result_list == [{"variant_id": "123"}]

    async def test_batch_query_calls_abatch_lookup(self) -> None:
        api = MagicMock()
        api.abatch_lookup = MagicMock(
            return_value=_async_gen_from_list(
                [
                    BatchResult(
                        variants=["v1", "v2"],
                        response=[{"id": "1"}, {"id": "2"}],
                    )
                ]
            )
        )

        result = lookup_query(
            api,
            ["v1", "v2"],
            request_parameters=None,
            ref_genome="hg38",
            max_requests=5,
        )

        result_list = [item async for item in result]
        api.abatch_lookup.assert_called_once_with(
            ["v1", "v2"], params=None, ref_genome="hg38", max_requests=5
        )
        assert result_list == [{"id": "1"}, {"id": "2"}]


class TestLookupFromFile:
    """Verify ``lookup_from_file`` reads the file and calls the async API."""

    async def test_batch_lookup(self, tmp_path: Any) -> None:
        f = tmp_path / "vars.txt"
        f.write_text("v1\nv2\n")
        api = MagicMock()
        api.abatch_lookup = MagicMock(
            return_value=_async_gen_from_list(
                [
                    BatchResult(
                        variants=["v1", "v2"],
                        response=[{"id": "1"}, {"id": "2"}],
                    )
                ]
            )
        )

        result = lookup_from_file(
            api,
            str(f),
            request_parameters=None,
            ref_genome="hg19",
            max_requests=5,
        )

        result_list = [item async for item in result]
        assert result_list == [{"id": "1"}, {"id": "2"}]
        api.abatch_lookup.assert_called_once()


class TestBuildAnnotateParser:
    """Verify the annotate_vcf argument parser is configured correctly."""

    def test_requires_api_key_and_input(self) -> None:
        parser = build_annotate_parser()
        with pytest.raises(SystemExit):
            parser.parse_args([])

    def test_requires_input_file(self) -> None:
        parser = build_annotate_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(["-k", "mykey"])

    def test_defaults(self) -> None:
        parser = build_annotate_parser()
        args = parser.parse_args(["-k", "mykey", "-i", "input.vcf"])
        assert args.k == "mykey"
        assert args.i == "input.vcf"
        assert args.g == "hg19"
        assert args.o is None
        assert args.t == 5
        assert args.p == ["add-ACMG-annotation=1"]
        assert args.verbose is False

    def test_all_flags(self) -> None:
        parser = build_annotate_parser()
        args = parser.parse_args(
            [
                "-k",
                "mykey",
                "-i",
                "input.vcf",
                "-o",
                "output.vcf",
                "-g",
                "hg38",
                "-t",
                "10",
                "-p",
                "add-all-data=1",
                "-u",
                "https://staging-api.varsome.com",
                "-v",
            ]
        )
        assert args.k == "mykey"
        assert args.i == "input.vcf"
        assert args.o == "output.vcf"
        assert args.g == "hg38"
        assert args.t == 10
        assert args.p == ["add-all-data=1"]
        assert args.u == "https://staging-api.varsome.com"
        assert args.verbose is True


class TestValidateAnnotateArgs:
    """Verify annotate_vcf argument validation."""

    def test_exits_when_input_file_missing(self) -> None:
        parser = build_annotate_parser()
        args = parser.parse_args(["-k", "mykey", "-i", "/nonexistent/input.vcf"])
        with pytest.raises(SystemExit):
            validate_annotate_args(args)

    def test_exits_when_output_file_exists(self, tmp_path: Any) -> None:
        inp = tmp_path / "input.vcf"
        inp.write_text("##fileformat=VCFv4.1\n")
        out = tmp_path / "output.vcf"
        out.write_text("existing data")
        parser = build_annotate_parser()
        args = parser.parse_args(["-k", "mykey", "-i", str(inp), "-o", str(out)])
        with pytest.raises(SystemExit):
            validate_annotate_args(args)

    def test_passes_with_valid_input_file(self, tmp_path: Any) -> None:
        inp = tmp_path / "input.vcf"
        inp.write_text("##fileformat=VCFv4.1\n")
        parser = build_annotate_parser()
        args = parser.parse_args(["-k", "mykey", "-i", str(inp)])
        validate_annotate_args(args)  # should not raise

    def test_passes_with_valid_input_and_new_output(self, tmp_path: Any) -> None:
        inp = tmp_path / "input.vcf"
        inp.write_text("##fileformat=VCFv4.1\n")
        out = tmp_path / "new_output.vcf"
        parser = build_annotate_parser()
        args = parser.parse_args(["-k", "mykey", "-i", str(inp), "-o", str(out)])
        validate_annotate_args(args)  # should not raise
