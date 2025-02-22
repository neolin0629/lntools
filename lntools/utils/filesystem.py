"""
Functions to deal with files and directories.

This module provides utility functions for file system operations including:
- Path validation and manipulation
- File operations (move, copy, rename, remove)
- Directory operations
- File reading with multiple formats support

@author: Neo
@time: 2024/6/8
"""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Callable, Union, Dict, Any
import shutil
import numpy as np
import pandas as pd
import polars as pl

from lntools.utils.log import Logger 
from lntools.utils.typing import PathLike, DatetimeLike

log = Logger("lntools.utils.filesystem")


def is_dir(d: PathLike) -> bool:
    """Check if path is a directory."""
    return Path(d).is_dir()


def is_file(file: PathLike) -> bool:
    """Check if path is a file."""
    return Path(file).is_file()


def handle_path(path: PathLike) -> Path:
    """
    Resolve and prepare a path for use.

    Args:
        path: Path to process

    Returns:
        Path: Resolved absolute path with created parent directories
    """
    resolved_path = Path(path).expanduser().resolve()
    resolved_path.parent.mkdir(parents=True, exist_ok=True)
    return resolved_path


def make_dirs(d: PathLike, parents: bool = True, exist_ok: bool = True) -> None:
    """
    Create directory(ies) at the specified path.

    Args:
        d: Directory path to create
        parents: If True, create parent directories if needed
        exist_ok: If False, raise error if directory exists
    """
    Path(d).mkdir(parents=parents, exist_ok=exist_ok)


def move(
    src: PathLike,
    dst: PathLike,
    keep_old: bool = True,
    exist_ok: bool = False
) -> None:
    """
    Move or copy (file or directory) from src to dst.

    Args:
        src: Source path (file or directory)
        dst: Destination path (directory)
        keep_old: If True, copy to destination; if False, move
        exist_ok: If True, replace existing files/directories

    Raises:
        FileNotFoundError: If source path does not exist
        FileExistsError: If destination exists and exist_ok is False
    """
    src, dst = Path(src), Path(dst)
    if not src.exists():
        raise FileNotFoundError(f"Source path does not exist: {src}")

    dst.parent.mkdir(parents=True, exist_ok=True)

    try:
        if not keep_old:
            shutil.move(str(src), str(dst))
        else:
            if src.is_dir():
                shutil.copytree(str(src), str(dst), dirs_exist_ok=exist_ok)
            else:
                shutil.copy2(str(src), str(dst))
    except FileExistsError:
        if not exist_ok:
            raise


def rename(src: PathLike, dst: PathLike) -> Path:
    """
    Rename a file or directory.

    Args:
        src: Source path
        dst: Destination path

    Returns:
        Path: New path after rename

    Raises:
        FileNotFoundError: If source does not exist
    """
    src, dst = Path(src), Path(dst)
    if not src.exists():
        raise FileNotFoundError(f"Source path does not exist: {src}")
    if dst.exists():
        log.info(f"{dst} already exists, will be overwritten")
    return src.replace(dst)


def remove(path: PathLike) -> None:
    """
    Remove a file or directory recursively.

    Args:
        path: Path to remove
    """
    path = Path(path)
    try:
        if path.is_file():
            path.unlink(missing_ok=True)
        elif path.is_dir():
            shutil.rmtree(path)
    except (OSError, PermissionError) as e:
        log.error(f"Failed to remove {path}: {e}")


def file_time(file_path: PathLike, method: str = 'm') -> datetime:
    """
    Get file's timestamp.

    Args:
        file_path: The file path to check
        method: Time type to return:
            'a' - last accessed time
            'm' - last modified time
            'c' - creation time

    Returns:
        datetime: Requested timestamp

    Raises:
        FileNotFoundError: If file does not exist
        ValueError: If method is invalid
    """
    from lntools.timeutils import ts2dt
    path_obj = Path(file_path)
    if not path_obj.exists():
        raise FileNotFoundError(f"File does not exist: {file_path}")

    times = {
        'a': path_obj.stat().st_atime,
        'm': path_obj.stat().st_mtime,
        'c': path_obj.stat().st_ctime
    }
    if method not in times:
        raise ValueError("Method must be one of 'a' (accessed), 'm' (modified), 'c' (created)")

    return ts2dt(times[method])


