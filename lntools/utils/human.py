"""
Human-readable formatting utilities for various data types.

This module provides functions to format different types of data (paths, units, times, lists)
into human-readable strings, primarily for logging and CLI output.

Author: Neo
Date: 2024/6/10
"""
from __future__ import annotations

from collections.abc import Callable, Generator, Iterable, Sequence, Sized

# from contextlib import suppress
from datetime import timedelta
from pathlib import Path
import threading
from typing import TYPE_CHECKING, Any, TypeAlias, TypeVar, cast

from .typing import DatetimeLike

if TYPE_CHECKING:
    from rich.progress import Progress


T = TypeVar('T')
Reporter: TypeAlias = Callable[[str], None]


def path(path_str: str | Path) -> str:
    """
    Convert a path to a human-readable format.

    If the path is relative to the current working directory, 
    returns the relative path. Otherwise returns absolute path.

    Args:
        path_str: The path string or Path object to format

    Returns:
        Formatted path string

    Examples:
        >>> import os
        >>> os.chdir("/home/user")
        >>> path("/home/user/project/file.txt")
        'project/file.txt'
    """
    if not path_str:
        return ""

    try:
        path_obj = Path(path_str).expanduser().resolve()
        cwd = Path.cwd()
        if path_obj.is_relative_to(cwd):
            return str(path_obj.relative_to(cwd))
        return str(path_obj)
    except (ValueError, OSError):
        return str(path_str)


def unit(
    n: int | float,
    unit_name: str,
    decimal: int = 0,
    auto_scale: bool = False
) -> str:
    """
    Format a number with its unit into human-readable text.

    Args:
        n: The quantity
        unit_name: The unit name (e.g. "apple", "byte")
        decimal: Number of decimal places
        auto_scale: If True, scale number to K, M, B, T (e.g. 1000 -> 1K)

    Returns:
        Formatted string (e.g. "1 apple", "2 apples", "1.5K users")

    Examples:
        >>> unit(1, "apple")
        '1 apple'
        >>> unit(10, "apple")
        '10 apples'
        >>> unit(1500, "user", auto_scale=True)
        '1.5K users'
    """
    if decimal < 0:
        raise ValueError("Decimal places cannot be negative")

    val = float(n)
    prefix = ""

    if auto_scale and abs(val) >= 1000:
        for p in ['', 'K', 'M', 'B', 'T']:
            if abs(val) < 1000.0:
                prefix = p
                break
            if p != 'T':  # Don't divide on the last step
                val /= 1000.0
            else:
                prefix = 'T'

        # For scaled numbers, usually 1 decimal is enough unless specified otherwise
        if decimal == 0 and val % 1 != 0:
            decimal = 1

    formatted_number = f"{val:.{decimal}f}"
    # Remove trailing zeros after decimal point if decimal > 0
    if "." in formatted_number:
        formatted_number = formatted_number.rstrip("0").rstrip(".")

    # Handle pluralization
    base_unit = unit_name
    suffix = 's' if (val != 1.0 or prefix) and not base_unit.endswith('s') else ''

    return f"{formatted_number}{prefix} {base_unit}{suffix}"


def bytes_size(n: int | float, decimal: int = 1) -> str:
    """
    Format bytes into human readable size (B, KB, MB, GB, TB).

    Args:
        n: Number of bytes
        decimal: Number of decimal places

    Returns:
        Formatted string (e.g. "1.5 MB")
    """
    n = float(n)
    for unit_name in ['B', 'KB', 'MB', 'GB', 'TB', 'PB']:
        if abs(n) < 1024.0:
            if unit_name == 'B':
                return f"{int(n)} {unit_name}"
            return f"{n:.{decimal}f} {unit_name}"
        n /= 1024.0
    return f"{n:.{decimal}f} EB"


