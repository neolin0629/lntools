"""
Human-readable formatting utilities for various data types.

This module provides functions to format different types of data (paths, units, times, etc.)
into human-readable strings.

Author: Neo
Date: 2024/6/10
"""
from __future__ import annotations

from datetime import timedelta
from pathlib import Path
from typing import Any, Callable, Iterable, List, Union, TypeVar

import pandas as pd

T = TypeVar('T')


def path(path_str: str) -> str:
    """Convert a path to a human-readable format.

    Parameters
    ----------
    path_str : str
        The path string to format

    Returns
    -------
    str
        Formatted path relative to current directory if possible,
        otherwise absolute path

    Raises
    ------
    ValueError
        If path string is empty
    """
    if not path_str:
        raise ValueError("Path cannot be empty")

    path_obj = Path(path_str).expanduser().resolve()
    try:
        if path_obj.is_relative_to(Path.cwd()):
            return str(path_obj.relative_to(Path.cwd()))
    except ValueError:
        pass
    return str(path_obj)


def unit(n: Union[int, float], unit_name: str, decimal: int = 0) -> str:
    """Format a number with its unit into human-readable text.

    Parameters
    ----------
    n : Union[int, float]
        The quantity
    unit_name : str
        The unit name
    decimal : int, optional
        Number of decimal places, by default 0

    Returns
    -------
    str
        Formatted string with proper pluralization

    Examples
    --------
    >>> unit(1, "apple")
    '1 apple'
    >>> unit(3.141, "meter", decimal=2)
    '3.14 meters'
    """
    if decimal < 0:
        raise ValueError("Decimal places cannot be negative")
    if not unit_name:
        raise ValueError("Unit name cannot be empty")

    formatted_number = f"{float(n):.{decimal}f}"
    plural = 's' if float(n) != 1 and not unit_name.endswith('s') else ''
    return f"{formatted_number} {unit_name}{plural}"


def sec2str(s: float) -> str:
    """Human-Readable Seconds Time

    Args
    ----------
    s : float
        Seconds.

    Returns
    -------
    str
        Human-readable seconds.

    Examples
    -------
    sec2str(3.1415926) -> 3.1416s
    sec2str(13.324) -> 13.3s
    sec2str(1024) -> 17 mins 4 s
    sec2str(9999) -> 2 hours 46 mins
    """
    delta = timedelta(seconds=s)
    if delta < timedelta(minutes=1):
        return f"{s:.4f}s" if s < 10 else f"{s:.1f}s"
    if delta < timedelta(hours=1):
        mins, secs = divmod(s, 60)
        return f"{unit(int(mins), 'min')} {int(secs)} s"
    hours, remainder = divmod(s, 3600)
    mins, _ = divmod(remainder, 60)
    return f"{unit(int(hours), 'hours')} {unit(int(mins), 'min')}"


def lists(items: List[Any], n: int = 3) -> str:
    """Human-Readable List ([a, b, c] (& n others))

    Args
    ----------
    items : list
        Given list to preview
    n : int, optional
        How many elements to preview, by default 3

    Returns
    -------
    str
        Human-Readable list
    """
    length: int = len(items)
    if length == 1:
        return f"{items} (only 1)"
    if length <= n:
        return f"{items}"
    return f"{items[:n]} (& {unit(length-n, 'other')})"


def ranges(days: list[pd.Timestamp], sort: bool = True) -> str:
    """Human-Readable Dates Range

    Args
    ----------
    days : list[pd.Timestamp]
        Given dates range
    sort : bool, optional
        Sort given list or not, by default True

    Returns
    -------
    str
        Human-Readable dates range
        "begin ~ end (N days given, calendar range)"

    example
    -------
        "2021/01/01 ~ 2021/09/18 (261 days, 8M18D)"
    """
    try:
        from dateutil.relativedelta import relativedelta
    except ModuleNotFoundError:
        from lntools.utils.misc import missing_dependency
        missing_dependency("python-dateutil")

    from lntools.timeutils import dt2str

    def get_ymd(delta: relativedelta) -> str:
        "Return How Many Years, Months & Days Message"
        result: str = f"{delta.days+1}D"
        if delta.months != 0:
            result = f"{delta.months}M" + result
        if delta.years != 0:
            result = f"{delta.years}Y" + result
        return result

    length: int = len(days)
    if length == 0:
        return "No days given"
    if length == 1:
        return f"{dt2str(days[0]), 'standard'} (only 1 day)"
    if sort:
        days.sort()
    begin, end = days[0], days[-1]
    ymd: str = get_ymd(relativedelta(end, begin))
    return f"{dt2str(begin, 'standard')} ~ {dt2str(end, 'standard')} ({length} days, {ymd})"


def datetime(d, method: str = "standard") -> str:
    """Return Human-Readable Date

    Parameters
    ----------
    d : DatetimeLike
        Given Date
    method : str, optional
        Format method, by default "standard"
        If not recognizable method shortcut, pass as format string itself

    Returns
    -------
    str
        Human-Readable Date
    """
    from lntools.timeutils import adjust, SHORTCUTS
    format_: str = SHORTCUTS.get(method, method)
    return adjust(d).strftime(format_)


def fprint(value) -> None:
    print(value, end="\r", flush=True)


def track(
    sequence: Iterable[T],
    msg: str,
    rich: bool = True,
    reporter: Callable[[str], None] = fprint,
) -> Iterable[T]:
    """Track progress of iteration over a sequence.

    Parameters
    ----------
    sequence : Iterable[T]
        The sequence to iterate over
    msg : str
        Progress message prefix
    rich : bool, optional
        Whether to use rich progress bars, by default True
    reporter : Callable[[str], None], optional
        Progress reporting function, by default prints with carriage return

    Returns
    -------
    Iterable[T]
        Generator yielding items from the sequence

    Notes
    -----
    Falls back to simple progress tracking if rich is not installed
    """
    if not msg:
        msg = "Progress"

    if rich:
        try:
            from rich.progress import track as rich_track
            yield from rich_track(sequence, description=msg)
            return
        except ModuleNotFoundError:
            pass

    yield from _track_without_rich(sequence, msg, reporter)


def _track_without_rich(sequence: Iterable[T], msg: str, reporter: Callable) -> Iterable[T]:
    total = len(sequence)  # type: ignore
    for i, item in enumerate(sequence):
        reporter(f"{msg} {(i+1) / total:.1%}")
        yield item
