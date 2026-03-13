"""Utils module - Deprecated, use core, format, types instead.

This module is kept for backward compatibility.
Please migrate to the new module structure:
- lntools.core - Core utilities (filesystem, log, cli)
- lntools.format - Formatting utilities (human)
- lntools.types - Type definitions (typing)
"""

import warnings

# Import from new locations for backward compatibility
from lntools.core import (
    CLI,
    CLIError,
    LogConfig,
    Logger,
    file_time,
    get_all,
    get_dirs,
    get_files,
    handle_path,
    is_dir,
    is_file,
    list_paths,
    make_dirs,
    move,
    read_directory,
    read_file,
    remove,
    rename,
)
from lntools.format import (
    RichProgressManager,
    datetime_str,
    fprint,
    lists,
    path,
    ranges,
    sec2str,
    track_simple,
    unit,
)
from lntools.types import (
    ArrayLike,
    DataFrameLike,
    DatetimeLike,
    PathLike,
    SeriesLike,
)

__all__ = [
    # CLI
    "CLI",
    "CLIError",
    # Filesystem
    "is_dir",
    "is_file",
    "handle_path",
    "make_dirs",
    "move",
    "rename",
    "remove",
    "file_time",
    "list_paths",
    "get_all",
    "get_files",
    "get_dirs",
    "read_file",
    "read_directory",
    # Log
    "Logger",
    "LogConfig",
    # Human format
    "path",
    "unit",
    "sec2str",
    "lists",
    "ranges",
    "datetime_str",
    "fprint",
    "track_simple",
    "RichProgressManager",
    # Types
    "ArrayLike",
    "SeriesLike",
    "DataFrameLike",
    "DatetimeLike",
    "PathLike",
]

# Deprecation warning
warnings.warn(
    "lntools.utils is deprecated. Use lntools.core, lntools.format, or lntools.types instead.",
    DeprecationWarning,
    stacklevel=2,
)
