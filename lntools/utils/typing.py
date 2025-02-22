from datetime import datetime
from pathlib import Path
from typing import Union

import numpy as np
import pandas as pd
import polars as pl

# Defining types for array-like and series-like data
ArrayLike = Union[list, np.ndarray, pd.Series, pl.Series]
SeriesLike = Union[pd.Series, pl.Series]

# Defining types for date and time-related data
DatetimeLike = Union[pd.Timestamp, int, float, str, datetime]
# Explanation of DatetimeLike possibilities:
# int: e.g., 20230420 (yearmonthday)
# float: e.g., 1681968801.5371664 (Unix timestamp)
# str: e.g., "20230420" or "today" (various string formats)

# Defining types for DataFrame structures
DataFrameLike = Union[pd.DataFrame, pl.DataFrame, pl.LazyFrame]

# Polars specific datetime types
PolarsDate = Union[pl.Datetime, pl.Date, pl.Time]

# Defining types for file path specifications
PathLike = Union[str, Path]