def list_paths(
    rootdir: PathLike,
    files_only: bool = False,
    dirs_only: bool = False
) -> List[Path]:
    """
    List paths under the given root directory.

    Args:
        rootdir: The root directory to search
        files_only: Whether to return only files
        dirs_only: Whether to return only directories

    Returns:
        List of paths matching the criteria

    Raises:
        FileNotFoundError: If root directory does not exist
    """
    root = Path(rootdir).expanduser().resolve()
    if not root.exists():
        raise FileNotFoundError(f"Directory does not exist: {root}")

    paths = root.rglob('*')
    if files_only and not dirs_only:
        return [p for p in paths if p.is_file()]
    if dirs_only and not files_only:
        return [p for p in paths if p.is_dir()]
    return list(paths)


# Simplified aliases for common operations
get_all = list_paths


def get_dirs(root: PathLike) -> List[Path]:
    """Get all directories under the given root directory."""
    return list_paths(root, dirs_only=True)


def get_files(root: PathLike) -> List[Path]:
    """Get all files under the given root directory."""
    return list_paths(root, files_only=True)


READERS: Dict[str, Dict[str, Callable]] = {
    "pandas": {
        ".csv": pd.read_csv,
        ".txt": pd.read_csv,
        ".parquet": pd.read_parquet,
        ".xlsx": pd.read_excel,
        ".xls": pd.read_excel,
        ".json": pd.read_json,
        ".feather": pd.read_feather,
    },
    "polars": {
        ".csv": pl.read_csv,
        ".txt": pl.read_csv,
        ".parquet": pl.read_parquet,
        ".xlsx": pl.read_excel,
        ".xls": pl.read_excel,
        ".json": pl.read_json,
        ".feather": pl.read_ipc,
    },
    "numpy": {
        ".csv": np.loadtxt,
        ".txt": np.loadtxt,
        ".npy": np.load,
        ".npz": np.load,
    },
    "base": {
        ".txt": lambda path, **kwargs: Path(path).read_text(encoding='utf-8', **kwargs),
        ".csv": lambda path, **kwargs: Path(path).read_text(encoding='utf-8', **kwargs),
        ".html": lambda path, **kwargs: Path(path).read_text(encoding='utf-8', **kwargs),
        ".jpg": lambda path, **kwargs: Path(path).read_bytes(),
        ".png": lambda path, **kwargs: Path(path).read_bytes(),
        ".pdf": lambda path, **kwargs: Path(path).read_bytes(),
        ".mp3": lambda path, **kwargs: Path(path).read_bytes(),
        ".mp4": lambda path, **kwargs: Path(path).read_bytes(),
    },
}


def read_file(
    path: PathLike,
    df_lib: Optional[str] = None,
    **kwargs: Any
) -> Union[pd.DataFrame, pl.DataFrame, np.ndarray, str, bytes]:
    """
    Read file content using specified library.

    Args:
        path: Path to the file
        df_lib: Library to use for reading ('pandas', 'polars', 'numpy', or 'base')
        **kwargs: Additional arguments passed to the reader function

    Returns:
        File content in format determined by the library:
            - pandas/polars: DataFrame
            - numpy: ndarray
            - base: str or bytes

    Raises:
        ValueError: If file type or library is unsupported
        FileNotFoundError: If file doesn't exist
        RuntimeError: If reading fails
    """
    if not Path(path).exists():
        raise FileNotFoundError(f"File not found: {path}")

    if not df_lib or (df_lib not in READERS):
        from lntools.config import CONFIG
        df_lib = CONFIG.df_lib

    extension = Path(path).suffix.lower()

    if df_lib not in READERS:
        raise ValueError(f"Unsupported library: {df_lib}")

    reader = READERS[df_lib].get(extension)
    if not reader:
        raise ValueError(f"Unsupported file type: {extension} for library: {df_lib}")

    try:
        return reader(path, **kwargs)
    except Exception as e:
        raise RuntimeError(f"Failed to read {path} using {df_lib}: {str(e)}") from e


