"""Internal typing for the integration's existing gate service response."""

from typing import TypedDict


class GateActionResult(TypedDict, total=False):
    """Fields consumed by button, switch and Assist callers."""

    success: bool
    error: str
