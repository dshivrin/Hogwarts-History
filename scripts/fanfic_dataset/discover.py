from __future__ import annotations

from typing import Protocol

from .models import SourceRecord, WorkDiscovery


class PlatformAdapter(Protocol):
    def discover(
        self, html: str, canonical_url: str, source: SourceRecord
    ) -> WorkDiscovery:
        """Parse public work metadata and canonical chapter URLs without I/O."""
        ...


def adapter_for(source: SourceRecord) -> PlatformAdapter:
    if source.platform == "fanfiction.net":
        from .fanfiction_net import FanFictionNetAdapter

        return FanFictionNetAdapter()
    raise ValueError(f"unsupported platform: {source.platform}")
