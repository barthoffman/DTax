"""JSON HTTP-API over de rekenkern (dependency-vrij, Python stdlib).

Endpoints:
  GET  /health                 -> {"status": "ok"}
  GET  /jaren                  -> {"jaren": [2025, 2026]}
  POST /vergelijk              -> rechtsvormvergelijking (werknemer/ZZP/DGA)
  POST /optimaliseer           -> optimalisatieadvies (beste route incl. vermogen)

Het JSON-contract ontkoppelt de client; ruil `http.server` later in voor FastAPI
zonder het contract te wijzigen.

Starten:  python3 api.py   (default poort 8000)
Voorbeeld:
  curl -s localhost:8000/optimaliseer -d '{"economische_waarde":150000,"prive_vermogen":500000,"verwacht_rendement":0.015}'
"""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from belastingkern import (
    Situatie, Huishoudprofiel, optimaliseer,
    Persoon, EigenWoning, Box3Vermogen, Onderneming, bereken_persoon,
)
from belastingkern.vergelijking import Vorm, vergelijk
from belastingkern.toerekening import optimale_eigenwoning_verdeling
from belastingkern.rapport import bouw_rapport, rapport_markdown

_PARAMS_DIR = Path(__file__).resolve().parent / "params"
_CLIENT_HTML = Path(__file__).resolve().parent / "client" / "index.html"


# ---------- (de)serialisatie ----------

def _profiel_from_json(data: dict | None) -> Huishoudprofiel | None:
    if not data:
        return None
    return Huishoudprofiel(
        heeft_toeslagpartner=bool(data.get("heeft_toeslagpartner", False)),
        partner_inkomen=float(data.get("partner_inkomen", 0.0)),
        aantal_kinderen=int(data.get("aantal_kinderen", 0)),
        kinderen_12_15=int(data.get("kinderen_12_15", 0)),
        kinderen_16_17=int(data.get("kinderen_16_17", 0)),
        alleenstaande_ouder=bool(data.get("alleenstaande_ouder", False)),
        box3_vermogen_1jan=float(data.get("box3_vermogen_1jan", 0.0)),
        rekenhuur=(float(data["rekenhuur"]) if data.get("rekenhuur") else None),
        kinderopvang_soort=data.get("kinderopvang_soort") or None,
        kinderopvang_uren_per_maand=float(data.get("kinderopvang_uren_per_maand", 0.0)),
        kinderopvang_uurtarief=float(data.get("kinderopvang_uurtarief", 0.0)),
        kinderopvang_kinderen=int(data.get("kinderopvang_kinderen", 0)),
    )


def _vorm_to_json(v: Vorm) -> dict:
    d = {
        "naam": v.naam,
        "bruto": v.bruto,
        "inkomstenheffing": v.inkomstenheffing,
        "zvw": v.zvw,
        "werknemersverzekeringen": v.werknemersverzekeringen,
        "pensioen": v.pensioen,
        "verzamelinkomen": v.verzamelinkomen,
        "totale_belasting": v.totale_belasting,
        "totale_wig": v.totale_wig,
        "effectief_tarief": v.effectief_tarief,
        "effectief_wig": v.effectief_wig,
        "netto_besteedbaar": v.netto_besteedbaar,
        "netto_inclusief_toeslagen": v.netto_inclusief_toeslagen,
    }
    if v.toeslagen is not None:
        d["toeslagen"] = {
            "zorgtoeslag": v.toeslagen.zorgtoeslag,
            "kindgebonden_budget": v.toeslagen.kindgebonden_budget,
            "huurtoeslag": v.toeslagen.huurtoeslag,
            "kinderopvangtoeslag": v.toeslagen.kinderopvangtoeslag,
            "totaal": v.toeslagen.totaal,
        }
    return d


def _vergelijk_handler(body: dict) -> dict:
    jaar = int(body.get("jaar", 2026))
    v = vergelijk(
        float(body["economische_waarde"]) if "economische_waarde" in body else float(body["bruto"]),
        jaar,
        urencriterium=bool(body.get("urencriterium", True)),
        inclusief_zvw=bool(body.get("inclusief_zvw", True)),
        inclusief_wnv=bool(body.get("inclusief_wnv", True)),
        pensioen_pct=float(body.get("pensioen_pct", 0.0)),
        profiel=_profiel_from_json(body.get("profiel")),
    )
    return {
        "jaar": v.jaar,
        "bruto": v.bruto,
        "werknemer": _vorm_to_json(v.werknemer),
        "zzp": _vorm_to_json(v.zzp),
        "dga": _vorm_to_json(v.dga),
        "spreiding_pp": v.spreiding,
    }


