"""Presenteerbaar rapport: invoer → motor → gestructureerd, herleidbaar resultaat.

Bedoeld om voor te leggen aan een boekhouder of (met onderbouwing) aan de Belastingdienst.
Het rapport is **formaat-agnostisch** (een dict); render het naar PDF/HTML/print in een
losse laag. `rapport_markdown()` is één voorbeeldrendering.

Het rapport bevat naast de uitkomst de **wettelijke grondslag** (wetsartikel + bron-ID +
versie/geldigheidsdatum, uit `bronnen/bronregister.md`) en de **aannames/benaderingen**,
zodat alles controleerbaar en herleidbaar is.
"""

from __future__ import annotations

import datetime

from .optimalisatiemotor import Situatie, optimaliseer
from .params import laad_params
from .vergelijking import vergelijk

REKENKERN_VERSIE = "0.3 (2026-06)"

# Curatie wetsartikel + bron-ID + versie per onderdeel (zie bronregister voor URL's).
WETTELIJKE_GRONDSLAG = [
    {"onderwerp": "Tarief box 1 (schijven, AOW)", "wetsartikel": "art. 2.10 / 2.10a Wet IB 2001", "bron_id": "B1-tarief", "versie": "2026-01-01"},
    {"onderwerp": "Eigen woning (EWF, rente, Hillen)", "wetsartikel": "art. 3.112 / 3.120 / 3.123a Wet IB 2001", "bron_id": "B1-ewf / B1-hra / B1-hillen", "versie": "2026-01-01"},
    {"onderwerp": "Heffingskortingen", "wetsartikel": "art. 8.10–8.18 Wet IB 2001", "bron_id": "HK-01", "versie": "2026-01-01"},
    {"onderwerp": "Ondernemersaftrek + MKB-winstvrijstelling", "wetsartikel": "art. 3.76 / 3.79a Wet IB 2001", "bron_id": "OND-WET-3.76 / OND-WET-3.79a", "versie": "2026-02-21"},
    {"onderwerp": "Box 2 (aanmerkelijk belang)", "wetsartikel": "art. 2.12 Wet IB 2001", "bron_id": "DGA-03 / DGA-04", "versie": "2026-01-01"},
    {"onderwerp": "Vennootschapsbelasting", "wetsartikel": "art. 22 Wet Vpb 1969", "bron_id": "DGA-01 / DGA-02", "versie": "2026-01-01"},
    {"onderwerp": "Gebruikelijk loon DGA", "wetsartikel": "art. 12a Wet LB 1964", "bron_id": "DGA-06 / DGA-07", "versie": "2026"},
    {"onderwerp": "Box 3 + tegenbewijs (werkelijk rendement)", "wetsartikel": "art. 5.2 / 2.13 Wet IB 2001; Wet tegenbewijsregeling box 3", "bron_id": "B3-01 / B3-09", "versie": "2026-01-01"},
    {"onderwerp": "Zvw inkomensafhankelijke bijdrage", "wetsartikel": "Zorgverzekeringswet", "bron_id": "ZVW-SVM2026 / ZVW-BD", "versie": "2026"},
    {"onderwerp": "Premies werknemersverzekeringen (WW/WIA)", "wetsartikel": "Wfsv", "bron_id": "WV-01 / WV-03", "versie": "2026"},
    {"onderwerp": "Toeslagen (toetsingsinkomen, vermogenstoets)", "wetsartikel": "Awir + Wet zorgtoeslag / huurtoeslag / kindgebonden budget / kinderopvang", "bron_id": "TOE-AWIR-2026 e.v.", "versie": "2026-01-01"},
    {"onderwerp": "Jaarruimte lijfrente", "wetsartikel": "art. 3.127 Wet IB 2001", "bron_id": "PEN-01", "versie": "2026-01-01"},
    {"onderwerp": "Partnertoerekening", "wetsartikel": "art. 2.17 Wet IB 2001", "bron_id": "AFT-WET-217", "versie": "2026"},
]

DISCLAIMER = (
    "Dit rapport is een schatting op basis van de ingevoerde gegevens en de op de "
    "versiedatum geldende parameters; het is geen belastingaangifte en geen fiscaal advies. "
    "Met (*) gemarkeerde punten berusten op aannames of benaderingen en lenen zich voor een "
    "onderbouwd standpunt richting de Belastingdienst. Laat het vóór indiening toetsen door "
    "een boekhouder/fiscalist."
)


