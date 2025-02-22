"""Time utility functions for datetime handling and conversion.

This module provides a collection of functions for:
- DateTime conversion between different formats
- Date calculations and adjustments
- Type checking for datetime columns
- Timestamp operations

@author Neo
@time 2024/6/8
"""
from datetime import datetime, timedelta
from typing import List, Union, Optional, Literal

import pandas as pd
import polars as pl
from pandas.api.types import is_datetime64_any_dtype as is_date_pd  # pylint: disable=unused-import # noqa: F401

from lntools.utils.decorator import timer  # pylint: disable=unused-import # noqa: F401
from lntools.utils.typing import DatetimeLike

# Constants
DATE_STR_PATTERN: str = r'\d{4}(0[1-9]|1[0-2])(0[1-9]|[1-2][0-9]|3[0-1])'

SHORTCUTS: dict[str, str] = {
    "standard": '%Y/%m/%d',
    "compact": '%Y%m%d',
    "wide": '%Y-%m-%d',
    "time": '%H:%M:%S',
    "datetime": '%Y/%m/%d %H:%M:%S',
}

FormatMethod = Literal["standard", "compact", "wide", "time", "datetime"]


def now() -> datetime:
    """Return current datetime with timezone information."""
    return datetime.now()


def day_of_week(dt: DatetimeLike = "today") -> int:
    """Return the day of the week for a given date (Monday=1, Sunday=7).

    Args:
        dt: Date-like input. Defaults to "today".
            Supported formats:
            - datetime object
            - pandas Timestamp
            - string in format YYYYMMDD
            - integer in format YYYYMMDD
            - "today" literal

    Returns:
        int: Day of week (1=Monday through 7=Sunday)

    Examples:
        >>> day_of_week("today")
        >>> day_of_week(datetime.now())
        >>> day_of_week(20211201)
        >>> day_of_week("20211201")
    """
    return adjust(dt).day_of_week + 1


def _any2pdt(t: DatetimeLike, date_only: bool = False) -> pd.Timestamp:
    """Convert any date-like object to pandas Timestamp.

    Args:
        t: Value to be converted to Timestamp
        date_only: If True, removes time component. Defaults to False.

    Returns:
        pd.Timestamp: Parsed datetime

    Raises:
        ValueError: If input format is not recognized
    """
    try:
        if isinstance(t, str) and t.lower() == "today":
            t = datetime.now()
        if not isinstance(t, pd.Timestamp):
            t = pd.Timestamp(str(t))
        return t.normalize() if date_only else t
    except (ValueError, TypeError) as e:
        raise ValueError(f"Invalid datetime format: {t}") from e


def adjust(date: DatetimeLike, n: int = 0, date_only: bool = False) -> pd.Timestamp:
    """Adjust date by adding/subtracting days.

    Args:
        date: Base date to adjust
        n: Number of days to adjust by (positive=forward, negative=backward)
        date_only: If True, removes time component. Defaults to False.

    Returns:
        pd.Timestamp: Adjusted datetime

    Examples:
        >>> adjust("2024-01-01", 1)  # Next day
        >>> adjust("2024-01-01", -1)  # Previous day
        >>> adjust("today")  # Today
    """
    date = _any2pdt(date, date_only=date_only)
    return date if n == 0 else date + pd.Timedelta(days=n)


def diff(start_date: DatetimeLike, end_date: DatetimeLike) -> int:
    """Calculate number of days between two dates.

    Args:
        start_date: Starting date
        end_date: Ending date

    Returns:
        int: Number of days between dates

    Examples:
        >>> diff("2024-01-01", "2024-02-01")  # 31
    """
    return (adjust(end_date, date_only=True) - adjust(start_date, date_only=True)).days


def get(start_date: Optional[DatetimeLike] = None,
        end_date: Optional[DatetimeLike] = None) -> List[pd.Timestamp]:
    """Generate a list of dates within range (inclusive).

    Args:
        start_date: Starting date. Defaults to "2010-01-01"
        end_date: Ending date. Defaults to today

    Returns:
        List[pd.Timestamp]: List of dates

    Raises:
        ValueError: If start_date is after end_date
    """
    start = adjust(start_date if start_date else "2010-01-01")
    end = adjust(end_date if end_date else "today")

    if start > end:
        raise ValueError(f"Start date {start} cannot be after end date {end}")

    return [start + timedelta(days=i) for i in range((end - start).days + 1)]


def str2dt(s: str) -> pd.Timestamp:
    """Convert a string to a pandas Timestamp.

    Args:
        s: Date string to convert

    Returns:
        pd.Timestamp: Converted timestamp

    Examples:
        >>> str2dt("2024-01-01")
        >>> str2dt("20240101")
    """
    return adjust(s)


def str2ts(s: str) -> float:
    """Convert a datetime-like string to a POSIX timestamp.

    Args:
        s: Date string to convert

    Returns:
        float: POSIX timestamp

    Examples:
        >>> str2ts("2024-01-01")
        1704067200.0
    """
    return adjust(s).timestamp()


def ts2dt(t: Union[int, float]) -> datetime:
    """Convert a POSIX timestamp to a datetime.

    Args:
        t: POSIX timestamp

    Returns:
        datetime: Converted datetime object

    Examples:
        >>> ts2dt(1704067200)
        datetime(2024, 1, 1, 0, 0)
    """
    return datetime.fromtimestamp(float(t))


def ts2str(t: Union[int, float], method: Union[FormatMethod, str] = "wide") -> str:
    """Convert a POSIX timestamp to a formatted string.

    Args:
        t: POSIX timestamp
        method: Format method or custom format string. Defaults to "wide"

    Returns:
        str: Formatted date string

    Examples:
        >>> ts2str(1704067200, "wide")
        '2024-01-01'
    """
    return dt2str(ts2dt(t), method)


def dt2ts(d: Union[datetime, pd.Timestamp]) -> float:
    """Convert a datetime to a POSIX timestamp.

    Args:
        d: Datetime object to convert

    Returns:
        float: POSIX timestamp

    Examples:
        >>> dt2ts(datetime(2024, 1, 1))
        1704067200.0
    """
    return d.timestamp()


def dt2str(d: datetime, method: Union[FormatMethod, str] = "wide") -> str:
    """Convert datetime to formatted string.

    Args:
        d: Datetime to convert
        method: Format method or custom format string. Defaults to "wide"

    Returns:
        str: Formatted date string
    """
    format_str = SHORTCUTS.get(method, method)
    return d.strftime(format_str)


def is_date_pl(data: Union[pl.DataFrame, pl.LazyFrame, pl.Series],
               col_name: str = "tdate") -> bool:
    """Check if polars object has date/datetime type.

    Args:
        data: Polars DataFrame, LazyFrame or Series
        col_name: Column name to check. Defaults to "tdate"

    Returns:
        bool: True if column is date/datetime type
    """
    if isinstance(data, pl.Series):
        return data.dtype in (pl.Date, pl.Datetime)

    return (col_name in data.schema and
            data.schema[col_name] in (pl.Date, pl.Datetime))
