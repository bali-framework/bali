import asyncio
import logging
from functools import wraps
from importlib import import_module
from typing import Callable

from fastapi import FastAPI

__all__ = ["add_background_tasks", "run_every"]

logger = logging.getLogger('bali')
background_tasks = set()


def add_background_tasks(app: FastAPI, module="tasks"):
    import_module(module)
    on_startup = app.on_event("startup")
    for i in background_tasks:
        logger.info("Find Task %s", i.__name__)
        on_startup(i)


def run_every(seconds: float):
    def decorator(func: Callable):
        @wraps(func)
        def wrapped():
            async def task():
                task_name = func.__name__
                is_coroutine = asyncio.iscoroutinefunction(func)

                while True:
                    logger.info("Start task %s", task_name)
                    try:
                        if is_coroutine:
                            await func()
                        else:
                            loop = asyncio.get_event_loop()
                            await loop.run_in_executor(None, func)
                    except Exception as e:
                        logger.error("Task %s raise an error: %s", task_name, repr(e))
                    else:
                        logger.info("Task %s done", task_name)
                    finally:
                        await asyncio.sleep(seconds)

            asyncio.ensure_future(task())

        background_tasks.add(wrapped)

    return decorator
