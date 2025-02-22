"Base Metadata Class"

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Union

from lntools.utils.log import Logger

log = Logger('lntools.utils.columns')


@dataclass
class Columns:
    """Base Metadata Class for handling column metadata.

    Parameters
    ----------
    columns : Optional[Union[str, List[str]]]
        Required columns, by default all columns, pass ``[]`` for no column.
    """
    columns: Optional[Union[str, List[str]]] = None
    _all_columns: tuple = field(default_factory=tuple)
    _column_map: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        # construct cache
        self._all_columns = self.get_columns()
        self._column_map = self.column_map
        self.columns = filter_columns(self.columns, self._all_columns)

    @staticmethod
    def get_columns() -> tuple:
        "Get All Available Column Names"
        return ()

    @property
    def column_map(self) -> Dict[str, str]:
        "Get defined column map"
        return {}

    # def _construct_sql(
    #   self, table_name: str, where: List[str], select: Optional[Union[List[str], Tuple[str]]] = None
    # ) -> str:
    #     if select is None:
    #         cols = {c: self._column_map[c] for c in self.columns}
    #         select = tuple(f"{v} AS {k}" for k, v in cols.items())
    #     sql = f"SELECT {', '.join(select)} FROM {table_name} where {' AND '.join(where)}"
    #     return sql


def filter_columns(
    required: Optional[Union[str, List[str]]],
    available: Union[tuple, List[str]]
) -> List[str]:
    """
    Filter and return columns from 'available' based on 'required' specification.

    Args:
        required (None | str | List[str]): Specification of required columns.
        `None` means all available columns, `[]` means no column at all.
        available (tuple | List[str]): List or tuple of available columns.

    Returns:
        List[str]: A list of columns based on the 'required' specification.

    Raises:
        ValueError: If any required columns are not available or none of the required columns are available.
    """
    if required is None:
        return list(available)
    if required == []:
        return []

    # Ensure 'required' is a list
    if isinstance(required, str):
        required = [required]

    # Validate 'required' to be a list of strings
    if not all(isinstance(col, str) for col in required):
        raise TypeError("All items in 'required' should be strings.")

    valid_columns = [col for col in required if col in available]
    if not valid_columns:
        raise ValueError(f"No required columns are available: {required}")

    if len(valid_columns) != len(required):
        unavailable = set(required) - set(available)
        from lntools.utils.human import lists
        log.error(f"Ignore unavailable columns: {lists(unavailable)}")

    return valid_columns
