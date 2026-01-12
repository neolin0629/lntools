from __future__ import annotations

import argparse
from typing import Dict, Any


class CLIError(Exception):
    """Custom exception for CLI-related errors."""
    def __init__(self, message: str | None = None, error_code: int | None = None):
        self.message = message or "An error occurred in CLI"
        self.error_code = error_code
        super().__init__(self.message)

    def __str__(self):
        if self.error_code:
            return f"[Error {self.error_code}] {self.message}"
        return self.message


class CLI:
    """
    A class to simplify the use of argparse for command line interfaces.

    Attributes:
        parser (argparse.ArgumentParser): The argument parser instance.
    """

    def __init__(self) -> None:
        """
        Initialize the argument parser.
        """
        self.parser = argparse.ArgumentParser(description="Command-Line Interface Utility")

    def add(self, *args, **kwargs) -> None:
        """Add an argument to the parser.

        Args
        ----------
        *args: Argument names and flags.
        **kwargs: Keyword arguments for various options like 'nargs', 'type', 'choices', etc.

        Notes
        ----------
        ``action
            store:        Stores the input value to the Namespace object
            store_const:  Stores a constant value when the option is specified
            store_true:   Stores the True Boolean value when the option is specified and stores False otherwise
            store_false:  Stores False when the option is specified and stores True otherwise
            append:       Appends the current value to a list each time the option is provided
            append_const: Appends a constant value to a list each time the option is provided
            count:        Stores the number of times the current option has been provided
            version:      Shows the app's version and terminates the execution

        ``nargs
            ?  Accepts a single input value, which can be optional
            *  Takes zero or more input values, which will be stored in a list
            +  Takes one or more input values, which will be stored in a list

        ``choices
            Specifying a List of Allowed Input Values

        """
        try:
            self.parser.add_argument(*args, **kwargs)
        except argparse.ArgumentError as e:
            raise CLIError(f"Failed to add argument: {e}") from e

    def get(self, allow_unknown: bool = False) -> Dict[str, Any]:
        """Parse command line arguments and return as dictionary.

        Args:
            allow_unknown: Whether to allow unknown arguments.
                If True, unknown args are included under 'unknown' key.
                If False, raises error on unknown arguments.

        Returns:
            Dictionary of parsed arguments

        Raises:
            CLIError: On parsing errors
            SystemExit: On help/version requests

        Examples:
            >>> args = cli.get()
            >>> name = args["name"]
            >>> verbose = args["verbose"]
        """
        try:
            if allow_unknown:
                args, unknown = self.parser.parse_known_args()
                result = vars(args)
                result['unknown'] = unknown
                return result
            return vars(self.parser.parse_args())
        except (argparse.ArgumentError, SystemExit) as e:
            # Let help/version actions exit
            if isinstance(e, SystemExit) and e.code == 0:
                raise
            raise CLIError(f"Failed to parse arguments: {e}") from e
