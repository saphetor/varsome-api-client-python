import asyncio

import pytest

from varsome_api._sync import run_sync, sync_wrapper


class TestRunSync:
    """Verify that ``run_sync`` correctly executes coroutines."""

    def test_returns_coroutine_result(self) -> None:
        """A simple coroutine result should be returned to the caller."""

        async def greet() -> str:
            return "hello"

        assert run_sync(greet()) == "hello"

    def test_propagates_exceptions(self) -> None:
        """Exceptions raised inside the coroutine must propagate."""

        async def boom() -> None:
            raise ValueError("kaboom")

        with pytest.raises(ValueError, match="kaboom"):
            run_sync(boom())

    def test_works_with_await_chains(self) -> None:
        """Coroutines that await other coroutines should work transparently."""

        async def add(a: int, b: int) -> int:
            await asyncio.sleep(0)
            return a + b

        async def pipeline() -> int:
            x = await add(1, 2)
            y = await add(x, 3)
            return y

        assert run_sync(pipeline()) == 6

    async def test_fallback_when_loop_is_running(self) -> None:
        """When called from within a running loop, must still work via thread fallback."""

        async def inner() -> int:
            return 42

        assert run_sync(inner()) == 42


class TestSyncWrapper:
    """Verify that ``sync_wrapper`` produces a working synchronous wrapper."""

    def test_wraps_coroutine_function(self) -> None:
        async def afetch(url: str) -> str:
            return f"response from {url}"

        fetch = sync_wrapper(afetch)
        assert fetch("https://example.com") == "response from https://example.com"

    def test_preserves_function_name(self) -> None:
        async def afetch(url: str) -> str:
            return url

        fetch = sync_wrapper(afetch)
        assert fetch.__name__ == "afetch"
        assert fetch.__wrapped__ is afetch  # type: ignore[attr-defined]

    def test_propagates_exceptions(self) -> None:
        async def fail() -> None:
            raise RuntimeError("oops")

        sync_fail = sync_wrapper(fail)
        with pytest.raises(RuntimeError, match="oops"):
            sync_fail()

    def test_works_as_unbound_method(self) -> None:
        """sync_wrapper(async_method) works correctly when assigned as a class attr."""

        class Greeter:
            async def agreet(self, name: str) -> str:
                return f"hi {name}"

            greet = sync_wrapper(agreet)

        g = Greeter()
        assert g.greet("world") == "hi world"
