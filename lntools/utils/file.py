#
# file.py
# @author Linnan
# @description Describing Data Source of `File`
# @created 2023-04-14T13:59:36.519Z+08:00
# @last-modified 2023-09-10T11:40:36.955Z+08:00
#
from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Callable, Optional, Any, Union

from lntools.utils.filesystem import read_file


class File:
    """Metadata and operations for local files.

    Args:
        path: Path to the local file.
        reader: Optional custom read function for the file.

    Attributes:
        path: Absolute path to the file
        directory: Directory containing the file
        basename: File name with extension
        filename: File name without extension
        extension: File extension including dot

    Raises:
        FileNotFoundError: If the file does not exist
        TypeError: If path is not a string
    """

    def __init__(self, path: Union[str, Path]) -> None:
        self.path = str(Path(path).resolve())
        if not isinstance(self.path, str):
            raise TypeError(f"Path must be string or Path, got {type(path)}")
        if not os.path.isfile(self.path):
            raise FileNotFoundError(f"File not found: {self.path}")

        self._path = Path(self.path)
        self.directory = str(self._path.parent)
        self.basename = self._path.name
        self.filename = self._path.stem
        self.extension = self._path.suffix

    @property
    def is_(self) -> bool:
        return os.path.isfile(self.path)

    def read(self,
             reader: Optional[Callable] = None,
             df_lib: Optional[str] = None,
             **kwargs: Any) -> Any:
        """Read the file content.

        Args:
            reader: Optional custom read function
            df_lib: Data frame library to use ('pandas', 'polars', 'numpy', 'base')
            **kwargs: Additional arguments passed to the reader

        Returns:
            File contents in the format specified by the reader
        """
        if reader:
            return reader(self.path, **kwargs)
        return read_file(self.path, df_lib=df_lib, **kwargs)

    def mv(self, dst: Union[str, Path]) -> None:
        """Move file to destination.

        Args:
            dst: Destination directory path

        Raises:
            OSError: If directory creation fails
        """
        dst_path = Path(dst)
        if not dst_path.exists():
            dst_path.mkdir(parents=True, exist_ok=True)
        shutil.move(self.path, str(dst_path))
        self.path = str(dst_path / self.basename)
        self._path = Path(self.path)

    def cp(self, dst: Union[str, Path]) -> None:
        """Copy file to destination.

        Args:
            dst: Destination directory path

        Raises:
            OSError: If directory creation fails
        """
        dst_path = Path(dst)
        if not dst_path.exists():
            dst_path.mkdir(parents=True, exist_ok=True)
        shutil.copy2(self.path, str(dst_path))

    def rm(self) -> None:
        """Remove the file.

        Raises:
            OSError: If file deletion fails
        """
        try:
            os.remove(self.path)
        except OSError as e:
            raise OSError(f"Failed to remove file {self.path}: {e}") from e

    @property
    def help(self) -> str:
        """Return help text with usage examples."""
        return """
        File Operations Helper

        Properties:
            path: str - Absolute file path
            directory: str - Parent directory path
            basename: str - File name with extension
            filename: str - File name without extension
            extension: str - File extension
            exists: bool - Whether file exists

        Methods:
            read([reader, df_lib]) -> Any: Read file contents
            cp(dst: str) -> None: Copy file to destination
            mv(dst: str) -> None: Move file to destination
            rm() -> None: Remove file

        Example:
            f = File("path/to/data.parquet")
            data = f.read(df_lib="polars")
            f.cp("backup/")
            f.mv("archive/")
            f.rm()
        """


if __name__ == '__main__':
    FILE_PATH = "test.txt"
    with open(FILE_PATH, "w", encoding="utf-8") as f:
        f.write("test content")

    f = File(FILE_PATH)
    print(f"{f.path}, {f.basename}, {f.filename}, {f.extension}")
    text = f.read()
    print(text)
    f.rm()