def _situatie_uit_body(body: dict) -> tuple[Situatie, int]:
    jaar = int(body.get("jaar", 2026))
    situatie = Situatie(
        economische_waarde=float(body["economische_waarde"]),
        profiel=_profiel_from_json(body.get("profiel")),
        prive_vermogen=float(body.get("prive_vermogen", 0.0)),
        spaargeld=float(body.get("spaargeld", 0.0)),
        verwacht_rendement=float(body.get("verwacht_rendement", 0.06)),
        urencriterium=bool(body.get("urencriterium", True)),
        tegenbewijs_box3=bool(body.get("tegenbewijs_box3", True)),
        vaste_kosten=body.get("vaste_kosten"),
        oprichtingskosten=body.get("oprichtingskosten"),
        horizon_jaren=body.get("horizon_jaren"),
        gebruikelijk_loon=(float(body["gebruikelijk_loon"]) if body.get("gebruikelijk_loon") is not None else None),
    )
    return situatie, jaar


def _rapport_handler(body: dict) -> dict:
    situatie, jaar = _situatie_uit_body(body)
    rapport = bouw_rapport(situatie, jaar)
    # Formaat-agnostisch: gestructureerd + één voorbeeldrendering (markdown).
    if body.get("formaat") == "markdown":
        return {"formaat": "markdown", "inhoud": rapport_markdown(rapport)}
    return rapport


def _persoon_van(d: dict) -> tuple[Persoon, float]:
    ew = d.get("eigen_woning") or {}
    b3 = d.get("box3") or {}
    loon = float(d.get("loon", 0))                 # som van alle dienstverbanden
    pensioen = float(d.get("uitkering_pensioen", 0))
    winst = float(d.get("winst", 0))
    row = float(d.get("resultaat_overige_werkzaamheden", 0))
    persoon = Persoon(
        loon=loon, uitkering_pensioen=pensioen, resultaat_overige_werkzaamheden=row,
        onderneming=(Onderneming(winst=winst, voldoet_urencriterium=bool(d.get("urencriterium", False)))
                     if winst else None),
        aftrekposten_box1=float(d.get("aftrekposten_box1", 0)),
        aow_gerechtigd=bool(d.get("aow_gerechtigd", False)),
        eigen_woning=EigenWoning(
            woz_waarde=float(ew.get("woz_waarde", 0)),
            betaalde_hypotheekrente=float(ew.get("betaalde_hypotheekrente", 0)),
        ),
        box3=Box3Vermogen(
            banktegoeden=float(b3.get("banktegoeden", 0)),
            overige_bezittingen=float(b3.get("overige_bezittingen", 0)),
            schulden=float(b3.get("schulden", 0)),
        ),
    )
    return persoon, round(loon + pensioen + winst + row, 2)


def _resultaat_dict(d: dict, jaar: int) -> dict:
    persoon, bruto = _persoon_van(d)
    r = bereken_persoon(persoon, jaar)
    k = r.kortingen
    return {
        "jaar": r.jaar, "bruto_inkomen": bruto,
        "belastbaar_box1": r.box1.belastbaar_inkomen,
        "heffing_box1": r.box1.belasting_en_premies,
        "heffing_box3": r.box3.belasting,
        "box3": {
            "grondslag": r.box3.rendementsgrondslag,
            "heffingvrij": round(r.box3.rendementsgrondslag - r.box3.grondslag_na_heffingvrij, 2),
            "effectief_rendementspercentage": r.box3.effectief_rendementspercentage,
            "belasting": r.box3.belasting,
            "tegenbewijs": r.box3.tegenbewijs_toegepast,
        },
        "verzamelinkomen": r.verzamelinkomen,
        "heffingskortingen": k.totaal,
        "kortingen": {"algemene": k.algemene, "arbeids": k.arbeids, "iack": k.iack,
                      "ouderen": k.ouderen, "jonggehandicapten": k.jonggehandicapten},
        "verzilverd": r.verzilverde_korting, "verdampt": r.verdampte_korting,
        "te_betalen": r.te_betalen, "netto": round(bruto - r.te_betalen, 2),
        "gemiddeld_tarief": round(r.te_betalen / bruto, 4) if bruto else 0.0,
        "waarschuwingen": r.waarschuwingen,
    }


