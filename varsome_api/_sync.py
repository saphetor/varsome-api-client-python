import asyncio
import functools
from collections.abc import Callable, Coroutine
from concurrent.futures import ThreadPoolExecutor
from typing import Any, TypeVar

T = TypeVar("T")

_SYNC_EXECUTOR = ThreadPoolExecutor(max_workers=4)


def run_sync(coro: Coroutine[Any, Any, T]) -> T:
    """Run an async coroutine from synchronous code and return its result.

    Args:
        coro: The coroutine to execute.

    Returns:
        The value returned by the coroutine.

    Raises:
        Any exception raised inside the coroutine is re-raised.
    """
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)

    future = _SYNC_EXECUTOR.submit(asyncio.run, coro)
    return future.result()


def sync_wrapper(async_fn: Callable[..., Coroutine[Any, Any, T]]) -> Callable[..., T]:
    """Return a synchronous function that calls *async_fn* via :func:`run_sync`.

    Useful as a decorator or factory for building sync counterparts of
    async methods::

        class Client:
            async def alookup(self, query: str) -> dict: ...
            lookup = sync_wrapper(alookup)

    Args:
        async_fn: The async function or unbound method to wrap.

    Returns:
        A synchronous wrapper that forwards all arguments to *async_fn*.
    """

    @functools.wraps(async_fn)
    def wrapper(*args: Any, **kwargs: Any) -> T:
        return run_sync(async_fn(*args, **kwargs))

    return wrapper
