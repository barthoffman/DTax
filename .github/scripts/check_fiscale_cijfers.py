#!/usr/bin/env python3
"""Detecteer of de fiscale cijfers voor het volgende belastingjaar bijgewerkt moeten worden.

Draait in de GitHub Action `fiscale-cijfers-check` (nov–feb). Logica:
- doeljaar = lopend jaar + 1 (in nov/dec) of lopend jaar (in jan/feb);
- al bijgewerkt? → `rekenkern/params/<doeljaar>.json` bestaat al → geen actie;
- anders: best-effort check of de bronnen (fisin<doeljaar>) al live zijn, en zet outputs zodat
  de workflow één issue opent met de checklist.

Pure stdlib (geen dependencies), faalt nooit op een netwerkfout. Testbaar via env:
  CHECK_DATE=2026-12-01  → forceer de "datum"
  SKIP_PROBE=1           → sla de netwerk-check over
"""
from __future__ import annotations

import datetime
import os
import pathlib
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[2]
UA = {"User-Agent": "Mozilla/5.0 (DTax update-check)"}


def _now() -> datetime.date:
    iso = os.environ.get("CHECK_DATE")
    return datetime.date.fromisoformat(iso) if iso else datetime.date.today()


def _doeljaar(d: datetime.date) -> int:
    # nov/dec: volgend jaar; jan/feb: het zojuist begonnen jaar.
    return d.year + 1 if d.month >= 11 else d.year


def _url_live(url: str, timeout: int = 15):
    if os.environ.get("SKIP_PROBE"):
        return None
    try:
        req = urllib.request.Request(url, headers=UA, method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as r:  # noqa: S310 (vaste https-bron)
            return 200 <= r.status < 300
    except Exception:
        return None  # onbekend → handmatig checken


def _mark(v) -> str:
    return "✅ live" if v is True else ("⏳ nog niet" if v is False else "❓ onbekend (handmatig checken)")


def main() -> None:
    target = _doeljaar(_now())
    params = ROOT / "rekenkern" / "params" / f"{target}.json"
    al_bijgewerkt = params.exists()
    needs = not al_bijgewerkt

    fisin = (f"https://www.belastingdienst.nl/wps/wcm/connect/fisin/"
             f"fisin{target}/uitgaven_voor_inkomensvoorzieningen")
    fisin_live = _url_live(fisin)

    body = f"""De jaarlijkse fiscale-cijfers-check meldt: **belastingjaar {target}** staat nog \
niet in de repo (`rekenkern/params/{target}.json` ontbreekt).

**Bronstatus (best-effort):**
- `fisin{target}` (Belastingdienst fiscale cijfers): {_mark(fisin_live)} — {fisin}
- Bijstellingsregeling directe belastingen {target}: \
<https://zoek.officielebekendmakingen.nl/resultaten?q=%22Bijstellingsregeling+directe+belastingen%22>
- Nieuwsbrief Loonheffingen: \
<https://www.belastingdienst.nl/wps/wcm/connect/bldcontentnl/themaoverstijgend/brochures_en_publicaties/nieuwsbrief-loonheffingen>

**Actie:** zodra de bronnen live zijn, start een Claude-sessie en zeg *"update naar {target}"*. \
Zie de update-kalender in `bronnen/bronregister.md`. Let op de **voorlopige box 3-forfaits** \
(banktegoeden/schulden) — die worden pas begin {target + 1} definitief vastgesteld.

_Automatisch geopend door de workflow `fiscale-cijfers-check`._
"""

    gh_out = os.environ.get("GITHUB_OUTPUT")
    if gh_out:
        with open(gh_out, "a", encoding="utf-8") as f:
            f.write(f"needs_update={'true' if needs else 'false'}\n")
            f.write(f"target_year={target}\n")
    pathlib.Path("issue_body.md").write_text(body, encoding="utf-8")
    print(f"target={target} al_bijgewerkt={al_bijgewerkt} "
          f"fisin_live={fisin_live} needs_update={needs}")


if __name__ == "__main__":
    main()