def sec2str(s: float) -> str:
    """
    Convert seconds to human-readable string.

    Args:
        s: Seconds

    Returns:
        String like "1.5s", "2m 30s", "1h 5m"
    """
    if s < 0:
        return f"-{sec2str(-s)}"

    if s < 0.001:  # Microseconds
        return f"{s*1e6:.0f}µs"
    if s < 1:  # Milliseconds
        return f"{s*1e3:.0f}ms"
    if s < 60:
        return f"{s:.2f}s" if s < 10 else f"{s:.1f}s"

    delta = timedelta(seconds=int(s))
    days = delta.days
    seconds = delta.seconds
    hours, remainder = divmod(seconds, 3600)
    minutes, secs = divmod(remainder, 60)

    parts = []
    if days > 0:
        parts.append(unit(days, "day"))
    if hours > 0:
        parts.append(unit(hours, "hr"))
    if minutes > 0:
        parts.append(unit(minutes, "min"))
    # Only show seconds if less than an hour or strictly needed
    if days == 0 and hours == 0 and secs > 0:
        parts.append(f"{secs}s")

    return " ".join(parts[:2])  # Return top 2 significant units


def lists(items: Sequence[Any] | None, n: int = 3, formatter: Callable[[Any], str] = str) -> str:
    """
    Format a list with truncation for preview.

    Args:
        items: The sequence to format
        n: Number of items to show before truncating
        formatter: Function to format each item

    Returns:
        String like "[1, 2, 3] (& 5 others)"
    """
    if items is None:
        return "None"

    # Handle numpy arrays and other non-standard sequences
    if hasattr(items, "tolist"):
        items = items.tolist()  # type: ignore

    # Convert generator/iterator to list if needed
    if not isinstance(items, (list, tuple, str)):
        items = list(items) if isinstance(items, Iterable) else [items]

    length = len(items)  # type: ignore

    if length == 0:
        return "[]"

    if length <= n:
        return f"[{', '.join(formatter(x) for x in items)}]"

    shown_items = ", ".join(formatter(x) for x in items[:n])
    remaining = length - n

    return f"[{shown_items}] (& {unit(remaining, 'other')})"


def ranges(days: Sequence[DatetimeLike], sort: bool = True) -> str:
    """
    Format a date range into human-readable string.

    Args:
        days: Sequence of datetime-like objects
        sort: Whether to sort the input

    Returns:
        String like "2024-01-01 ~ 2024-01-31 (31 days, 1M)"
    """
    if not days:
        return "No dates"

    import pandas as pd
    # Use pd.DatetimeIndex which is often more robust for type checkers with sequences
    try:
        ts_index = pd.to_datetime(pd.Series(days))
    except (ValueError, TypeError):
        return f"{len(days)} items (invalid dates)"

    length = len(ts_index)
    if length == 1:
        return f"{ts_index[0]:%Y-%m-%d} (1 day)"

    if sort:
        ts_index = ts_index.sort_values()

    start, end = ts_index.iloc[0], ts_index.iloc[-1]

    # Calculate duration
    delta = end - start
    duration_days = delta.days + 1  # Inclusive

    # Calculate Year-Month-Day duration
    # This is an approximation since we don't use relativedelta to avoid dependency
    years = duration_days // 365
    remaining_days = duration_days % 365
    months = remaining_days // 30

    duration_str = []
    if years > 0:
        duration_str.append(f"{years}Y")
    if months > 0:
        duration_str.append(f"{months}M")

    # Add precise days only if less than 2 months or exact match
    if years == 0 and months < 2:
        exact_days = duration_days
        duration_str = [f"{exact_days}D"]

    duration_text = "".join(duration_str) if duration_str else f"{duration_days}D"

    return f"{start:%Y-%m-%d} ~ {end:%Y-%m-%d} ({length} days, {duration_text})"


def datetime_str(d: DatetimeLike, method: str = "standard") -> str:
    """
    Format a datetime object to string using a shortcut method.

    Args:
        d: Datetime-like object
        method: 'standard' (YYYY/MM/DD), 'compact' (YYYYMMDD), 'wide' (YYYY-MM-DD),
                or any strftime format string.

    Returns:
        Formatted date string
    """
    from lntools.timeutils import SHORTCUTS, adjust

    try:
        dt = adjust(d)
        fmt = SHORTCUTS.get(method, method)
        return dt.strftime(fmt)  # type: ignore[no-any-return]
    except (ValueError, TypeError):
        return str(d)


