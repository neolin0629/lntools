"""
Frequently-Used Utility Decorators
@author: Neo
@date: 2024/6/9
"""
import time
from typing import Callable, Any


def timer(
    msg: str,
    reporter: Callable = print,
    threshold: int = 3,
    process_time: bool = False,
) -> Callable:
    """
    Decorator for reporting the process time of a function.
    Reports the time if it exceeds a given threshold.

    Args
    ----------
    msg : str
        The message to prefix the reported time with.
    reporter : Callable, optional
        The function to report the message with, defaults to `print`.
    threshold : int, optional
        The minimum time (in seconds) required to report the execution time,
        defaults to 3 seconds.
    process_time : bool, optional
        If True, use `time.process_time()` to measure CPU process time,
        otherwise `time.perf_counter()` for wall-clock time.
    """
    timer_func = time.process_time if process_time else time.perf_counter

    def decorator(func: Callable) -> Callable:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = timer_func()
            result = func(*args, **kwargs)
            elapsed_time = timer_func() - start_time
            if elapsed_time > threshold:
                from lntools.utils.human import sec2str

                reporter(f"{msg}: {sec2str(elapsed_time)}")
            return result

        return wrapper

    return decorator
