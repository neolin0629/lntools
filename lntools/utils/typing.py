from datetime import datetime
from pathlib import Path
from typing import TypeAlias

import numpy as np
import pandas as pd
import polars as pl

# ==========================================
# Data Structure Types
# ==========================================

# Lists, Arrays, and Series
ArrayLike: TypeAlias = list | np.ndarray | pd.Series | pl.Series
SeriesLike: TypeAlias = pd.Series | pl.Series

# DataFrames (Eager and Lazy)
DataFrameLike: TypeAlias = pd.DataFrame | pl.DataFrame | pl.LazyFrame

# ==========================================
# Time & Date Types
# ==========================================

# Flexible datetime input:
# - Timestamp/datetime objects
# - int (YYYYMMDD or Epoch)
# - float (Epoch)
# - str ("20230420", "today")
DatetimeLike: TypeAlias = pd.Timestamp | datetime | int | float | str

# Polars specific temporal types (Dtypes)
PolarsDate: TypeAlias = pl.Datetime | pl.Date | pl.Time

# ==========================================
# File System Types
# ==========================================

PathLike: TypeAlias = str | Path
