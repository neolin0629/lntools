"""
Configuration API of lntools.
@author: Neo
@date: 2024/6/9
"""
import importlib.resources
from configparser import ConfigParser, ExtendedInterpolation
from dataclasses import dataclass, field, fields
from pathlib import Path
from typing import Any, Dict

from yaml import Loader, dump, load, safe_dump, safe_load

from lntools.utils import Logger, PathLike, handle_path


log = Logger("lntools.config")
PATH: Path = handle_path(Path.home() / ".config" / "lntools" / "lntools.yaml")


def read_pkg_ini(
    config_name: str, package: str = "lntools", encoding: str = "utf8"
) -> ConfigParser:
    """
    Read an INI file from a package and return a ConfigParser object.

    Args:
        config_name: Path to the INI file relative to the package root.
        package: Package name where the INI file is located.
        encoding: File encoding (default: utf8).

    Returns:
        ConfigParser: A parser object loaded with the INI file content.

    Raises:
        FileNotFoundError: If the specified INI file does not exist.

    Time Complexity: O(n) where n is the file size.
    """
    ref = importlib.resources.files(package) / config_name
    with importlib.resources.as_file(ref) as config_path:
        if not config_path.exists():
            raise FileNotFoundError(
                f"INI file '{config_name}' not found in package '{package}'"
            )
        cfg = ConfigParser(interpolation=ExtendedInterpolation())
        try:
            cfg.read(str(config_path), encoding=encoding)
        except Exception as exc:
            log.error("Failed to parse INI file '%s': %s", config_name, exc)
            raise
    return cfg


def read_ini(path: PathLike, encoding: str = "utf8") -> ConfigParser:
    """
    Read an INI file from filesystem and return a ConfigParser object.

    Args:
        path: Path to the INI file.
        encoding: File encoding (default: utf8).

    Returns:
        ConfigParser: Parsed configuration object.

    Raises:
        FileNotFoundError: If file does not exist.
        ValueError: If file cannot be parsed.

    Time Complexity: O(n) where n is the file size.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"INI file not found: {path}")

    cfg = ConfigParser(interpolation=ExtendedInterpolation())
    try:
        with open(path, "r", encoding=encoding) as file:
            cfg.read_file(file)
    except Exception as exc:
        log.error("Failed to read INI file '%s': %s", path, exc)
        raise ValueError(f"Cannot parse INI file: {path}") from exc
    return cfg


def write_ini(path: PathLike, cfg: ConfigParser, encoding: str = "utf8") -> None:
    """
    Write a ConfigParser object to an INI file.

    Args:
        path: Target file path.
        cfg: ConfigParser object to write.
        encoding: File encoding (default: utf8).

    Raises:
        OSError: If file cannot be written (permission denied, disk full, etc).

    Time Complexity: O(n) where n is the config size.
    """
    path = Path(path)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding=encoding) as file:
            cfg.write(file)
    except OSError as exc:
        log.error("Failed to write INI file '%s': %s", path, exc)
        raise


def read_pkg_yaml(
    config_name: str, package: str = "lntools", encoding: str = "utf8", safe: bool = True
) -> Any:
    """
    Read a YAML file from a package and return its contents.

    Args:
        config_name: Path to the YAML file relative to the package root.
        package: Package name where the YAML file is located.
        encoding: File encoding (default: utf8).
        safe: Use safe_load (recommended) vs load.

    Returns:
        Parsed YAML content (dict, list, or primitive types).

    Raises:
        FileNotFoundError: If resource not found.
        ValueError: If YAML parsing fails.

    Time Complexity: O(n) where n is the file size.
    """
    ref = importlib.resources.files(package) / config_name
    with importlib.resources.as_file(ref) as resource_path:
        if not resource_path.exists():
            raise FileNotFoundError(
                f"YAML file '{config_name}' not found in package '{package}'"
            )
        try:
            with open(resource_path, "r", encoding=encoding) as file:
                return safe_load(file) if safe else load(file, Loader=Loader)
        except Exception as exc:
            log.error("Failed to parse YAML file '%s': %s", config_name, exc)
            raise ValueError(f"Cannot parse YAML: {config_name}") from exc


def read_yaml(path: PathLike, encoding: str = "utf8", safe: bool = True) -> Any:
    """
    Read a YAML file from filesystem and return its contents.

    Args:
        path: Path to the YAML file.
        encoding: File encoding (default: utf8).
        safe: Use safe_load (recommended) vs load.

    Returns:
        Parsed YAML content (dict, list, or primitive types).

    Raises:
        FileNotFoundError: If file does not exist.
        ValueError: If YAML parsing fails.

    Time Complexity: O(n) where n is the file size.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"YAML file not found: {path}")

    try:
        with open(path, "r", encoding=encoding) as file:
            return safe_load(file) if safe else load(file, Loader=Loader)
    except Exception as exc:
        log.error("Failed to parse YAML file '%s': %s", path, exc)
        raise ValueError(f"Cannot parse YAML: {path}") from exc


def write_yaml(path: PathLike, data: Any, safe: bool = True, encoding: str = "utf8") -> None:
    """
    Write data to a YAML file.

    Args:
        path: Target file path.
        data: Data structure to serialize (dict, list, primitives).
        safe: Use safe_dump (recommended) vs dump.
        encoding: File encoding (default: utf8).

    Raises:
        OSError: If file cannot be written.

    Time Complexity: O(n) where n is the data structure size.
    """
    path = Path(path)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding=encoding) as file:
            file.write(safe_dump(data) if safe else dump(data))
    except OSError as exc:
        log.error("Failed to write YAML file '%s': %s", path, exc)
        raise


@dataclass
class Config:
    """
    Configuration dataclass for lntools.

    Attributes:
        db: Database configuration dict (host, port, etc).
        mail: Mail server configuration dict (server, username, password, etc).
        df_lib: Default dataframe library ("polars", "pandas", or "numpy").
    """

    db: Dict[str, str] = field(default_factory=dict)
    mail: Dict[str, str] = field(default_factory=dict)
    df_lib: str = field(default="polars")


def config() -> Config:
    """
    Load lntools configuration from `~/.config/lntools/lntools.yaml`.

    Creates the config file with defaults if it does not exist.

    Returns:
        Config: Current configuration instance.

    Time Complexity: O(n) where n is the config file size.
    """
    cfg = Config()

    # Create config file with defaults if missing
    if not PATH.exists():
        log.info("Creating lntools config file at: %s", PATH)
        PATH.parent.mkdir(parents=True, exist_ok=True)
        write_yaml(PATH, cfg.__dict__)
        return cfg

    # Load and merge user config
    try:
        user_config = read_yaml(PATH)
        if user_config:
            for field_name in (f.name for f in fields(Config)):
                if field_name in user_config:
                    setattr(cfg, field_name, user_config[field_name])
    except (FileNotFoundError, ValueError, OSError) as exc:
        log.warning("Failed to load config, using defaults: %s", exc)

    return cfg


CONFIG = config()
