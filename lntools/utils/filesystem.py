from collections.abc import Callable, Sequence
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
import shutil
from typing import Any, TypeVar

import numpy as np
import pandas as pd
import polars as pl

from .log import Logger
from .typing import DatetimeLike, PathLike

T = TypeVar("T")
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
    path_obj = Path(file_path)
    if not path_obj.exists():
        raise FileNotFoundError(f"File does not exist: {file_path}")

    stat = path_obj.stat()
    if method == 'a':
        timestamp = stat.st_atime
    elif method == 'm':
        timestamp = stat.st_mtime
    elif method == 'c':
        timestamp = stat.st_birthtime
    else:
        raise ValueError("Method must be one of 'a' (accessed), 'm' (modified), 'c' (created)")

    return datetime.fromtimestamp(timestamp)


def list_paths(
    rootdir: PathLike,
    files_only: bool = False,
    dirs_only: bool = False
) -> list[Path]:
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


def get_dirs(root: PathLike) -> list[Path]:
    """Get all directories under the given root directory."""
    return list_paths(root, dirs_only=True)


def get_files(root: PathLike) -> list[Path]:
    """Get all files under the given root directory."""
    return list_paths(root, files_only=True)


READERS: dict[str, dict[str, Callable[..., Any]]] = {
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


def load_data(
    file_path: str | Path,
    engine: str = "pandas",
    **kwargs: Any
) -> Any:
    """
    统一数据加载接口，根据后缀自动选择 Reader。

    Args:
        file_path: 文件路径
        engine: 使用的引擎 ('pandas', 'polars', 'numpy', 'base')
        **kwargs: 传递给底层读取函数的参数 (如 sep, encoding 等)
    """
    path = Path(file_path)
    ext = path.suffix.lower()

    # 1. 检查引擎是否存在
    if engine not in READERS:
        raise ValueError(f"Unsupported engine: {engine}. Available options: {list(READERS.keys())}")

    # 2. 获取该引擎下的所有可用后缀读取器
    engine_readers = READERS[engine]

    # 3. 匹配后缀并执行
    if ext in engine_readers:
        reader = engine_readers[ext]
        return reader(str(path), **kwargs)

    raise ValueError(f"engine '{engine}' does not support file format: {ext}")


def read_file(
    path: PathLike,
    engine: str | None = None,
    **kwargs: Any
) -> pd.DataFrame | pl.DataFrame | np.ndarray | str | bytes:
    """
    Read file content using specified library.

    Args:
        path: Path to the file
        engine: Engine to use for reading ('pandas', 'polars', 'numpy', or 'base')
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

    if not engine:
        from lntools.config import CONFIG
        engine = CONFIG.df_lib

    try:
        return load_data(file_path=path, engine=str(engine), **kwargs)
    except ValueError as e:
        raise e
    except Exception as e:
        raise RuntimeError(f"Failed to read {path} using {engine}: {str(e)}") from e


def _get_formatted_files(
    sdt: DatetimeLike,
    edt: DatetimeLike,
    path: PathLike,
    file_pattern: str = "{date}.csv",
    date_format: str = "%Y-%m-%d",
    trading_dates: Sequence[DatetimeLike] | None = None
) -> list[Path]:
    """
    Get list of formatted file paths between two dates.

    Args:
        sdt: Start date
        edt: End date
        path: Directory path
        file_pattern: File name pattern with {date} placeholder
        date_format: Date format in file names
        trading_dates: Pre-defined list of dates to use. If None, uses natural dates via get_range.

    Returns:
        List of Path objects for existing files

    Raises:
        FileNotFoundError: If directory does not exist
        RuntimeError: If no matching files found

    Time Complexity: O(n), where n is the number of dates
    Space Complexity: O(n) for storing file paths
    """
    from lntools.timeutils import dt2str, get_range

    # 使用传入的 trading_dates 或者通过 get_range 获取自然日
    if trading_dates is not None:
        dates = trading_dates
        log.debug(f"Using {len(dates)} provided trading dates")
    else:
        dates = get_range(sdt, edt)
        log.debug(f"Using natural date range: {len(dates)} days from {sdt} to {edt}")

    base_path = Path(path)
    if not base_path.exists():
        raise FileNotFoundError(f"Directory not found: {path}")

    # Generate expected and actual file paths
    expected_files = [
        file_pattern.format(date=dt2str(pd.Timestamp(date), date_format)) for date in dates
    ]
    existing_files = [
        base_path / f for f in expected_files
        if (base_path / f).exists()
    ]

    # Log missing files (only show first 10 to avoid cluttering logs)
    missing = set(expected_files) - {p.name for p in existing_files}
    if missing:
        from lntools.utils.human import lists
        log.warning(f"Missing {len(missing)} files: {lists(sorted(missing), n=10)}")

    if not existing_files:
        raise RuntimeError(
            f"No files matching '{file_pattern}' found in {path} "
            f"between {sdt} and {edt}"
        )

    log.info(f"Found {len(existing_files)}/{len(dates)} files in {path}")
    return existing_files


def read_directory(
    path: PathLike,
    reader: Callable[..., Any] | None = None,
    sdt: DatetimeLike | None = None,
    edt: DatetimeLike | None = None,
    file_pattern: str = "{date}.csv",
    date_format: str = "%Y-%m-%d",
    trading_dates: Sequence[DatetimeLike] | None = None,
    engine: str = "polars",
    threads: int = 10,
    **kwargs: Any
) -> pd.DataFrame | pl.DataFrame:
    """
    Read and concatenate files from directory with optional date filtering.

    Args:
        path: Directory path containing files to read
        reader: Custom reader function (defaults to read_file)
        sdt: Start date (optional, requires edt)
        edt: End date (optional, requires sdt)
        file_pattern: File name pattern with {date} placeholder
        date_format: Date format string for parsing file names
        trading_dates: Pre-defined list of dates to use. If None, uses natural dates.
        engine: Data library to use ('polars' or 'pandas')
        threads: Number of parallel worker threads for reading files
        **kwargs: Additional arguments passed to reader function

    Returns:
        Concatenated DataFrame from all matching files

    Raises:
        ValueError: If engine is invalid or date parameters are inconsistent
        RuntimeError: If no files found or reading fails

    Time Complexity: O(n*m), where n is number of files and m is average file size
    Space Complexity: O(n*m) for loading all data into memory

    Examples:
        >>> # Read all CSV files in directory
        >>> df = read_directory('/data/market')

        >>> # Read files for specific date range (natural days)
        >>> df = read_directory('/data/market', sdt='2024-01-01', edt='2024-01-31')

        >>> # Read files for specific trading dates
        >>> trading_days = [pd.Timestamp('2024-01-02'), pd.Timestamp('2024-01-03')]
        >>> df = read_directory('/data/market', sdt='2024-01-01', edt='2024-01-31',
        ...                     trading_dates=trading_days)
    """
    if engine not in ("polars", "pandas"):
        raise ValueError("engine must be either 'polars' or 'pandas'")

    reader = reader or read_file
    base_path = Path(path)

    if not base_path.exists():
        raise FileNotFoundError(f"Directory not found: {path}")

    # Get file list
    if sdt is not None and edt is not None:
        files = _get_formatted_files(
            sdt, edt, base_path, file_pattern, date_format, trading_dates
        )
    else:
        files = get_files(base_path)
        if not files:
            log.warning(f"No files found in {base_path}")
            return pl.DataFrame() if engine == "polars" else pd.DataFrame()

    log.info(f"Starting parallel read of {len(files)} files with {threads} threads")

    # Parallel read files
    def _read_file(f: Path) -> pd.DataFrame | pl.DataFrame:
        try:
            if reader is read_file:
                return reader(f, engine=engine, **kwargs)
            return reader(f, **kwargs)
        except Exception as e:  # pylint: disable=broad-exception-caught
            log.error(f"Failed to read {f.name}: {e}")
            return pl.DataFrame() if engine == "polars" else pd.DataFrame()

    with ThreadPoolExecutor(max_workers=threads) as executor:
        results = list(executor.map(_read_file, files))

    # Remove empty DataFrames
    results = [df for df in results if df.shape[0] > 0]

    if not results:
        log.warning("No valid data read from any files")
        return pl.DataFrame() if engine == "polars" else pd.DataFrame()

    log.info(f"Successfully read {len(results)} files, concatenating...")

    # Concatenate results
    try:
        concatenated = (
            pl.concat(results, how="vertical_relaxed")  # type: ignore[arg-type]
            if engine == "polars"
            else pd.concat(results, ignore_index=True)  # type: ignore[arg-type]
        )
        log.info(f"Concatenated shape: {concatenated.shape}")
        return concatenated
    except Exception as e:
        raise RuntimeError(f"Failed to concatenate results: {e}") from e
