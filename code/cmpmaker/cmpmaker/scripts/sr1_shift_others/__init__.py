from __future__ import annotations

from cmpmaker.runner.resolver import resolve_family_export


def __getattr__(name: str):
    return resolve_family_export(__name__, __file__, name)