def _bereken_handler(body: dict) -> dict:
    """Werkelijke situatie: meerdere inkomstenbronnen samen in één box 1-berekening.
    Optioneel een `partner` (zelfde velden) → huishoudtotalen."""
    jaar = int(body.get("jaar", 2026))
    out = _resultaat_dict(body, jaar)
    partner = body.get("partner")
    if partner:
        pres = _resultaat_dict(partner, jaar)
        out["partner"] = pres
        out["huishouden"] = {
            "bruto": round(out["bruto_inkomen"] + pres["bruto_inkomen"], 2),
            "te_betalen": round(out["te_betalen"] + pres["te_betalen"], 2),
            "netto": round(out["netto"] + pres["netto"], 2),
        }
    return out


def _advies_handler(body: dict) -> dict:
    from belastingkern.advies import optimalisatie_advies
    ew = body.get("eigen_woning") or {}
    b3 = body.get("box3") or {}
    r = optimalisatie_advies(
        int(body.get("jaar", 2026)),
        loon=float(body.get("loon", 0)),
        ondernemer_inkomen=float(body.get("ondernemer_inkomen", 0)),
        huidige_vorm=str(body.get("huidige_vorm", "zzp")),
        urencriterium=bool(body.get("urencriterium", False)),
        gebruikelijk_loon=(float(body["gebruikelijk_loon"]) if body.get("gebruikelijk_loon") else None),
        partner_inkomen=float(body.get("partner_inkomen", 0)),
        eigen_woning=EigenWoning(woz_waarde=float(ew.get("woz_waarde", 0)),
                                 betaalde_hypotheekrente=float(ew.get("betaalde_hypotheekrente", 0))),
        box3=Box3Vermogen(banktegoeden=float(b3.get("banktegoeden", 0)),
                          overige_bezittingen=float(b3.get("overige_bezittingen", 0)),
                          schulden=float(b3.get("schulden", 0))),
        profiel=_profiel_from_json(body.get("profiel")),
        rendement=float(body.get("rendement", 0.06)),
        horizon=int(body.get("horizon", 15)),
    )
    return {
        "jaar": r.jaar, "baseline_belasting": r.baseline_belasting,
        "baseline_toeslagen": r.baseline_toeslagen, "baseline_netto": r.baseline_netto,
        "totaal_potentieel": r.totaal_potentieel, "rechtsvorm": r.rechtsvorm,
        "vermogen": r.vermogen, "lijfrente": r.lijfrente, "detail": r.detail,
        "suggesties": [
            {"titel": s.titel, "besparing": s.besparing, "toelichting": s.toelichting,
             "wetsartikel": s.wetsartikel}
            for s in r.suggesties
        ],
    }


def _mix_handler(body: dict) -> dict:
    from belastingkern.mix import bereken_mix
    ew = body.get("eigen_woning") or {}
    b3 = body.get("box3") or {}
    r = bereken_mix(
        float(body["vast_loon"]), float(body["extra_waarde"]),
        int(body.get("jaar", 2026)),
        vast_winst=float(body.get("vast_winst", 0)),
        urencriterium=bool(body.get("urencriterium", False)),
        gebruikelijk_loon=(float(body["gebruikelijk_loon"]) if body.get("gebruikelijk_loon") else None),
        eigen_woning=EigenWoning(
            woz_waarde=float(ew.get("woz_waarde", 0)),
            betaalde_hypotheekrente=float(ew.get("betaalde_hypotheekrente", 0)),
        ),
        box3=Box3Vermogen(
            banktegoeden=float(b3.get("banktegoeden", 0)),
            overige_bezittingen=float(b3.get("overige_bezittingen", 0)),
            schulden=float(b3.get("schulden", 0)),
        ),
        partner_inkomen=float(body.get("partner_inkomen", 0)),
        profiel=_profiel_from_json(body.get("profiel")),
    )
    return {
        "jaar": r.jaar, "vast_loon": r.vast_loon, "extra_waarde": r.extra_waarde,
        "beste": r.beste.naam,
        "opties": [
            {"naam": o.naam, "label": o.label, "marginale_belasting": o.marginale_belasting,
             "netto_extra": o.netto_extra, "marginaal_tarief": o.marginaal_tarief,
             "huishouden_belasting": o.huishouden_belasting, "huishouden_netto": o.huishouden_netto,
             "gemiddelde_druk": o.gemiddelde_druk}
            for o in sorted(r.opties, key=lambda x: -x.huishouden_netto)
        ],
        "detail_beste": r.detail_beste,
        "waarschuwingen": r.waarschuwingen,
    }


