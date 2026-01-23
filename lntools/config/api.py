"""
Configuration API of lntools.
@author: Neo
@date: 2024/6/9
"""
from configparser import ConfigParser, ExtendedInterpolation
from dataclasses import dataclass, fields, field
from pathlib import Path

import importlib.resources
from yaml import safe_dump, dump, safe_load, load, Loader

from lntools.utils import handle_path, Logger, PathLike


log = Logger("lntools.config")
PATH: Path = handle_path(Path.home() / ".config" / "lntools" / "lntools.yaml")


def read_pkg_ini(config_name: str, package: str = 'lntools', encoding='utf8'):
    """
    Read an ini file in a package, return a ConfigParser object.
    Args:
        config_name (str): Path to the ini file relative to the package root.
        package (str): Package name where the ini file is located.
        encoding (str): Encoding of the ini file.

    Returns:
        ConfigParser: A parser object loaded with the ini file content.
    """
    ref = importlib.resources.files(package) / config_name
    with importlib.resources.as_file(ref) as config_path:
        if config_path.exists():
            cfg = ConfigParser(interpolation=ExtendedInterpolation())
            cfg.read(str(config_path), encoding=encoding)
        else:
            raise FileNotFoundError(f"The specified ini file {config_name} does not exist in the package {package}.")
    return cfg


def read_ini(path: PathLike, encoding='utf8'):
    """
    read an ini file, return a map ordered dict
    """
    cfg = ConfigParser(interpolation=ExtendedInterpolation())
    with open(path, 'r', encoding=encoding) as file:
        cfg.read_file(file)
    return cfg


def write_ini(path: PathLike, cfg: ConfigParser):
    """
    Write a ConfigParser object back to an INI file.
    """
    with open(path, 'w', encoding='utf8') as file:
        cfg.write(file)


def read_pkg_yaml(config_name, package='lntools', encoding='utf8', safe=True):
    """
    Read a YAML file from a package and return its contents.
    """
    ref = importlib.resources.files(package) / config_name
    with importlib.resources.as_file(ref) as resource_path:
        if resource_path.exists():
            with open(resource_path, 'r', encoding=encoding) as file:
                return safe_load(file) if safe else load(file, Loader=Loader)
        else:
            raise FileNotFoundError(f"Resource {config_name} not found in package {package}.")


def read_yaml(path: PathLike, encoding='utf8', safe=True):
    """
    Read a YAML file and return its contents.
    """
    with open(path, 'r', encoding=encoding) as file:
        return safe_load(file) if safe else load(file, Loader=Loader)


def write_yaml(path: PathLike, data, safe: bool = True):
    """
    Write data to a YAML file.
    """
    with open(path, 'w', encoding='utf8') as file:
        file.write(safe_dump(data) if safe else dump(data))


@dataclass
class Config:
    """
    Configuration dataclass for lntools.
    """
    db: dict[str, str] | None = field(default_factory=dict)
    mail: dict[str, str] | None = field(default=None)
    df_lib: str = field(default="polars")


def config() -> Config:
    """
    Get the initialized configuration of lntools in file
        `~/.config/lntools/lntools.yaml`.
    Create and populate the config file with defaults if it does not exist.

    Returns
    -------
    Config: Current initial configuration of lntools.
    """
    cfg = Config()

    # Create and populate the config file with defaults if it does not exist.
    if not PATH.exists():
        log.info(f"Creating new lntools config file at {PATH}")
        write_yaml(PATH, cfg.__dict__)
        return cfg

    if user_config := read_yaml(PATH):
        for field_name in (f.name for f in fields(Config)):
            if field_name in user_config:
                setattr(cfg, field_name, user_config[field_name])

    return cfg


CONFIG = config()
