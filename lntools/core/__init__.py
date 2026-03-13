"""Core utilities for lntools.

This module provides fundamental utilities for:
- Filesystem operations
- Logging
- Command-line interface
"""

from .cli import CLI, CLIError
from .filesystem import (
    READERS,
    file_time,
    get_all,
    get_dirs,
    get_files,
    handle_path,
    is_dir,
    is_file,
    list_paths,
    load_data,
    make_dirs,
    move,
    read_directory,
    read_file,
    remove,
    rename,
)
from .log import (
    LOG_LEVELS,
    VALID_OUTPUT_METHODS,
    LogConfig,
    Logger,
    LogLevel,
    LogMethod,
)

__all__ = [
    # CLI
    "CLI",
    "CLIError",
    # Filesystem
    "READERS",
    "file_time",
    "get_all",
    "get_dirs",
    "get_files",
    "handle_path",
    "is_dir",
    "is_file",
    "list_paths",
    "load_data",
    "make_dirs",
    "move",
    "read_directory",
    "read_file",
    "remove",
    "rename",
    # Log
    "LOG_LEVELS",
    "VALID_OUTPUT_METHODS",
    "LogConfig",
    "LogLevel",
    "LogMethod",
    "Logger",
]
