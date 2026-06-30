"""Kleine CLI om een scenario door te rekenen.

Voorbeeld:
    python cli.py --jaar 2026 --loon 45000 --woz 350000 --rente 6000 \
                  --banktegoeden 80000

Bedoeld als rooktest/demonstratie; het echte invullen gaat later via het dashboard.
"""

from __future__ import annotations

import argparse

from belastingkern import (
    Persoon,
    EigenWoning,
    Box3Vermogen,
    Onderneming,
    bereken_persoon,
)


def main() -> None:
    ap = argparse.ArgumentParser(description="Reken een box 1/3-scenario door.")
    ap.add_argument("--jaar", type=int, default=2026)
    ap.add_argument("--naam", default="persoon")
    ap.add_argument("--aow", action="store_true", help="AOW-gerechtigd")
    ap.add_argument("--loon", type=float, default=0.0, help="loon tegenwoordige arbeid")
    ap.add_argument("--pensioen", type=float, default=0.0, help="AOW/pensioen/uitkering")
    ap.add_argument("--winst", type=float, default=0.0,
                    help="winst uit onderneming (volledige IB-ondernemerroute)")
    ap.add_argument("--urencriterium", action="store_true",
                    help="voldoet aan urencriterium (zelfstandigenaftrek)")
    ap.add_argument("--starter", action="store_true", help="recht op startersaftrek")
    ap.add_argument("--aftrek", type=float, default=0.0, help="aftrekposten box 1")
    ap.add_argument("--woz", type=float, default=0.0)
    ap.add_argument("--rente", type=float, default=0.0, help="hypotheekrente")
    ap.add_argument("--banktegoeden", type=float, default=0.0)
    ap.add_argument("--overige-bezittingen", type=float, default=0.0)
    ap.add_argument("--schulden", type=float, default=0.0)
    ap.add_argument("--partner", action="store_true", help="heeft fiscale partner")
    ap.add_argument("--kind-leeftijd", type=int, default=None)
    args = ap.parse_args()

    persoon = Persoon(
        naam=args.naam,
        aow_gerechtigd=args.aow,
        loon=args.loon,
        uitkering_pensioen=args.pensioen,
        onderneming=(
            Onderneming(
                winst=args.winst,
                voldoet_urencriterium=args.urencriterium,
                starter=args.starter,
            )
            if args.winst
            else None
        ),
        aftrekposten_box1=args.aftrek,
        eigen_woning=EigenWoning(
            woz_waarde=args.woz, betaalde_hypotheekrente=args.rente
        ),
        box3=Box3Vermogen(
            banktegoeden=args.banktegoeden,
            overige_bezittingen=args.overige_bezittingen,
            schulden=args.schulden,
        ),
        heeft_fiscale_partner=args.partner,
        jongste_kind_leeftijd=args.kind_leeftijd,
    )

    resultaat = bereken_persoon(persoon, args.jaar)
    print(resultaat.samenvatting())


if __name__ == "__main__":
    main()
