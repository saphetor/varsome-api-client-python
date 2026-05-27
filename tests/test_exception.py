import pytest

from varsome_api.exceptions import VarSomeAPIException


class TestVarSomeAPIException:
    """Verify the custom API exception behaviour."""

    @pytest.mark.parametrize(
        ("status", "response", "expected_fragments"),
        [
            (400, "Bad input", ["400", "Bad input"]),
            (500, None, ["500", "Internal Server Error"]),
            (None, "Connection refused", ["Connection refused"]),
            (None, None, ["Unknown error"]),
        ],
        ids=["status_and_response", "status_only", "none_status", "no_info"],
    )
    def test_str_representation(
        self,
        status: int | None,
        response: str | None,
        expected_fragments: list[str],
    ) -> None:
        exc = VarSomeAPIException(status, response)
        for fragment in expected_fragments:
            assert fragment in str(exc)

    def test_repr(self) -> None:
        exc = VarSomeAPIException(404)
        assert repr(exc) == "VarSomeAPIException(status=404)"