def _uitstel_handler(body: dict) -> dict:
    from belastingkern.uitstel import vergelijk_uitstel
    r = vergelijk_uitstel(
        float(body["kapitaal"]), float(body["rendement_pct"]), int(body.get("jaren", 15)),
        int(body.get("jaar", 2026)), tegenbewijs=bool(body.get("tegenbewijs", True)),
        partner=bool(body.get("partner", False)),
    )
    return {
        "jaar": r.jaar, "kapitaal": r.kapitaal, "rendement_pct": r.rendement_pct, "jaren": r.jaren,
        "bv_netto_groei_pct": r.bv_netto_groei_pct, "prive_netto_groei_pct": r.prive_netto_groei_pct,
        "bv_eindnetto": r.bv_eindnetto, "prive_eindnetto": r.prive_eindnetto,
        "omslag_rendement": r.omslag_rendement, "beste": r.beste,
        "waarschuwingen": r.waarschuwingen,
    }


def _straks_handler(body: dict) -> dict:
    """Pensioenfase: AOW + pensioen/lijfrente-uitkering (box 1, AOW-tarieven) + BV-dividend
    (box 2) + box 3-vermogen. Toont wat je STRAKS betaalt en netto overhoudt."""
    jaar = int(body.get("jaar", 2026))

    def bouw(d: dict) -> tuple[dict, float, float]:
        b3 = d.get("box3") or {}
        box3 = Box3Vermogen(
            banktegoeden=float(b3.get("banktegoeden", 0)),
            overige_bezittingen=float(b3.get("overige_bezittingen", 0)),
            schulden=float(b3.get("schulden", 0)),
        )
        inkomen = float(d.get("aow", 0)) + float(d.get("pensioen", 0)) + float(d.get("lijfrente", 0))
        div = float(d.get("bv_dividend", 0))
        persoon = Persoon(uitkering_pensioen=inkomen, box3=box3, aow_gerechtigd=True)
        r = bereken_persoon(persoon, jaar, box2_inkomen=div)
        bruto = inkomen + div
        blok = {
            "aow": float(d.get("aow", 0)), "pensioen": float(d.get("pensioen", 0)),
            "lijfrente": float(d.get("lijfrente", 0)), "bv_dividend": div,
            "bruto_inkomen": round(bruto, 2), "belastbaar_box1": r.box1.belastbaar_inkomen,
            "heffing_box1": r.box1.belasting_en_premies, "box2_belasting": r.box2_belasting,
            "heffing_box3": r.box3.belasting, "verzilverd": r.verzilverde_korting,
            "te_betalen": r.te_betalen, "netto": round(bruto - r.te_betalen, 2),
        }
        return blok, r.te_betalen, bruto

    jij, taxj, brutoj = bouw(body)
    out: dict = {"jaar": jaar, "jij": jij}
    tot_tax, tot_bruto = taxj, brutoj
    if body.get("partner"):
        partner, taxp, brutop = bouw(body["partner"])
        out["partner"] = partner
        tot_tax += taxp
        tot_bruto += brutop
    out["huishouden"] = {"te_betalen": round(tot_tax, 2), "netto": round(tot_bruto - tot_tax, 2)}
    return out


def _vermogensadvies_handler(body: dict) -> dict:
    from belastingkern.vermogensadvies import vermogensadvies
    r = vermogensadvies(
        int(body.get("jaar", 2026)),
        nieuwe_inleg=float(body.get("nieuwe_inleg", 0)),
        bestaand_box3=float(body.get("bestaand_box3", 0)),
        bestaand_spaargeld=float(body.get("bestaand_spaargeld", 0)),
        bestaand_bv_spaargeld=float(body.get("bestaand_bv_spaargeld", 0)),
        bestaand_bv_beleggingen=float(body.get("bestaand_bv_beleggingen", 0)),
        rendement=float(body.get("rendement", 0.06)),
        jaren=int(body.get("jaren", 15)),
        marginaal_nu=float(body.get("marginaal_nu", 0.3756)),
        tarief_uit=float(body.get("tarief_uit", 0.1785)),
        jaarruimte=float(body.get("jaarruimte", 0)),
        vrij_opneembaar=float(body.get("vrij_opneembaar", 0)),
        verwacht_pensioen=float(body.get("verwacht_pensioen", 0)),
        is_ondernemer=bool(body.get("is_ondernemer", False)),
        partner=bool(body.get("partner", False)),
        uitkeringsjaren=int(body.get("uitkeringsjaren", 20)),
        inflatie=float(body.get("inflatie", 0.02)),
    )
    return {
        "jaar": r.jaar, "nieuwe_inleg": r.nieuwe_inleg, "jaren": r.jaren, "rendement": r.rendement,
        "projectie": r.projectie,
        "containers": [
            {"naam": c.naam, "label": c.label, "netto_eind": c.netto_eind,
             "voorwaarde": c.voorwaarde, "max_bedrag": c.max_bedrag, "soort": c.soort}
            for c in r.containers
        ],
        "allocatie": r.allocatie, "bestaand_box3_last": r.bestaand_box3_last,
        "bestaand_bv": r.bestaand_bv, "liquiditeit_advies": r.liquiditeit_advies,
        "lijfrente_optimaal": r.lijfrente_optimaal,
        "waarschuwingen": r.waarschuwingen,
    }


