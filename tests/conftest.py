from collections.abc import Callable
from typing import Any

import pytest

from varsome_api.client import VarSomeAPIClient


@pytest.fixture()
def api_client() -> VarSomeAPIClient:
    """A ``VarSomeAPIClient`` pre-configured with a test API key."""
    return VarSomeAPIClient(api_key="test")


@pytest.fixture()
def make_fake_request() -> Callable[
    [Callable[[list[str]], list[dict[str, Any]]]],
    Callable[..., Any],
]:
    """Factory that builds an async ``_make_request`` replacement.

    Call with a *response_builder* — a function that receives the
    variant list extracted from the POST JSON body and returns the
    mock API response list.

    Example::

        fake = make_fake_request(lambda batch: [{"id": v} for v in batch])
    """

    def _factory(
        response_builder: Callable[[list[str]], list[dict[str, Any]]],
    ) -> Callable[..., Any]:
        async def _fake(
            _session: Any,
            *,
            path: str,
            method: str = "GET",
            **kwargs: Any,
        ) -> list[dict[str, Any]]:
            batch = kwargs.get("json", {}).get("variants", [])
            return response_builder(batch)

        return _fake

    return _factory
