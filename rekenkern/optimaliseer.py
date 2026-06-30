"""Optimalisatieadvies voor één situatie.

    python3 optimaliseer.py --waarde 150000 --vermogen 500000 --rendement 0.02
    python3 optimaliseer.py --waarde 40000 --kinderen 2 --partner
"""

from __future__ import annotations

import argparse

from belastingkern import Situatie, Huishoudprofiel, optimaliseer


def main() -> None:
    ap = argparse.ArgumentParser(description="Fiscaal optimalisatieadvies.")
    ap.add_argument("--jaar", type=int, default=2026)
    ap.add_argument("--waarde", type=float, required=True, help="economische waarde V per jaar")
    ap.add_argument("--vermogen", type=float, default=0.0, help="priv/box 3-vermogen")
    ap.add_argument("--rendement", type=float, default=0.06, help="verwacht werkelijk rendement")
    ap.add_argument("--partner", action="store_true", help="heeft toeslagpartner")
    ap.add_argument("--kinderen", type=int, default=0)
    ap.add_argument("--geen-urencriterium", action="store_true")
    args = ap.parse_args()

    profiel = None
    if args.partner or args.kinderen:
        profiel = Huishoudprofiel(
            heeft_toeslagpartner=args.partner, aantal_kinderen=args.kinderen
        )

    situatie = Situatie(
        economische_waarde=args.waarde,
        profiel=profiel,
        prive_vermogen=args.vermogen,
        verwacht_rendement=args.rendement,
        urencriterium=not args.geen_urencriterium,
    )
    print(optimaliseer(situatie, args.jaar).rapport())


if __name__ == "__main__":
    main()