def _dividendplan_handler(body: dict) -> dict:
    from belastingkern.dividendplan import box2_dividendplan
    r = box2_dividendplan(
        float(body["bedrag"]), int(body.get("jaar", 2026)),
        partner=bool(body.get("partner", False)),
        overig_box2=float(body.get("overig_box2", 0)),
    )
    return {
        "jaar": r.jaar, "bedrag": r.bedrag, "grens_laag": r.grens_laag,
        "tarief_laag": r.tarief_laag, "tarief_hoog": r.tarief_hoog,
        "heffing_ineens": r.heffing_ineens, "heffing_gespreid": r.heffing_gespreid,
        "besparing": r.besparing, "jaren_optimaal": r.jaren_optimaal,
        "jaarlijks_dividend": r.jaarlijks_dividend, "waarschuwingen": r.waarschuwingen,
    }


def _lijfrente_handler(body: dict) -> dict:
    from belastingkern.lijfrente import vergelijk_lijfrente
    r = vergelijk_lijfrente(
        float(body["inleg"]), float(body["rendement_pct"]), int(body.get("jaren", 20)),
        int(body.get("jaar", 2026)),
        marginaal_nu=float(body.get("marginaal_nu", 0.3756)),
        tarief_uit=float(body.get("tarief_uit", 0.1785)),
        overig_pensioen=(float(body["overig_pensioen"]) if body.get("overig_pensioen") not in (None, "") else None),
        uitkeringsjaren=int(body.get("uitkeringsjaren", 20)),
        tegenbewijs=bool(body.get("tegenbewijs", True)),
        partner=bool(body.get("partner", False)),
    )
    return {
        "jaar": r.jaar, "inleg": r.inleg, "rendement_pct": r.rendement_pct, "jaren": r.jaren,
        "marginaal_nu": r.marginaal_nu, "tarief_uit": r.tarief_uit,
        "lijfrente_eindnetto": r.lijfrente_eindnetto, "prive_eindnetto": r.prive_eindnetto,
        "voordeel": r.voordeel, "breakeven_tarief_uit": r.breakeven_tarief_uit,
        "overig_pensioen": r.overig_pensioen, "uitkering_per_jaar": r.uitkering_per_jaar,
        "tarief_uit_berekend": r.tarief_uit_berekend,
        "waarschuwingen": r.waarschuwingen,
    }


def _beleggingsgroei_handler(body: dict) -> dict:
    from belastingkern.beleggingsgroei import vergelijk_beleggingsgroei
    r = vergelijk_beleggingsgroei(
        float(body["beleggingen"]), float(body["rendement_pct"]),
        int(body.get("jaar", 2026)),
        spaargeld=float(body.get("spaargeld", 0)),
        schulden=float(body.get("schulden", 0)),
        overig_inkomen=float(body.get("overig_inkomen", 0)),
        urencriterium=bool(body.get("urencriterium", False)),
        tegenbewijs=bool(body.get("tegenbewijs", True)),
        partner=bool(body.get("partner", False)),
    )
    return {
        "jaar": r.jaar, "spaargeld": r.spaargeld, "beleggingen": r.beleggingen,
        "schulden": r.schulden, "rendement_pct": r.rendement_pct,
        "groei": r.groei, "beste": r.beste.naam,
        "opties": [
            {"naam": o.naam, "label": o.label, "belasting": o.belasting,
             "netto": o.netto, "effectief_tarief": o.effectief_tarief, "toelichting": o.toelichting}
            for o in sorted(r.opties, key=lambda x: x.belasting)
        ],
        "waarschuwingen": r.waarschuwingen,
    }


