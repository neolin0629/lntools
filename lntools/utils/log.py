"""
Logging utility module that provides a customizable Logger class.

@author Neo
@time 2024/6/11
"""
from __future__ import annotations

import logging
import os
import sys
from pathlib import Path
from typing import Union, List, Literal
from rich.logging import RichHandler

# Constants for log formats and datetime format
DATETIME_FORMAT: str = '%Y-%m-%d %H:%M:%S'
FORMAT: str = '[%(asctime)s][%(name)s][%(levelname)s] %(message)s'
RICH_FORMAT: str = '[%(name)s] %(message)s'

LogMethod = Union[str, List[str]]
LogLevel = Literal['debug', 'info', 'warning', 'error', 'critical']
VALID_OUTPUT_METHODS = {'console', 'file'}
LOG_LEVELS = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL
}


class Logger:
    """
    A singleton logger class that generates logs in the specified location.

    Attributes:
        _instances (dict): Storage for singleton instances
        _log (logging.Logger): The underlying logger instance
    """
    _instances: dict = {}

    def __new__(cls, *args, module_name: str = "default", **kwargs) -> Logger:
        """Create or return existing logger instance."""
        if module_name not in cls._instances:
            instance = super(Logger, cls).__new__(cls)
            cls._instances[module_name] = instance
        return cls._instances[module_name]

    def __init__(
        self,
        module_name: str = "default",
        output_method: LogMethod = 'console',
        fmt: str = "",
        rich: bool = True,
        file: Union[str, Path] = "",
        level: LogLevel = 'info'
    ) -> None:
        """
        Initialize the logger with specified configuration.

        Args:
            module_name: Name of the module using the logger
            output_method: Where to output logs ('console' and/or 'file')
            fmt: Custom log format string
            rich: Whether to use rich formatting for console output
            file: Custom log file path
            level: Initial logging level
        """
        if not hasattr(self, '_log'):  # Only initialize if not already done
            if isinstance(output_method, str):
                output_method = [output_method]

            if not set(output_method).issubset(VALID_OUTPUT_METHODS):
                raise ValueError(f"Invalid output method. Must be one of: {VALID_OUTPUT_METHODS}")

            self._log = logging.getLogger(module_name)
            self.setup_logger(output_method, fmt, rich, file)
            self.set_level(level)

    def setup_logger(
        self,
        output_method: List[str],
        fmt: str,
        rich: bool,
        file: Union[str, Path]
    ) -> None:
        """Configure logger with handlers based on output methods."""
        root = Path(os.path.abspath(sys.argv[0])).parent
        default_log_file = root / f"{Path(sys.argv[0]).stem}.log"
        log_file = Path(file) if file else default_log_file

        if 'file' in output_method:
            file_handler = self.create_handler(logging.FileHandler, log_file, FORMAT, DATETIME_FORMAT)
            self._log.addHandler(file_handler)

        if 'console' in output_method:
            console_handler_class = RichHandler if rich else logging.StreamHandler
            console_handler = self.create_handler(
                console_handler_class,
                sys.stdout,
                self.get_format(fmt, rich),
                DATETIME_FORMAT
            )
            self._log.addHandler(console_handler)

    def create_handler(self, handler_class, output, fmt: str, dtfmt: str) -> logging.Handler:
        """Create and configure a log handler."""
        if handler_class is RichHandler:
            handler = handler_class(show_path=False, rich_tracebacks=True)
        elif handler_class is logging.FileHandler:
            handler = handler_class(output, mode='a', encoding='utf-8')
        else:
            handler = handler_class(output)

        handler.setFormatter(logging.Formatter(fmt, dtfmt))
        return handler

    def get_format(self, fmt: str, rich: bool) -> str:
        """Return appropriate log format string."""
        return fmt if fmt else (RICH_FORMAT if rich else FORMAT)

    def set_level(self, level: LogLevel) -> None:
        """Set the logging level."""
        self._log.setLevel(LOG_LEVELS.get(level.lower(), logging.INFO))

    def log(self, level: str, msg: str, *args) -> None:
        """Generic logging method."""
        if hasattr(self._log, level):
            getattr(self._log, level)(msg, *args)

    # Specific logging methods
    def info(self, msg: str, *args) -> None:
        """Log an info message."""
        self.log('info', msg, *args)

    def warning(self, msg: str, *args) -> None:
        """Log a warning message."""
        self.log('warning', msg, *args)

    def error(self, msg: str, *args) -> None:
        """Log an error message."""
        self.log('error', msg, *args)

    def debug(self, msg: str, *args) -> None:
        """Log a debug message."""
        self.log('debug', msg, *args)

    @property
    def help(self) -> str:
        """Return usage instructions."""
        return """
        The properties of `Logger`:

            module_name: str = "default",
            output_method: str | list[str] = 'console' or ['console', 'file'],
            format: str = "",   # the default format is as below
            rich: bool = True,  # whether use rich
            file: str = "",
            level: str = 'info' # logging level

            ---
            DATETIME_FORMAT: str = '%Y-%m-%d %H:%M:%S'
            FORMAT: str = '[%(asctime)s][%(name)s][%(levelname)s] %(message)s'
            RICH_FORMAT: str = '[%(name)s] %(message)s'
            ---

        How to use:

            from lntools.utils import Logger
            log = Logger("xxx", output_method=["console", "file"], file="/xxx/xxx.log")
            log.info("information")
        """
