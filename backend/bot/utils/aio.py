import asyncio
from collections.abc import Callable, Coroutine
from typing import Any

from bot.loader import logger, loop


async def asyncio_wait(
    fs,
    *,
    timeout=None,
    return_when=asyncio.ALL_COMPLETED,
) -> tuple[set, set]:
    if not fs:
        return set(), set()
    return await asyncio.wait(fs, timeout=timeout, return_when=return_when)


async def run_loop_task(
    func: Callable[[], Coroutine[Any, Any, None]],
    *,
    timeout: int = 300,
):
    try:
        await func()
        await asyncio.sleep(timeout)
    except Exception as e:
        logger.exception(f'Error in {func.__name__}', exc_info=e)
        await asyncio.sleep(timeout)
    finally:
        loop.create_task(run_loop_task(func, timeout=timeout))