def _profiel_dict(s: Situatie) -> dict | None:
    if s.profiel is None:
        return None
    p = s.profiel
    return {
        "toeslagpartner": p.heeft_toeslagpartner,
        "partner_inkomen": p.partner_inkomen,
        "aantal_kinderen": p.aantal_kinderen,
        "rekenhuur": p.rekenhuur,
        "box3_vermogen_1jan": p.box3_vermogen_1jan,
    }


def bouw_rapport(situatie: Situatie, jaar: int, *, datum: str | None = None) -> dict:
    advies = optimaliseer(situatie, jaar)
    verg = vergelijk(
        situatie.economische_waarde, jaar,
        urencriterium=situatie.urencriterium, profiel=situatie.profiel,
    )

    aannames: list[str] = list(advies.tips)
    for vorm in verg.vormen:
        if vorm.toeslagen is not None:
            aannames.extend(vorm.toeslagen.waarschuwingen)
    aannames.append("Gebruikelijk loon DGA = normbedrag (solo-DGA-aanname).")
    aannames.append("Box 2-dividend verondersteld volledig uitgekeerd (geen uitstel gemodelleerd).")
    aannames.append(
        "Vaste administratie-/boekhoudkosten zijn indicatief (markt) en instelbaar; "
        "eenmalige oprichtingskosten BV (~€ 400-800) zijn niet meegenomen."
    )
    # Ontdubbelen, volgorde behouden
    aannames = list(dict.fromkeys(aannames))

    return {
        "metadata": {
            "titel": "Fiscaal optimalisatierapport",
            "belastingjaar": jaar,
            "gegenereerd_op": datum or datetime.date.today().isoformat(),
            "rekenkern_versie": REKENKERN_VERSIE,
        },
        "invoer": {
            "economische_waarde": situatie.economische_waarde,
            "prive_vermogen": situatie.prive_vermogen,
            "verwacht_rendement": situatie.verwacht_rendement,
            "urencriterium": situatie.urencriterium,
            "tegenbewijs_box3": situatie.tegenbewijs_box3,
            "profiel": _profiel_dict(situatie),
        },
        "advies": {
            "beste_route": advies.beste.naam,
            "besparing_vs_slechtste": advies.besparing_vs_slechtste,
            "break_even_rendement": advies.break_even_rendement,
            "jaarruimte_lijfrente": advies.jaarruimte_lijfrente,
            "routes": [
                {
                    "naam": u.naam,
                    "inkomen_netto": u.inkomen_netto,
                    "vermogen_last": u.vermogen_last,
                    "totaal_netto": u.totaal_netto,
                    "toelichting": u.toelichting,
                }
                for u in sorted(advies.uitkomsten, key=lambda x: -x.totaal_netto)
            ],
        },
        "wettelijke_grondslag": WETTELIJKE_GRONDSLAG,
        "aannames_en_benaderingen": aannames,
        "disclaimer": DISCLAIMER,
    }


def rapport_markdown(rapport: dict) -> str:
    m = rapport["metadata"]
    a = rapport["advies"]
    regels = [
        f"# {m['titel']} — {m['belastingjaar']}",
        f"_Gegenereerd op {m['gegenereerd_op']} · rekenkern {m['rekenkern_versie']}_",
        "",
        "## Advies",
        f"**Beste route: {a['beste_route'].upper()}** — € {a['besparing_vs_slechtste']:,.0f} "
        f"per jaar voordeliger dan de duurste.".replace(",", "."),
        "",
        "| Route | Inkomen netto | Vermogenslast | Totaal netto |",
        "|---|---|---|---|",
    ]
    for r in a["routes"]:
        regels.append(
            f"| {r['naam']} | € {r['inkomen_netto']:,.0f} | € {r['vermogen_last']:,.0f} | "
            f"€ {r['totaal_netto']:,.0f} |".replace(",", ".")
        )
    if a["jaarruimte_lijfrente"]:
        regels.append("")
        regels.append(f"Jaarruimte lijfrente (art. 3.127): € {a['jaarruimte_lijfrente']:,.0f}".replace(",", "."))

    regels += ["", "## Wettelijke grondslag", "", "| Onderwerp | Wetsartikel | Bron | Versie |", "|---|---|---|---|"]
    for g in rapport["wettelijke_grondslag"]:
        regels.append(f"| {g['onderwerp']} | {g['wetsartikel']} | {g['bron_id']} | {g['versie']} |")

    regels += ["", "## Aannames en benaderingen (*)", ""]
    for x in rapport["aannames_en_benaderingen"]:
        regels.append(f"- {x}")

    regels += ["", "## Disclaimer", "", rapport["disclaimer"]]
    return "\n".join(regels)
