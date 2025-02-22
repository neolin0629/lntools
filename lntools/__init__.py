"""
@author neo
@time 2024/6/11
"""
import pandas as pd

from .bot import notify_feishu

# Import from config module
from .config import CONFIG, read_pkg_ini, read_ini, write_ini, read_pkg_yaml, read_yaml, write_yaml

# Import from mail module
from .mail import MailPlus

# Import from time module, handling potential duplicate imports
from .timeutils import (
    now,
    day_of_week,
    timer,
    adjust,
    diff,
    get,
    str2dt,
    str2ts,
    ts2dt,
    ts2str,
    dt2str,
    dt2ts,
    SHORTCUTS,
    is_date_pd,
    is_date_pl
)

# Import from utils module, avoiding redundant imports
from .utils import (
    CLI, Columns, filter_columns, Directory, File,
    is_dir, is_file, handle_path, make_dirs,
    move, rename, remove, file_time, list_paths, get_all, get_files, get_dirs,
    read_file, read_directory, path,  unit, sec2str, lists, ranges, datetime, fprint, track, Logger,
    missing_dependency, is_valid_df_lib, is_valid_exchange,
    ArrayLike, SeriesLike, DatetimeLike, DataFrameLike, PolarsDate, PathLike
)


# Enable copy_on_write to optimize memory usage during chained assignment
pd.options.mode.copy_on_write = True


__all__ = [
    "notify_feishu",
    "CONFIG",
    "read_pkg_ini",
    "read_ini",
    "write_ini",
    "read_pkg_yaml",
    "read_yaml",
    "write_yaml",
    "MailPlus",
    "now",
    "day_of_week",
    "timer",
    "adjust",
    "diff",
    "get",
    "str2dt",
    "str2ts",
    "ts2dt",
    "ts2str",
    "dt2str",
    "dt2ts",
    "SHORTCUTS",
    "is_date_pd",
    "is_date_pl",
    "CLI",
    "Columns",
    "filter_columns",
    "Directory",
    "File",
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
    "path",
    "unit",
    "sec2str",
    "lists",
    "ranges",
    "datetime",
    "fprint",
    "track",
    "Logger",
    "missing_dependency",
    "is_valid_df_lib",
    "is_valid_exchange",
    "ArrayLike",
    "SeriesLike",
    "DatetimeLike",
    "DataFrameLike",
    "PolarsDate",
    "PathLike"
]
