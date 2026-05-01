"""
Shadow Drive is deprecated — replaced by Irys in the hosted API layer.
This stub maintains interface compatibility for existing code.
"""
from __future__ import annotations
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .types import ShadowDriveConfig
    from .collection import SolVecCollection


async def _upload_snapshot(
    collection: "SolVecCollection",
    config: "ShadowDriveConfig",
) -> Optional[str]:
    return None


def schedule_snapshot(
    collection: "SolVecCollection",
    config: "ShadowDriveConfig",
) -> None:
    pass