def fprint(value: Any) -> None:
    """Print value to stdout with carriage return (overwrite line)."""
    print(value, end="\r", flush=True)


def _track_text(
    items: Iterable[T],
    msg: str,
    total: int | None,
    reporter: Reporter,
    report_every: int = 100,
) -> Generator[T, None, None]:

    last_reported_pct = -1
    for i, item in enumerate(items):
        count = i + 1

        if total:
            curr_pct = int(count * 100 / total)
            if curr_pct > last_reported_pct or count == total:
                reporter(f"{msg}: {count / total:.0%} ({count}/{total})")
                last_reported_pct = curr_pct
        else:
            if count == 1 or (report_every > 0 and count % report_every == 0):
                reporter(f"{msg}: {count} items")

        yield item


# ==========================================
# 1. 极简模式 (基于 tqdm)
# ==========================================

def track_simple(
    sequence: Iterable[T] | int,
    msg: str = "Processing",
    total: int | None = None,
    reporter: Reporter = print,
    report_every: int = 100,
    **tqdm_kwargs: Any,
) -> Generator[T, None, None]:
    items: Iterable[T] = cast(Iterable[T], range(sequence)) if isinstance(sequence, int) else sequence

    if total is None and isinstance(items, Sized):
        total = len(items)

    try:
        from tqdm import tqdm
        with tqdm(
            items,
            desc=msg,
            total=total,
            leave=True,
            dynamic_ncols=True,
            **tqdm_kwargs,
        ) as t:
            yield from t
        return
    except ImportError:
        # 没 tqdm -> text fallback（有节流）
        yield from _track_text(items, msg=msg, total=total, reporter=reporter, report_every=report_every)


# ==========================================
# 2. 增强模式 (基于 rich，支持多进度条)
# ==========================================

class RichProgressManager:
    """Rich-based progress manager supporting multiple concurrent tasks."""

    def __init__(
        self,
        transient: bool = False,
        reporter: Reporter = print,
        report_every: int = 100,
        remove_task_on_finish: bool = False,
    ):
        self.progress: Progress | None = None
        self.transient = transient
        self.reporter = reporter
        self.report_every = report_every
        self.remove_task_on_finish = remove_task_on_finish
        self._lock = threading.Lock()

    def __enter__(self) -> RichProgressManager:
        try:
            from rich.progress import (
                BarColumn,
                Progress,
                SpinnerColumn,
                TextColumn,
                TimeRemainingColumn,
            )

            self.progress = Progress(
                SpinnerColumn(),
                TextColumn("[bold blue]{task.description}", justify="right"),
                BarColumn(bar_width=None),
                "[progress.percentage]{task.percentage:>3.0f}%",
                "•",
                TimeRemainingColumn(),
                transient=self.transient,
            )
            self.progress.start()
            return self
        except ImportError:
            self.progress = None
            self.reporter("Warning: rich is not installed, RichProgressManager will fallback to text progress.")
            return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any | None,
    ) -> None:
        if self.progress:
            self.progress.stop()

    def track(
        self,
        sequence: Iterable[T] | int,
        msg: str = "Working",
        total: int | None = None,
    ) -> Generator[T, None, None]:
        items: Iterable[T] = cast(Iterable[T], range(sequence)) if isinstance(sequence, int) else sequence
        if total is None and isinstance(items, Sized):
            total = len(items)

        # rich 不可用 -> text fallback（有节流）
        if self.progress is None:
            yield from _track_text(
                items,
                msg=msg,
                total=total,
                reporter=self.reporter,
                report_every=self.report_every,
            )
            return

        # rich 可用：同屏多任务
        with self._lock:
            task_id = self.progress.add_task(msg, total=total)

        try:
            for item in items:
                yield item
                # 多线程场景下，update/advance 也加锁，避免竞态
                with self._lock:
                    self.progress.advance(task_id, 1)
        finally:
            # 可选：任务结束后收敛 UI，避免堆积
            if self.remove_task_on_finish:
                with self._lock:
                    self.progress.remove_task(task_id)
            else:
                # 如果 total 可得，确保最终完成态
                if total is not None:
                    with self._lock:
                        self.progress.update(task_id, completed=total)
