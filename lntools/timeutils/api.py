from collections.abc import Callable
from datetime import datetime
import functools
import time
from typing import Literal, ParamSpec, TypeVar

import pandas as pd
import polars as pl

from lntools.utils.typing import DatetimeLike

# ==========================================
# 类型定义与常量
# ==========================================
P = ParamSpec("P")
R = TypeVar("R")

DATE_STR_PATTERN: str = r"\d{4}(0[1-9]|1[0-2])(0[1-9]|[1-2][0-9]|3[0-1])"

FormatMethod = Literal["standard", "compact", "wide", "time", "datetime"]

SHORTCUTS: dict[str, str] = {
    "standard": "%Y/%m/%d",
    "compact": "%Y%m%d",
    "wide": "%Y-%m-%d",
    "time": "%H:%M:%S",
    "datetime": "%Y/%m/%d %H:%M:%S",
}


# ==========================================
# 装饰器
# ==========================================


def timer(
    msg: str,
    reporter: Callable[[str], None] = print,
    threshold: float = 3.0,
    process_time: bool = False,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    Performance analysis decorator to measure execution time.

    Args:
        msg: Message prefix for the report.
        reporter: Function to handle the output (defaults to print).
        threshold: Minimum seconds to trigger reporting.
        process_time: Use CPU process time if True, else wall-clock time.
    """
    timer_func = time.process_time if process_time else time.perf_counter

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            start_time = timer_func()
            result = func(*args, **kwargs)
            elapsed = timer_func() - start_time

            if elapsed >= threshold:
                time_str = f"{elapsed:.2f}s" if elapsed < 60 else f"{elapsed / 60:.2f}min"
                reporter(f"[{msg}] 耗时: {time_str}")
            return result

        return wrapper

    return decorator


# ==========================================
# 核心转换函数 (Internal)
# ==========================================


def to_timestamp(t: DatetimeLike, date_only: bool = False) -> pd.Timestamp:
    """
    Convert any date-like input to a pandas.Timestamp object.

    Args:
        t: Input date (Timestamp, datetime, string, or number).
        date_only: If True, normalize to midnight.

    Returns:
        pd.Timestamp: The parsed timestamp object.
    """
    if isinstance(t, str) and t.lower() == "today":
        ts = pd.Timestamp.now()
    else:
        try:
            if isinstance(t, int) and t > 19000101:
                # Assume YYYYMMDD format for large integers
                ts = pd.to_datetime(str(t), format="%Y%m%d")
            else:
                # Let pandas handle str, float (epoch), datetime, etc.
                ts = pd.to_datetime(t)
        except Exception as e:
            raise ValueError(f"Invalid datetime format: {t}") from e

    return ts.normalize() if date_only else ts


# ==========================================
# 工具函数
# ==========================================


def day_of_week(dt: DatetimeLike = "today") -> int:
    """
    Get the day of the week for a given date.

    Returns:
        int: 1 for Monday, 7 for Sunday.
    """
    # Pandas 的 dayofweek 范围是 0-6 (周一至周日)
    return int(to_timestamp(dt).dayofweek + 1)


def adjust(date: DatetimeLike, n: int = 0, date_only: bool = False) -> pd.Timestamp:
    """
    Adjust a date by adding or subtracting a number of days.

    Args:
        date: Base date to adjust.
        n: Number of days to shift.
        date_only: Whether to strip the time component.
    """
    ts = to_timestamp(date, date_only=date_only)
    return ts if n == 0 else ts + pd.Timedelta(days=n)


def diff(start_date: DatetimeLike, end_date: DatetimeLike) -> int:
    """
    Calculate the total number of days between two dates.
    """
    s = to_timestamp(start_date, date_only=True)
    e = to_timestamp(end_date, date_only=True)
    return int((e - s).days)


def get_range(
    start_date: DatetimeLike | None = None, end_date: DatetimeLike | None = None
) -> list[pd.Timestamp]:
    """
    Generate a list of daily timestamps within a specified range.

    Args:
        start_date: Defaults to "2010-01-01".
        end_date: Defaults to current date.
    """
    start = to_timestamp(start_date if start_date else "2010-01-01", date_only=True)
    end = to_timestamp(end_date if end_date else "today", date_only=True)

    if start > end:
        raise ValueError(f"Start date {start} cannot be later than end date {end}")

    return pd.date_range(start, end, freq="D").tolist()  # type: ignore[no-any-return]


def dt2str(d: datetime | pd.Timestamp, method: FormatMethod | str = "wide") -> str:
    """Convert a datetime/timestamp object to a formatted string."""
    fmt = SHORTCUTS.get(method, method)
    return d.strftime(fmt)


def ts2str(t: int | float, method: FormatMethod | str = "wide") -> str:
    """Convert a Unix epoch timestamp to a formatted string."""
    dt = datetime.fromtimestamp(float(t))
    return dt2str(dt, method)


def is_date_pl(data: pl.DataFrame | pl.LazyFrame | pl.Series, col_name: str = "dt") -> bool:
    """Check if a Polars Series or DataFrame column is a temporal type."""
    if isinstance(data, pl.Series):
        return data.dtype.is_temporal()

    if col_name not in data.schema:
        return False

    return bool(data.schema[col_name].is_temporal())


def is_date_pd(series: pd.Series) -> bool:
    """Check if a Pandas Series is a datetime type."""
    return bool(pd.api.types.is_datetime64_any_dtype(series))
