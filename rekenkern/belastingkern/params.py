"""Laden van de jaar-parameters uit params/<jaar>.json."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

_PARAMS_DIR = Path(__file__).resolve().parent.parent / "params"


@dataclass
class Params:
    """Dunne wrapper rond het params-dict met handige toegang."""

    jaar: int
    data: dict[str, Any]

    def __getitem__(self, key: str) -> Any:
        return self.data[key]

    @property
    def box1(self) -> dict[str, Any]:
        return self.data["box1"]

    @property
    def heffingskortingen(self) -> dict[str, Any]:
        return self.data["heffingskortingen"]

    @property
    def box3(self) -> dict[str, Any]:
        return self.data["box3"]


def laad_params(jaar: int) -> Params:
    pad = _PARAMS_DIR / f"{jaar}.json"
    if not pad.exists():
        beschikbaar = sorted(p.stem for p in _PARAMS_DIR.glob("*.json"))
        raise ValueError(
            f"Geen parameters voor jaar {jaar}. Beschikbaar: {beschikbaar}"
        )
    with pad.open(encoding="utf-8") as f:
        data = json.load(f)
    return Params(jaar=jaar, data=data)
