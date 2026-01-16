from __future__ import annotations

from contextlib import suppress
from dataclasses import dataclass
import logging
import os
from pathlib import Path
import sys
from typing import Any, Literal

from rich.logging import RichHandler

# Type Aliases
LogMethod = str | list[str]
LogLevel = Literal['debug', 'info', 'warning', 'error', 'critical']

# Constants
VALID_OUTPUT_METHODS = frozenset({'console', 'file'})
LOG_LEVELS: dict[str, int] = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL
}


@dataclass
class LogConfig:
    """
    Configuration class for Logger.
    Allows customization of default logging behavior.

    Attributes:
        datetime_format: DateTime format string for log timestamps
        file_format: Format string for file output
        console_format: Format string for console output (when rich=False)
        rich_format: Format string for rich console output (when rich=True)
        default_level: Default logging level
        default_output_method: Default output method(s)
        default_rich: Whether to use rich formatting by default
        default_log_dir: Default directory for log files (None=script dir)
    """
    datetime_format: str = '%Y-%m-%d %H:%M:%S'
    file_format: str = '[%(asctime)s][%(name)s][%(levelname)s] %(message)s'
    console_format: str = '[%(asctime)s][%(name)s][%(levelname)s] %(message)s'
    rich_format: str = '[%(name)s] %(message)s'
    default_level: LogLevel = 'info'
    default_output_method: LogMethod = 'console'
    default_rich: bool = True
    default_log_dir: Path | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert config to dictionary."""
        return {
            'datetime_format': self.datetime_format,
            'file_format': self.file_format,
            'console_format': self.console_format,
            'rich_format': self.rich_format,
            'default_level': self.default_level,
            'default_output_method': self.default_output_method,
            'default_rich': self.default_rich,
            'default_log_dir': str(self.default_log_dir) if self.default_log_dir else None
        }


class Logger:
    """
    A singleton logger class with configurable output and formatting.

    Features:
    - Singleton pattern per module_name (each module has its own logger instance)
    - Configurable output methods (console/file or both)
    - Rich console formatting support
    - Thread-safe handler management
    - Runtime level adjustment

    Time Complexity: O(1) for logging operations
    Space Complexity: O(n) where n = number of unique module_name instances

    Attributes:
        _instances: Storage for singleton instances per module_name
        _log: The underlying Python logging.Logger instance
        _handlers: Registry of handlers added to this logger
        config: LogConfig instance for this logger
    """
    _instances: dict[str, Logger] = {}
    _initialized: dict[str, bool] = {}  # Track initialization status

    def __new__(cls, *args: Any, **kwargs: Any) -> Logger:
        # 1. 从 kwargs 或 args 中提取 module_name
        # 如果调用者没传，则取默认值 "default"
        module_name = kwargs.get("module_name")
        module_name = (
            args[0]
            if module_name is None and len(args) > 0
            else (module_name or "default")
        )

        if module_name not in cls._instances:
            instance = super().__new__(cls)
            cls._instances[module_name] = instance
            cls._initialized[module_name] = False

        return cls._instances[module_name]

    def __init__(
        self,
        module_name: str = "default",
        output_method: LogMethod | None = None,
        fmt: str = "",
        rich: bool | None = None,
        file: str | Path = "",
        level: LogLevel | None = None,
        config: LogConfig | None = None
    ) -> None:
        """
        Initialize the logger with specified configuration.

        Args:
            module_name: Name of the module using the logger
            output_method: Where to output logs ('console'/'file' or both).
                          If None, uses config.default_output_method
            fmt: Custom log format string (overrides config formats)
            rich: Whether to use rich formatting for console.
                  If None, uses config.default_rich
            file: Custom log file path. If empty, auto-generates based on script name
            level: Logging level. If None, uses config.default_level
            config: LogConfig instance. If None, uses default LogConfig()

        Raises:
            ValueError: If output_method contains invalid values
        """
        # 避免重复初始化
        if self._initialized.get(module_name, False):
            return

        # 初始化配置
        self.config = config or LogConfig()
        self._handlers: dict[str, logging.Handler] = {}
        self._log = logging.getLogger(module_name)
        self._log.propagate = False  # 避免日志传播到root logger

        # 解析参数，使用config作为默认值
        if output_method is None:
            output_method = self.config.default_output_method
        if rich is None:
            rich = self.config.default_rich
        if level is None:
            level = self.config.default_level

        # 标准化output_method为列表
        if isinstance(output_method, str):
            output_method = [output_method]

        # 验证output_method
        if not set(output_method).issubset(VALID_OUTPUT_METHODS):
            raise ValueError(
                f"Invalid output method. Must be subset of: {VALID_OUTPUT_METHODS}. "
                f"Got: {set(output_method)}"
            )

        # 设置日志处理器
        self.setup_logger(output_method, fmt, rich, file)
        self.set_level(level)

        # 标记为已初始化
        self._initialized[module_name] = True

    def setup_logger(
        self,
        output_method: list[str],
        fmt: str,
        rich: bool,
        file: str | Path
    ) -> None:
        """
        Configure logger with handlers based on output methods.

        Args:
            output_method: List of output methods
            fmt: Custom format string (empty string uses defaults)
            rich: Whether to use rich console formatting
            file: Path to log file
        """
        # 确定日志文件路径
        if 'file' in output_method:
            log_file = self._resolve_log_file_path(file)
            file_handler = self._create_file_handler(log_file, fmt)
            self._handlers['file'] = file_handler
            self._log.addHandler(file_handler)

        # 控制台输出
        if 'console' in output_method:
            console_handler = self._create_console_handler(fmt, rich)
            self._handlers['console'] = console_handler
            self._log.addHandler(console_handler)

    def _resolve_log_file_path(self, file: str | Path) -> Path:
        """
        Resolve the log file path.

        Args:
            file: User-specified file path (empty for auto-generation)

        Returns:
            Resolved Path object for log file
        """
        if file:
            return Path(file)

        # 使用配置的默认目录或脚本目录
        log_dir = (
            self.config.default_log_dir
            if self.config.default_log_dir is not None
            else Path(os.path.abspath(sys.argv[0])).parent
        )

        # 确保目录存在
        log_dir.mkdir(parents=True, exist_ok=True)

        # 自动生成日志文件名
        log_filename = f"{Path(sys.argv[0]).stem}.log"
        return log_dir / log_filename

    def _create_file_handler(self, log_file: Path, fmt: str) -> logging.FileHandler:
        """
        Create file handler with configured formatting.

        Args:
            log_file: Path to log file
            fmt: Custom format (empty uses config.file_format)

        Returns:
            Configured FileHandler instance
        """
        handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
        format_str = fmt if fmt else self.config.file_format
        handler.setFormatter(
            logging.Formatter(format_str, self.config.datetime_format)
        )
        return handler

    def _create_console_handler(self, fmt: str, rich: bool) -> logging.Handler:
        """
        Create console handler (rich or standard).

        Args:
            fmt: Custom format (empty uses config formats)
            rich: Whether to use RichHandler

        Returns:
            Configured console handler (RichHandler or StreamHandler)
        """
        if rich:
            handler: logging.Handler = RichHandler(
                show_path=False,
                rich_tracebacks=True,
                markup=True,  # 允许rich标记
                show_time=True
            )
            format_str = fmt if fmt else self.config.rich_format
        else:
            handler = logging.StreamHandler(sys.stdout)
            format_str = fmt if fmt else self.config.console_format

        handler.setFormatter(
            logging.Formatter(format_str, self.config.datetime_format)
        )
        return handler

    def set_level(self, level: LogLevel) -> None:
        """
        Set the logging level.

        Args:
            level: Logging level string (case-insensitive)
        """
        log_level = LOG_LEVELS.get(level.lower(), logging.INFO)
        self._log.setLevel(log_level)

    def add_handler(self, name: str, handler: logging.Handler) -> None:
        """
        Add a custom handler to the logger.

        Args:
            name: Unique name for the handler
            handler: logging.Handler instance

        Raises:
            ValueError: If handler with same name already exists
        """
        if name in self._handlers:
            raise ValueError(f"Handler '{name}' already exists. Remove it first.")
        self._handlers[name] = handler
        self._log.addHandler(handler)

    def remove_handler(self, name: str) -> None:
        """
        Remove a handler by name.

        Args:
            name: Name of the handler to remove

        Raises:
            KeyError: If handler name not found
        """
        if name not in self._handlers:
            raise KeyError(f"Handler '{name}' not found.")
        handler = self._handlers.pop(name)
        self._log.removeHandler(handler)
        handler.close()

    def get_handlers(self) -> dict[str, logging.Handler]:
        """
        Get all registered handlers.

        Returns:
            Dictionary of handler names to handler instances
        """
        return self._handlers.copy()

    def clear_handlers(self) -> None:
        """Remove all handlers and close them properly."""
        for name in list(self._handlers.keys()):
            self.remove_handler(name)

    def log(self, level: str, msg: str, *args: Any, **kwargs: Any) -> None:
        """
        Generic logging method.

        Args:
            level: Log level name (debug/info/warning/error/critical)
            msg: Log message (supports %-formatting)
            *args: Arguments for %-formatting
            **kwargs: Additional logging kwargs (exc_info, stack_info, etc.)
        """
        if hasattr(self._log, level):
            getattr(self._log, level)(msg, *args, **kwargs)

    # Specific logging methods
    def info(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log an info message."""
        self.log('info', msg, *args, **kwargs)

    def warning(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log a warning message."""
        self.log('warning', msg, *args, **kwargs)

    def error(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log an error message."""
        self.log('error', msg, *args, **kwargs)

    def debug(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log a debug message."""
        self.log('debug', msg, *args, **kwargs)

    def critical(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log a critical message."""
        self.log('critical', msg, *args, **kwargs)

    def exception(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """
        Log an exception with traceback.
        Should be called from an exception handler.
        """
        kwargs.setdefault('exc_info', True)
        self.error(msg, *args, **kwargs)

    @property
    def help(self) -> str:
        """Return usage instructions."""
        return """
        Logger - A configurable singleton logging utility

        Basic Usage:
            from lntools.utils import Logger

            # Simple console logging
            log = Logger("myapp")
            log.info("Application started")

            # Console + file logging
            log = Logger("myapp", output_method=["console", "file"], file="/path/to/app.log")
            log.debug("Debug info")
            log.warning("Warning message")
            log.error("Error occurred")

        Advanced Usage:
            from lntools.utils import Logger, LogConfig

            # Customize default behavior globally
            config = LogConfig(
                datetime_format='%Y-%m-%d %H:%M:%S.%f',
                file_format='[%(asctime)s] %(levelname)-8s | %(name)s | %(message)s',
                default_level='debug',
                default_log_dir=Path('/var/log/myapp')
            )
            log = Logger("myapp", config=config)

            # Runtime handler management
            log.add_handler("syslog", my_syslog_handler)
            log.remove_handler("console")

            # Change log level at runtime
            log.set_level('debug')

        Parameters:
            module_name: str = "default"        # Logger instance identifier
            output_method: str | list = None    # 'console', 'file', or both
            fmt: str = ""                       # Custom format (overrides config)
            rich: bool = None                   # Use rich console formatting
            file: str = ""                      # Log file path
            level: str = None                   # 'debug'|'info'|'warning'|'error'|'critical'
            config: LogConfig = None            # Configuration object

        Default Formats (customizable via LogConfig):
            datetime_format = '%Y-%m-%d %H:%M:%S'
            file_format = '[%(asctime)s][%(name)s][%(levelname)s] %(message)s'
            console_format = '[%(asctime)s][%(name)s][%(levelname)s] %(message)s'
            rich_format = '[%(name)s] %(message)s'
        """

    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"Logger(name={self._log.name}, level={self._log.level}, "
            f"handlers={list(self._handlers.keys())})"
        )

    def __del__(self) -> None:
        """Cleanup handlers on deletion."""
        with suppress(AttributeError, RuntimeError):
            self.clear_handlers()
