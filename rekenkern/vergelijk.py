"""Print de rechtsvormvergelijking (werknemer / ZZP / DGA) over een reeks inkomens.

    python3 vergelijk.py --jaar 2026
    python3 vergelijk.py --jaar 2025 --bedragen 30000 50000 75000 100000 150000 200000
"""

from __future__ import annotations

import argparse

from belastingkern.vergelijking import tabel


def main() -> None:
    ap = argparse.ArgumentParser(description="Rechtsvormvergelijking belastingdruk.")
    ap.add_argument("--jaar", type=int, default=2026)
    ap.add_argument(
        "--bedragen",
        type=float,
        nargs="+",
        default=[30000, 50000, 75000, 100000, 150000, 200000, 300000],
    )
    ap.add_argument(
        "--geen-urencriterium",
        action="store_true",
        help="ZZP zonder zelfstandigenaftrek (voldoet niet aan urencriterium)",
    )
    ap.add_argument("--geen-zvw", action="store_true", help="Zvw buiten beschouwing laten")
    ap.add_argument("--geen-wnv", action="store_true", help="WW/WIA buiten beschouwing laten")
    ap.add_argument(
        "--metric", choices=["belasting", "wig"], default="belasting",
        help="belasting = IB/Vpb/box2 + Zvw; wig = inclusief WW/WIA-premie",
    )
    ap.add_argument(
        "--pensioen", type=float, default=0.0,
        help="pensioen-equivalent als fractie van V (bv. 0.15)",
    )
    args = ap.parse_args()
    print(
        tabel(
            args.bedragen,
            args.jaar,
            urencriterium=not args.geen_urencriterium,
            inclusief_zvw=not args.geen_zvw,
            inclusief_wnv=not args.geen_wnv,
            pensioen_pct=args.pensioen,
            metric=args.metric,
        )
    )


if __name__ == "__main__":
    main()