def _get_formatted_files(
    sdt: DatetimeLike,
    edt: DatetimeLike,
    path: PathLike,
    file_pattern: str = "{date}.csv",
    date_format: str = "%Y-%m-%d",
    use_tcal: bool = True
) -> List[Path]:
    """
    Get list of formatted file paths between two dates.

    Args:
        sdt: Start date
        edt: End date
        path: Directory path
        file_pattern: File name pattern with {date} placeholder
        date_format: Date format in file names
        use_tcal: Whether to use trading calendar

    Returns:
        List of Path objects for existing files

    Raises:
        RuntimeError: If no matching files found
    """
    from lntools.timeutils import dt2str, get

    if use_tcal:
        from qxanalyze.api.tcalendar import TCalendar
        dates = TCalendar(["tdate"]).get(sdt, edt, dtype="datetime")
    else:
        dates = get(sdt, edt)

    base_path = Path(path)
    if not base_path.exists():
        raise FileNotFoundError(f"Directory not found: {path}")

    # Generate expected and actual file paths
    expected_files = [file_pattern.format(date=dt2str(date, date_format)) for date in dates]
    existing_files = [
        base_path / f for f in expected_files
        if (base_path / f).exists()
    ]

    # Log missing files
    missing = set(expected_files) - {p.name for p in existing_files}
    if missing:
        from lntools.utils.human import lists
        log.warning(f"Missing files: {lists(missing)}")

    if not existing_files:
        raise RuntimeError(
            f"No files matching '{file_pattern}' found in {path}"
            f"between {sdt} and {edt}"
        )

    return existing_files


def read_directory(
    path: PathLike,
    reader: Optional[Callable] = None,
    sdt: Optional[DatetimeLike] = None,
    edt: Optional[DatetimeLike] = None,
    file_pattern: str = "{date}.csv",
    date_format: str = "%Y-%m-%d",
    use_tcal: bool = True,
    df_lib: str = "polars",
    threads: int = 10,
    **kwargs: Any
) -> Union[pd.DataFrame, pl.DataFrame]:
    """
    Read and concatenate files from directory.

    Args:
        path: Directory path
        reader: Custom reader function (defaults to read_file)
        sdt: Start date (optional)
        edt: End date (optional)
        file_pattern: File name pattern
        date_format: Date format in file names
        use_tcal: Use trading calendar
        df_lib: Library for data handling
        threads: Number of parallel threads
        **kwargs: Additional reader arguments

    Returns:
        Concatenated DataFrame

    Raises:
        ValueError: If df_lib is invalid
        RuntimeError: If no files found or reading fails
    """
    from lntools.utils.misc import is_valid_df_lib
    is_valid_df_lib(df_lib)

    reader = reader or read_file
    base_path = Path(path)

    # Get file list
    files = (_get_formatted_files(sdt, edt, base_path, file_pattern, date_format, use_tcal)
             if sdt is not None and edt is not None
             else get_files(base_path))

    if not files:
        return pl.DataFrame() if df_lib == "polars" else pd.DataFrame()

    # Parallel read files
    def _read_file(f: Path) -> Union[pd.DataFrame, pl.DataFrame]:
        try:
            if reader is read_file:
                return reader(f, df_lib=df_lib, **kwargs)

            return reader(f, **kwargs)
        except Exception as e:  # pylint: disable=broad-exception-caught
            log.error(f"Failed to read {f}: {e}")
            return pl.DataFrame() if df_lib == "polars" else pd.DataFrame()

    with ThreadPoolExecutor(max_workers=threads) as executor:
        results = list(executor.map(_read_file, files))

    # Remove empty DataFrames
    results = [df for df in results if not df.shape[0] > 0]

    if not results:
        log.warning("No data read from any files")
        return pl.DataFrame() if df_lib == "polars" else pd.DataFrame()

    # Concatenate results
    try:
        return (pl.concat(results, how="vertical_relaxed") if df_lib == "polars"
                else pd.concat(results, ignore_index=True))
    except Exception as e:
        raise RuntimeError(f"Failed to concatenate results: {e}") from e
