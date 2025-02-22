#
# directory.py
# @author Linnan
# @description Describing Data Source of `Directory`
# @created 2024-12-17 14:02:28.270Z+08:00
# @last-modified 2024-12-17 14:02:28.270Z+08:00
#
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
import os
from typing import Callable, List, Optional, Union, Any, Dict

import numpy as np
import pandas as pd
import polars as pl
from datetime import datetime

from lntools.utils.typing import PathLike
from lntools.utils.log import Logger
from lntools.utils.filesystem import read_file

log = Logger("lntools.utils.directory")


class Directory:
    """Directory data reader with multi-threading support.

    Provides functionality to read data files from a directory, with optional 
    date-based filtering and multi-threading support.

    Args:
        path: Path to the local directory
        threads: Number of threads to use for parallel reading, defaults to 10

    Raises:
        ValueError: If path is invalid or directory doesn't exist
    """

    _SUPPORTED_LIBS = frozenset({"pandas", "polars", "numpy"})

    def __init__(self, path: str, threads: int = 10) -> None:
        self._validate_path(path)
        self.path: str = path
        self.threads: int = max(1, threads)
        self.file_pattern: str = "{date}.csv"
        self.date_format: str = "%Y-%m-%d"
        self.use_tcal: bool = True
        self.lib: Optional[str] = None

    @staticmethod
    def _validate_path(path: str) -> None:
        if not isinstance(path, str) or not os.path.isdir(path):
            raise ValueError(f"Invalid directory path: {path}")

    def read(
        self,
        sdt: Optional[Union[str, datetime]] = None,
        edt: Optional[Union[str, datetime]] = None,
        reader: Optional[Callable[[PathLike], Union[pd.DataFrame, pl.DataFrame, np.ndarray]]] = None,
        **kwargs: Any
    ) -> Union[pd.DataFrame, pl.DataFrame, np.ndarray]:
        """Read data from directory with optional date filtering.

        Args:
            sdt: Start date for filtering files
            edt: End date for filtering files  
            reader: Custom function to read individual files
            **kwargs: Additional parameters to override instance attributes

        Returns:
            Combined data from all matching files

        Raises:
            RuntimeError: If no matching files found
            ValueError: If invalid parameters provided
        """
        try:
            self._update_parameters(kwargs)
            self.lib = self._get_lib(kwargs.get("lib"))
            reader = reader or self._make_default_reader
 
            params = (
                self._get_all_files_in_dir() 
                if not (sdt and edt) 
                else [os.path.join(self.path, f) for f in self._get_daily_files(sdt, edt)]
            )

            from lntools.utils.human import path as human_path
            log.info(f"Reading directory: {human_path(self.path)} ({len(params)} files)")

            data_list = (
                [reader(param) for param in params]
                if len(params) <= 1 or self.threads == 1
                else self._multithread_read(reader, params)
            )

            return self._concat_data_list(data_list, self.lib)

        except (IOError, OSError, ValueError) as e:
            log.error(f"Failed to read directory: {str(e)}")
            raise

    def _update_parameters(self, kwargs: Dict[str, Any]) -> None:
        """Update instance parameters from kwargs."""
        self.threads = kwargs.get("threads", self.threads)
        self.file_pattern = kwargs.get("file_pattern", self.file_pattern)
        self.date_format = kwargs.get("date_format", self.date_format)
        self.use_tcal = kwargs.get("use_tcal", self.use_tcal)

    def _get_lib(self, lib: Optional[str]) -> str:
        """Get and validate data analysis library."""
        if not lib or lib not in self._SUPPORTED_LIBS:
            from lntools.config import CONFIG
            lib = CONFIG.df_lib
        if lib not in self._SUPPORTED_LIBS:
            raise ValueError(f"Unsupported library: {lib}")
        return lib

    def _multithread_read(
        self,
        reader: Callable[[str], Union[pd.DataFrame, pl.DataFrame, np.ndarray]],
        params: List[str],
    ) -> List[Union[pd.DataFrame, pl.DataFrame, np.ndarray]]:
        """Parallel file reading with error handling."""
        threads = min(len(params), self.threads)
        log.info(f"Using {threads} threads for reading")

        results = []
        with ThreadPoolExecutor(max_workers=threads) as executor:
            future_to_param = {executor.submit(reader, param): param for param in params}
            for future in as_completed(future_to_param):
                param = future_to_param[future]
                try:
                    results.append(future.result())
                except (IOError, OSError, ValueError) as e:
                    log.error(f"Failed to read {param}: {str(e)}")
        return results

    def _concat_data_list(
        self,
        data_list: List[Union[pd.DataFrame, pl.DataFrame, np.ndarray]],
        lib: str,
    ) -> Union[pd.DataFrame, pl.DataFrame, np.ndarray]:
        """Combine multiple datasets based on library type."""
        if not data_list:
            return {
                "polars": pl.DataFrame(),
                "numpy": np.array([]),
                "pandas": pd.DataFrame(),
            }[lib]

        if lib == "polars":
            return pl.concat(data_list, how="vertical_relaxed")
        if lib == "numpy":
            return np.concatenate(data_list, axis=0)
        if lib == "pandas":
            return pd.concat(data_list)

    def _make_default_reader(
        self, path_str: str
    ) -> Union[pd.DataFrame, pl.DataFrame, np.ndarray]:
        """Create default reader based on specified library."""
        try:
            return read_file(path_str, df_lib=self.lib)
        except (IOError, OSError, ValueError, AssertionError) as e:
            log.warning(f"Failed to read {path_str}: {str(e)}")
            return self._concat_data_list([], self.lib)

    # def _multithread_read(
    #     self,
    #     reader: Callable[[str], Union[pd.DataFrame, pl.DataFrame, np.ndarray]],
    #     params: List[str],
    # ) -> List[Union[pd.DataFrame, pl.DataFrame, np.ndarray]]:
    #     """
    #     使用多进程并行读取文件列表。
    #     """
    #     threads = min(len(params), self.threads)
    #     log.info(f"Using {threads} threads for reading directory.")

    #     with ThreadPoolExecutor(max_workers=threads) as executor:
    #         data_list = executor.map(reader, params)
    #     return data_list

    def _get_all_files_in_dir(self) -> List[str]:
        """
        获取目录下所有文件的路径列表。
        """
        return [os.path.join(self.path, f) for f in os.listdir(self.path)]

    def _get_daily_files(self, sdt: Any, edt: Any) -> List[str]:
        """Get matching files for date range."""
        from lntools.utils.human import lists
        from lntools.timeutils import get as getn, dt2str
        from qxanalyze.api.tcalendar import get_Tcalendar

        date_seq = (
            get_Tcalendar().get(sdt, edt, dtype="datetime")
            if self.use_tcal
            else getn(sdt, edt)
        )

        dates = [dt2str(t, self.date_format) for t in date_seq]
        files = [self.file_pattern.format(date=d) for d in dates]
        all_in_dir = set(os.listdir(self.path))

        missing = [f for f in files if f not in all_in_dir]
        if missing:
            log.warning(f"Missing files: {lists(missing)}")

        existing = [f for f in files if f in all_in_dir]
        if not existing:
            raise RuntimeError(
                f"No matching files found for pattern '{self.file_pattern}' "
                f"in {self.path} (date range: {sdt} ~ {edt})"
            )
        return existing

    @property
    def is_(self) -> bool:
        return os.path.isdir(self.path)

    @property
    def help(self):
        """
        展示 read 方法中的可选参数及示例。
        """
        return """
        The optional parameters of `read`:

        sdt         : DatetimeLike, start date
        edt         : DatetimeLike, end date
        reader      : Callable, a custom function to read single file
        file_pattern: str, define how to insert 'date' into file name, e.g. "pos{date}.csv"
        date_format : str, define date format, e.g. "%Y%m%d"
        use_tcal    : bool, if use trading calendar or not
        lib         : {"pandas","polars","numpy"}, default from CONFIG if not given
        threads   : int, how many threads for parallel reading

        Examples

        1) Read directory with trading calendar
        ------------------------------------------------
            d = Directory("E:/project/quote/px")
            read_params = {"lib": "polars", "file_pattern": "{date}.parquet",
                        "date_format": "%Y-%m-%d", "use_tcal": True}
            data = d.read(sdt=20210101, edt=20230801, **read_params)

        2) Read entire directory without specifying date range
        ------------------------------------------------
            d = Directory("E:/project/quote/px")
            data = d.read()
        """


if __name__ == "__main__":
    d = Directory("/home/lin/data/quote/etfdaily")
    read_params = {
        "lib": "polars",
        "file_pattern": "{date}.parquet",
        "date_format": "%Y%m%d",
        "use_tcal": True,
        "threads": 3
    }
    print(d.read(sdt="2023-12-28", edt="2024-01-05", **read_params))
