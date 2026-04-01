"""lntools - Development Assistance Tools."""

# ==========================================
# Submodules
# ==========================================
from . import bot, config, core, format, mail, timeutils, types

# ==========================================
# Core utilities (from core module)
# ==========================================
from .core import (
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

# ==========================================
# Formatting utilities (from format module)
# ==========================================
from .format import (
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

# ==========================================
# Type definitions (from types module)
# ==========================================
from .types import (
    ArrayLike,
    DataFrameLike,
    DatetimeLike,
    PathLike,
    SeriesLike,
)

# ==========================================
# Exports
# ==========================================
__all__ = [
    # Submodules
    "bot",
    "config",
    "core",
    "format",
    "mail",
    "timeutils",
    "types",
    # Core - CLI
    "CLI",
    "CLIError",
    # Core - Filesystem
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
    # Core - Log
    "Logger",
    "LogConfig",
    # Format
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
