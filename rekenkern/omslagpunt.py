"""Print de omslagpunten ZZP <-> DGA en de optimale route per jaar.

    python3 omslagpunt.py
    python3 omslagpunt.py --jaar 2025 --geen-zvw
"""

from __future__ import annotations

import argparse

from belastingkern.optimalisatie import bepaal_optimale_route, omslagpunten


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--jaar", type=int, nargs="+", default=[2025, 2026])
    ap.add_argument("--geen-zvw", action="store_true")
    args = ap.parse_args()

    incl = not args.geen_zvw
    for jaar in args.jaar:
        route = bepaal_optimale_route(jaar, inclusief_zvw=incl)
        print(route.advies())
        kaal = omslagpunten("zzp", "dga", jaar, inclusief_zvw=False)
        met = omslagpunten("zzp", "dga", jaar, inclusief_zvw=True)

        def fmt(punten: list[float]) -> str:
            return ", ".join(f"€ {p:,.0f}".replace(",", ".") for p in punten) or "geen"

        print(f"  omslagpunten kaal     : {fmt(kaal)}")
        print(f"  omslagpunten incl Zvw : {fmt(met)}")
        print()


if __name__ == "__main__":
    main()