def _toerekening_handler(body: dict) -> dict:
    r = optimale_eigenwoning_verdeling(
        float(body["inkomen_a"]),
        float(body["inkomen_b"]),
        float(body.get("woz_waarde", 0.0)),
        float(body.get("hypotheekrente", 0.0)),
        int(body.get("jaar", 2026)),
    )
    return {
        "optimale_fractie_partner_a": r.optimale_fractie_partner_a,
        "totaal_optimaal": r.totaal_optimaal,
        "totaal_5050": r.totaal_5050,
        "besparing_vs_5050": r.besparing_vs_5050,
        "toelichting": r.toelichting,
    }


def _optimaliseer_handler(body: dict) -> dict:
    jaar = int(body.get("jaar", 2026))
    situatie = Situatie(
        economische_waarde=float(body["economische_waarde"]),
        profiel=_profiel_from_json(body.get("profiel")),
        prive_vermogen=float(body.get("prive_vermogen", 0.0)),
        spaargeld=float(body.get("spaargeld", 0.0)),
        verwacht_rendement=float(body.get("verwacht_rendement", 0.06)),
        urencriterium=bool(body.get("urencriterium", True)),
    )
    a = optimaliseer(situatie, jaar)
    return {
        "jaar": a.jaar,
        "beste": a.beste.naam,
        "besparing_vs_slechtste": a.besparing_vs_slechtste,
        "break_even_rendement": a.break_even_rendement,
        "jaarruimte_lijfrente": a.jaarruimte_lijfrente,
        "uitkomsten": [
            {
                "naam": u.naam,
                "inkomen_netto": u.inkomen_netto,
                "vermogen_last": u.vermogen_last,
                "totaal_netto": u.totaal_netto,
                "toelichting": u.toelichting,
            }
            for u in sorted(a.uitkomsten, key=lambda x: -x.totaal_netto)
        ],
        "tips": a.tips,
    }


# ---------- HTTP ----------

class Handler(BaseHTTPRequestHandler):
    server_version = "BelastingAPI/1.0"

    def _send(self, status: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_html(self) -> None:
        try:
            body = _CLIENT_HTML.read_bytes()
        except OSError:
            return self._send(404, {"error": "client niet gevonden"})
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self) -> None:  # CORS preflight
        self._send(204, {})

    def do_GET(self) -> None:
        if self.path in ("/", "/index.html"):
            return self._send_html()
        if self.path == "/health":
            return self._send(200, {"status": "ok"})
        if self.path == "/jaren":
            jaren = sorted(int(p.stem) for p in _PARAMS_DIR.glob("*.json"))
            return self._send(200, {"jaren": jaren})
        if self.path == "/grondslag":
            from belastingkern.rapport import WETTELIJKE_GRONDSLAG, DISCLAIMER
            return self._send(200, {"wettelijke_grondslag": WETTELIJKE_GRONDSLAG, "disclaimer": DISCLAIMER})
        self._send(404, {"error": f"onbekend pad: {self.path}"})

    def do_POST(self) -> None:
        roin = {
            "/vergelijk": _vergelijk_handler,
            "/optimaliseer": _optimaliseer_handler,
            "/toerekening": _toerekening_handler,
            "/rapport": _rapport_handler,
            "/bereken": _bereken_handler,
            "/mix": _mix_handler,
            "/advies": _advies_handler,
            "/beleggingsgroei": _beleggingsgroei_handler,
            "/uitstel": _uitstel_handler,
            "/lijfrente": _lijfrente_handler,
            "/dividendplan": _dividendplan_handler,
            "/vermogensadvies": _vermogensadvies_handler,
            "/straks": _straks_handler,
        }
        handler = roin.get(self.path)
        if handler is None:
            return self._send(404, {"error": f"onbekend pad: {self.path}"})
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length) or b"{}")
            return self._send(200, handler(body))
        except (KeyError, ValueError, TypeError) as e:
            return self._send(400, {"error": f"ongeldige invoer: {e}"})

    def log_message(self, *args) -> None:  # stil houden
        pass


def main(poort: int = 8000) -> None:
    server = ThreadingHTTPServer(("127.0.0.1", poort), Handler)
    print(f"Belasting-API op http://127.0.0.1:{poort}  (Ctrl-C om te stoppen)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--poort", type=int, default=8000)
    args = ap.parse_args()
    main(args.poort)
