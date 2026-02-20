"""Output format definitions to avoid circular imports."""

from enum import Enum


class OutputFormat(str, Enum):
    """Output format options."""
    RICH = "rich"
    JSON = "json"
    PLAIN = "plain"


# Global state for output format
_output_format = OutputFormat.RICH


def set_output_format(fmt: OutputFormat):
    """Set the global output format."""
    global _output_format
    _output_format = fmt


def get_output_format() -> OutputFormat:
    """Get the current output format."""
    return _output_format
