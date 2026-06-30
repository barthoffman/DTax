"""Tests met handmatig nagerekende waarden (belastingjaar 2025/2026).

Draaien: vanuit map rekenkern/  ->  python -m pytest -q
(of zonder pytest:  python tests/test_kern.py)
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from belastingkern import (  # noqa: E402
    Persoon,
    EigenWoning,
    Box3Vermogen,
    Onderneming,
    bereken_persoon,
)
from belastingkern.box1 import bereken_box1  # noqa: E402
from belastingkern.onderneming import bereken_onderneming  # noqa: E402
from belastingkern.params import laad_params  # noqa: E402


def benadert(a: float, b: float, marge: float = 0.05) -> bool:
    return abs(a - b) <= marge


def test_box1_tarief_2026_werknemer():
    """Loon 45.000, onder AOW: schijf 1 + deel schijf 2."""
    p = laad_params(2026)
    persoon = Persoon(loon=45000)
    r = bereken_box1(persoon, p)
    # 38883*0,3575 + (45000-38883)*0,3756
    verwacht = 38883 * 0.3575 + (45000 - 38883) * 0.3756
    assert benadert(r.belasting_en_premies, round(verwacht, 2)), r.belasting_en_premies
    assert benadert(r.belastbaar_inkomen, 45000)


def test_arbeidskorting_2026_45000():
    p = laad_params(2026)
    r = bereken_persoon(Persoon(loon=45000), p)
    # segment 25845: 5300 + 0,0195*(45000-25845)
    verwacht = 5300 + 0.01950 * (45000 - 25845)
    assert benadert(r.kortingen.arbeids, round(verwacht, 2)), r.kortingen.arbeids


def test_algemene_heffingskorting_afbouw_2026():
    p = laad_params(2026)
    r = bereken_persoon(Persoon(loon=45000), p)
    verwacht = 3115 - 0.06398 * (45000 - 29736)
    assert benadert(r.kortingen.algemene, round(verwacht, 2)), r.kortingen.algemene


def test_volledige_werknemer_2026_te_betalen():
    """Integratie: loon 45.000, geen woning/vermogen."""
    r = bereken_persoon(Persoon(loon=45000), 2026)
    heffing = 38883 * 0.3575 + (45000 - 38883) * 0.3756
    ak = 5300 + 0.01950 * (45000 - 25845)
    ahk = 3115 - 0.06398 * (45000 - 29736)
    verwacht = heffing - ak - ahk
    assert benadert(r.te_betalen, round(verwacht, 2)), r.te_betalen


def test_pensioen_geeft_geen_arbeidskorting():
    """AOW-gerechtigde met alleen pensioen: arbeidskorting moet 0 zijn."""
    persoon = Persoon(aow_gerechtigd=True, uitkering_pensioen=30000)
    r = bereken_persoon(persoon, 2025)
    assert r.kortingen.arbeids == 0.0
    # schijf 1 AOW-tarief 17,92% over 30.000
    assert benadert(r.box1.belasting_en_premies, round(30000 * 0.1792, 2))


def test_box3_spaargeld_2026():
    """100.000 spaargeld, alleenstaand, 2026."""
    persoon = Persoon(box3=Box3Vermogen(banktegoeden=100000))
    r = bereken_persoon(persoon, 2026)
    grondslag_na_vrij = 100000 - 59357
    voordeel = grondslag_na_vrij * 0.0128
    verwacht = voordeel * 0.36
    assert benadert(r.box3.belasting, round(verwacht, 2)), r.box3.belasting


def test_box3_onder_heffingvrij_is_nul():
    persoon = Persoon(box3=Box3Vermogen(banktegoeden=40000))
    r = bereken_persoon(persoon, 2026)
    assert r.box3.belasting == 0.0


def test_hillen_aftrek_afgeloste_woning_2025():
    """Afgeloste woning: EWF wordt grotendeels onbelast door Hillen (76,67%)."""
    persoon = Persoon(
        loon=40000,
        eigen_woning=EigenWoning(woz_waarde=400000, betaalde_hypotheekrente=0),
    )
    r = bereken_persoon(persoon, 2025)
    ewf = 400000 * 0.0035  # 1400
    hillen = ewf * 0.7667
    netto_ewf = ewf - hillen
    assert benadert(r.box1.eigen_woning.hillen_aftrek, round(hillen, 2))
    # belastbaar = loon + netto EWF
    assert benadert(r.box1.belastbaar_inkomen, round(40000 + netto_ewf, 2))


def test_verdamping_korting_bij_laag_inkomen():
    """Weinig heffing, hoge korting: deel verdampt, te betalen = 0."""
    persoon = Persoon(box3=Box3Vermogen(banktegoeden=100000))
    r = bereken_persoon(persoon, 2026)
    assert r.te_betalen == 0.0
    assert r.verdampte_korting > 0


def test_onderneming_zelfstandigenaftrek_en_mkb_2026():
    """Winst 60.000, urencriterium, niet-starter, 2026."""
    p = laad_params(2026)
    r = bereken_onderneming(
        Onderneming(winst=60000, voldoet_urencriterium=True), p
    )
    assert benadert(r.zelfstandigenaftrek, 1200)
    winst_na = 60000 - 1200
    mkb = winst_na * 0.127
    assert benadert(r.mkb_winstvrijstelling, round(mkb, 2)), r.mkb_winstvrijstelling
    assert benadert(r.belastbare_winst, round(winst_na - mkb, 2))


def test_onderneming_zonder_urencriterium_alleen_mkb():
    p = laad_params(2025)
    r = bereken_onderneming(Onderneming(winst=50000), p)
    assert r.zelfstandigenaftrek == 0.0
    assert benadert(r.mkb_winstvrijstelling, round(50000 * 0.127, 2))


def test_zzp_arbeidskorting_op_belastbare_winst_2026():
    """Arbeidskorting-grondslag = belastbare winst (na ondernemersaftrek + MKB)."""
    persoon = Persoon(onderneming=Onderneming(winst=60000, voldoet_urencriterium=True))
    r = bereken_persoon(persoon, 2026)
    belastbare_winst = round((60000 - 1200) * (1 - 0.127), 2)  # 51.332,40
    assert benadert(r.box1.belastbaar_inkomen, belastbare_winst), r.box1.belastbaar_inkomen
    # arbeidskorting over belastbare winst (~51.332): afbouwsegment vanaf 45.592
    ak = 5685 - 0.06510 * (belastbare_winst - 45592)
    assert benadert(r.kortingen.arbeids, round(ak, 2)), r.kortingen.arbeids


def test_box2_tarief_2026():
    """Dividend 50.000 (< grens 68.843) → 24,5%."""
    from belastingkern import bereken_persoon as bp
    r = bp(Persoon(naam="ab"), 2026, box2_inkomen=50000)
    assert benadert(r.box2_belasting, round(50000 * 0.245, 2)), r.box2_belasting


def test_dga_gecombineerde_druk_hoog():
    """Grote winst: deel winst boven schijven → richting ~48,8% op het dividend-deel."""
    from belastingkern.dga import bereken_dga
    r = bereken_dga(500000, 2026)
    # Sanity: effectief tarief tussen 30% en 50%.
    assert 0.30 < r.effectief_tarief < 0.50, r.effectief_tarief
    # Vpb over winst na gebruikelijk loon (500k - 58k = 442k): 200k*19% + 242k*25,8%
    verwacht_vpb = 200000 * 0.19 + (442000 - 200000) * 0.258
    assert benadert(r.vennootschapsbelasting, round(verwacht_vpb, 2)), r.vennootschapsbelasting


def test_vergelijking_drie_vormen_2026():
    from belastingkern.vergelijking import vergelijk
    v = vergelijk(100000, 2026)  # incl. Zvw + WW/WIA
    for vorm in v.vormen:
        assert 0.20 < vorm.effectief_tarief < 0.45, (vorm.naam, vorm.effectief_tarief)
    # Netto besteedbaar + wig + vaste kosten + oprichting == bruto (pensioen = 0).
    for vorm in v.vormen:
        assert benadert(
            vorm.netto_besteedbaar + vorm.totale_wig + vorm.vaste_kosten
            + vorm.oprichtingskosten_jaar, 100000, marge=1.0
        )


def test_zvw_sluit_kloof_zzp_dga_2026():
    """Thesis-toets: met Zvw (zonder WW/WIA) convergeren ZZP en DGA op ± 100k (binnen ~1,5pp)."""
    from belastingkern.vergelijking import vergelijk
    v = vergelijk(100000, 2026, inclusief_zvw=True, inclusief_wnv=False)
    verschil = abs(v.zzp.effectief_tarief - v.dga.effectief_tarief) * 100
    assert verschil < 1.5, (v.zzp.effectief_tarief, v.dga.effectief_tarief)
    # Zonder WW/WIA blijft de werknemer duurder.
    assert v.werknemer.effectief_tarief > v.zzp.effectief_tarief


def test_dividend_geen_zvw():
    """Over box 2-dividend is geen Zvw verschuldigd: DGA-Zvw alleen over het loon."""
    from belastingkern.vergelijking import vergelijk
    from belastingkern.params import laad_params
    p = laad_params(2026)
    v = vergelijk(200000, 2026)
    # DGA-Zvw = lage bijdrage over (gemaximeerd) gebruikelijk loon, niet over winst.
    maxg = p["zvw"]["max_bijdrage_inkomen"]
    verwacht = round(min(58000, maxg) * 0.0485, 2)
    assert benadert(v.dga.zvw, verwacht), v.dga.zvw


def test_werknemersverzekeringen_sluit_kloof_2026():
    """Met WW/WIA als werkgeverslast in V daalt de zuivere belastingdruk van de werknemer
    richting de ZZP (de premie buigt het brutoloon omlaag); WW/WIA verschijnt apart."""
    from belastingkern.vergelijking import vergelijk
    met = vergelijk(120000, 2026, inclusief_wnv=True)
    zonder = vergelijk(120000, 2026, inclusief_wnv=False)
    # WW/WIA-premie alleen bij de werknemer, niet bij ZZP/DGA.
    assert met.werknemer.werknemersverzekeringen > 0
    assert met.zzp.werknemersverzekeringen == 0.0
    assert met.dga.werknemersverzekeringen == 0.0
    # Belastingdruk werknemer daalt door het meenemen van WW/WIA in V.
    assert met.werknemer.effectief_tarief < zonder.werknemer.effectief_tarief
    # En komt dicht bij de ZZP (binnen ~1,5pp).
    assert abs(met.werknemer.effectief_tarief - met.zzp.effectief_tarief) * 100 < 1.5


def test_wig_hoger_dan_belasting_werknemer():
    from belastingkern.vergelijking import vergelijk
    v = vergelijk(120000, 2026)
    assert v.werknemer.totale_wig > v.werknemer.totale_belasting
    assert v.zzp.totale_wig == v.zzp.totale_belasting  # geen WW/WIA


def test_vaste_kosten_drukken_netto_en_verschuiven_omslagpunt():
    from belastingkern.vergelijking import vergelijk
    from belastingkern.optimalisatie import omslagpunten
    met = vergelijk(120000, 2026)
    geen = vergelijk(120000, 2026, vaste_kosten={"werknemer": 0, "zzp": 0, "dga": 0})
    assert met.dga.vaste_kosten == 2000 and met.zzp.vaste_kosten == 900
    # Na-belasting kost de € 2.000 BV-overhead tussen ~€ 1.000 en € 2.000 netto.
    verschil = geen.dga.netto_besteedbaar - met.dga.netto_besteedbaar
    assert 1000 < verschil < 2100, verschil
    # Het ZZP->DGA-omslagpunt schuift omhoog door de overhead.
    assert omslagpunten("zzp", "dga", 2026)[0] > 105000


def test_gebruikelijk_loon_eigen_gebruik_verdampt_dga_voordeel():
    """Bij gebruikelijk loon = volledige arbeidsbeloning (eigen gebruik) verdwijnt het
    DGA-voordeel: geen dividend, geen ondernemersaftrek -> de ZZP wint."""
    from belastingkern.vergelijking import vergelijk
    norm = vergelijk(120000, 2026)                                # loon = normbedrag
    arbeid = vergelijk(120000, 2026, gebruikelijk_loon=120000)    # loon = volledige arbeid
    assert norm.dga.netto_besteedbaar > norm.zzp.netto_besteedbaar
    assert arbeid.dga.netto_besteedbaar < arbeid.zzp.netto_besteedbaar


def test_oprichtingskosten_geamortiseerd():
    from belastingkern.vergelijking import vergelijk
    v = vergelijk(120000, 2026)
    # BV € 600 / 10 jaar = € 60/jr; ZZP € 80 / 10 = € 8/jr
    assert benadert(v.dga.oprichtingskosten_jaar, 60.0)
    assert benadert(v.zzp.oprichtingskosten_jaar, 8.0)
    # Kortere horizon -> hogere jaarlast
    kort = vergelijk(120000, 2026, horizon_jaren=2)
    assert kort.dga.oprichtingskosten_jaar > v.dga.oprichtingskosten_jaar


def test_omslagpunten_zzp_dga_2026():
    """DGA is alleen in een VENSTER optimaal: route is zzp -> dga -> zzp."""
    from belastingkern.optimalisatie import bepaal_optimale_route
    r = bepaal_optimale_route(2026)
    assert len(r.omslagpunten_zzp_dga) == 2, r.omslagpunten_zzp_dga
    assert 95000 < r.omslagpunten_zzp_dga[0] < 110000
    assert 380000 < r.omslagpunten_zzp_dga[1] < 430000
    assert [s.vorm for s in r.segmenten] == ["zzp", "dga", "zzp"]


def test_toeslagen_koppeling_aan_rechtsvorm_2026():
    """Bij laag inkomen heeft de DGA het hoogste toetsingsinkomen (volledig loon, geen
    ondernemersaftrek) -> minste toeslag; de ZZP het laagste -> meeste toeslag."""
    from belastingkern.vergelijking import vergelijk
    from belastingkern.toeslagen import Huishoudprofiel
    prof = Huishoudprofiel(heeft_toeslagpartner=True, aantal_kinderen=2)
    v = vergelijk(40000, 2026, profiel=prof)
    assert v.dga.verzamelinkomen > v.zzp.verzamelinkomen
    assert v.zzp.toeslagen_totaal >= v.dga.toeslagen_totaal
    # Zonder profiel: geen toeslagen berekend.
    assert vergelijk(40000, 2026).werknemer.toeslagen is None


def test_huurtoeslag_2026():
    from belastingkern.toeslagen import huurtoeslag, Huishoudprofiel
    p = laad_params(2026)
    prof = Huishoudprofiel()  # alleenstaande
    laag, _ = huurtoeslag(700.0, 20000, p, profiel=prof)   # laag inkomen, huur in 65%-zone
    hoog, _ = huurtoeslag(700.0, 40000, p, profiel=prof)   # hoger inkomen: afbouw
    assert laag > 0
    assert hoog < laag                                     # inkomensafbouw werkt
    # Huur onder de eigen bijdrage -> geen toeslag
    geen, _ = huurtoeslag(150.0, 20000, p, profiel=prof)
    assert geen == 0.0


def test_huurtoeslag_via_profiel_in_vergelijking():
    from belastingkern.vergelijking import vergelijk
    from belastingkern.toeslagen import Huishoudprofiel
    prof = Huishoudprofiel(heeft_toeslagpartner=True, aantal_kinderen=2, rekenhuur=750.0)
    v = vergelijk(35000, 2026, profiel=prof)
    assert v.zzp.toeslagen.huurtoeslag > 0  # huurtoeslag stroomt mee in de koppeling


def test_kinderopvangtoeslag_2026():
    from belastingkern.toeslagen import kinderopvangtoeslag, kinderopvang_vergoedingspercentage
    p = laad_params(2026)
    assert kinderopvang_vergoedingspercentage(40000, p) == 0.96       # onder grens: max
    assert kinderopvang_vergoedingspercentage(200000, p) == 0.365     # boven: min 1e kind
    # 1 kind dagopvang, 120 u/mnd, beide ouders 160 u/mnd werk, laag inkomen
    kot = kinderopvangtoeslag(
        40000, p, opvangsoort="dagopvang", uurtarief=11.23,
        opvanguren_per_maand=120, gewerkte_uren_minstverdiener_per_maand=160,
    )
    # 11,23 x min(120, 1,40x160=224, 230)=120 x 0,96 x 12
    assert benadert(kot, round(11.23 * 120 * 0.96 * 12, 2), marge=1.0), kot
    # Tarief boven max wordt afgetopt
    afgetopt = kinderopvangtoeslag(
        40000, p, opvangsoort="dagopvang", uurtarief=15.0,
        opvanguren_per_maand=120, gewerkte_uren_minstverdiener_per_maand=160,
    )
    assert afgetopt == kot  # 15 -> afgetopt op 11,23


def test_zorgtoeslag_afbouw_2026():
    from belastingkern.toeslagen import zorgtoeslag
    p = laad_params(2026)
    assert zorgtoeslag(25000, p) == 1548.0          # onder drempel: max
    assert zorgtoeslag(45000, p) == 0.0             # boven inkomensgrens: nihil
    assert 0 < zorgtoeslag(35000, p) < 1548.0       # ertussen: afbouw
    # vermogenstoets: te hoog vermogen -> 0
    assert zorgtoeslag(25000, p, vermogen=200000) == 0.0


def test_kindgebonden_budget_afbouw_2026():
    from belastingkern.toeslagen import kindgebonden_budget, Huishoudprofiel
    p = laad_params(2026)
    prof = Huishoudprofiel(aantal_kinderen=2, kinderen_12_15=1)
    laag = kindgebonden_budget(20000, p, profiel=prof)
    # 2x basis 2580 + 1x opslag 724 = 5884 (onder afbouwpunt)
    assert benadert(laag, 2 * 2580 + 724), laag
    hoog = kindgebonden_budget(80000, p, profiel=prof)
    assert hoog < laag  # afbouw


def test_toeslagen_lager_bij_hoger_inkomen():
    from belastingkern.toeslagen import bereken_toeslagen, Huishoudprofiel
    p = laad_params(2026)
    prof = Huishoudprofiel(aantal_kinderen=1)
    laag = bereken_toeslagen(25000, p, profiel=prof).totaal
    hoog = bereken_toeslagen(60000, p, profiel=prof).totaal
    assert laag > hoog


def test_optimalisatiemotor_kiest_beste():
    from belastingkern import Situatie, optimaliseer
    # Midden in het DGA-venster, geen vermogen -> DGA optimaal.
    a = optimaliseer(Situatie(economische_waarde=200000), 2026)
    assert a.beste.naam == "dga", a.beste.naam
    assert a.besparing_vs_slechtste > 0


def test_box3_vs_bv_breakeven_2026():
    from belastingkern.optimalisatiemotor import break_even_rendement
    from belastingkern.params import laad_params
    p = laad_params(2026)
    be = break_even_rendement(p)
    # forfait 6,00% x 36% / (0,19 + 0,81 x 0,245) ≈ 5,56%
    assert benadert(be, 0.0216 / 0.38845, marge=0.002), be


def test_box3_vermogen_dimensie_versterkt_dga_zonder_tegenbewijs():
    """Forfait-only: laagrenderend vermogen vergroot het DGA-voordeel (box 3 vermeden in BV)."""
    from belastingkern import Situatie, optimaliseer
    zonder = optimaliseer(Situatie(economische_waarde=200000, tegenbewijs_box3=False), 2026)
    met = optimaliseer(
        Situatie(economische_waarde=200000, prive_vermogen=500000,
                 verwacht_rendement=0.015, tegenbewijs_box3=False),
        2026,
    )
    voordeel_zonder = zonder.beste.totaal_netto - min(u.totaal_netto for u in zonder.uitkomsten)
    voordeel_met = met.beste.totaal_netto - min(u.totaal_netto for u in met.uitkomsten)
    assert met.beste.naam == "dga"
    assert voordeel_met > voordeel_zonder


def test_tegenbewijs_box3_verlaagt_heffing():
    """bereken_box3: werkelijk rendement onder het forfait -> lagere heffing."""
    from belastingkern.box3 import bereken_box3
    from belastingkern import Box3Vermogen
    p = laad_params(2026)
    forfait = bereken_box3(Box3Vermogen(overige_bezittingen=500000), p)
    werkelijk = bereken_box3(
        Box3Vermogen(overige_bezittingen=500000, werkelijk_rendement_pct=0.015), p
    )
    assert werkelijk.tegenbewijs_toegepast
    assert werkelijk.belasting < forfait.belasting


def test_tegenbewijs_neutraliseert_bv_voordeel():
    """Mét tegenbewijs (default) heft box 3 op werkelijk rendement (36%) < BV (38,8%):
    de DGA houdt vermogen dan óók privé, dus geen BV-vermogensvoordeel."""
    from belastingkern import Situatie, optimaliseer
    a = optimaliseer(
        Situatie(economische_waarde=200000, prive_vermogen=500000, verwacht_rendement=0.015),
        2026,
    )
    lasten = {u.naam: u.vermogen_last for u in a.uitkomsten}
    assert benadert(lasten["dga"], lasten["zzp"], marge=1.0)  # gelijk: allen box 3


def test_jaarruimte_2026():
    from belastingkern.pensioen import jaarruimte
    p = laad_params(2026)
    # 0,30 x (60.000 - 19.172 franchise), factor A = 0
    assert benadert(jaarruimte(60000, p), round(0.30 * (60000 - 19172), 2))
    # Boven de aftoppingsgrens: gemaximeerd op max_jaarruimte
    assert jaarruimte(200000, p) <= 35589
    # Factor A (werkgeverspensioen) verlaagt de ruimte
    assert jaarruimte(60000, p, factor_a=1000) < jaarruimte(60000, p)


def test_partnertoerekening_lage_inkomenspartner():
    """HRA bij de lage-inkomenspartner verdampt deels -> optimaal naar de hoogverdiener."""
    from belastingkern.toerekening import optimale_eigenwoning_verdeling
    r = optimale_eigenwoning_verdeling(120000, 20000, woz_waarde=0, hypotheekrente=7000, jaar=2026)
    assert r.optimale_fractie_partner_a >= 0.9          # vrijwel volledig bij A (120k)
    assert r.besparing_vs_5050 > 0


def test_partnertoerekening_twee_topverdieners_indifferent():
    """Twee partners in de topschijf: verdeling maakt ~niets uit (aftopping 37,56%)."""
    from belastingkern.toerekening import optimale_eigenwoning_verdeling
    r = optimale_eigenwoning_verdeling(120000, 120000, woz_waarde=0, hypotheekrente=7000, jaar=2026)
    assert r.besparing_vs_5050 < 1.0


def test_mix_zzp_beste_voor_kleine_bijverdienste():
    from belastingkern.mix import bereken_mix
    r = bereken_mix(40000, 30000, 2026, urencriterium=False)
    assert r.beste.naam == "zzp"  # MKB-winstvrijstelling wint
    bv = next(o for o in r.opties if o.naam == "bv")
    loon = next(o for o in r.opties if o.naam == "meer_loon")
    assert bv.marginale_belasting > loon.marginale_belasting  # kleine BV = alleen overhead


def test_mix_volledige_situatie_partner_box3():
    """Mix met partner + box 3 levert huishouden_netto en houdt de ZZP-voorkeur."""
    from belastingkern.mix import bereken_mix
    from belastingkern.model import Box3Vermogen
    r = bereken_mix(40000, 30000, 2026, urencriterium=False,
                    partner_inkomen=25000, box3=Box3Vermogen(banktegoeden=80000))
    assert r.beste.naam == "zzp"
    assert all(o.huishouden_netto > 0 for o in r.opties)


def test_box3_split_spaargeld_lager_belast_dan_beleggingen():
    from belastingkern.optimalisatiemotor import box3_last
    p = laad_params(2026)
    spaar = box3_last(p, spaargeld=200000, beleggingen=0)
    beleg = box3_last(p, spaargeld=0, beleggingen=200000)
    assert 0 < spaar < beleg


def test_bereken_partner_huishouden():
    from api import _bereken_handler
    r = _bereken_handler({"jaar": 2026, "loon": 40000, "partner": {"loon": 30000}})
    assert "partner" in r and "huishouden" in r
    assert benadert(r["huishouden"]["te_betalen"], r["te_betalen"] + r["partner"]["te_betalen"], marge=1.0)


def test_uitstel_bv_vs_prive_met_heffingvrij():
    from belastingkern.uitstel import vergelijk_uitstel
    # Klein bedrag: heffingvrij vermogen domineert → privé wint (ook bij gematigd rendement).
    klein = vergelijk_uitstel(100000, 0.08, 15, 2026)
    assert klein.beste == "prive"
    # Groot bedrag, gematigd rendement: heffingvrij verwaarloosbaar → BV wint.
    groot = vergelijk_uitstel(2000000, 0.06, 15, 2026)
    assert groot.beste == "bv"
    # Groot bedrag, hoog rendement: box 3-forfait ondertaxeert → privé wint.
    hoog = vergelijk_uitstel(2000000, 0.15, 15, 2026)
    assert hoog.beste == "prive"


def test_lijfrente_vs_prive():
    from belastingkern.lijfrente import vergelijk_lijfrente
    # Tariefarbitrage (37,56% nu, 17,85% opname) → lijfrente wint ruim.
    arb = vergelijk_lijfrente(20000, 0.06, 20, 2026, marginaal_nu=0.3756, tarief_uit=0.1785)
    assert arb.voordeel > 0 and arb.lijfrente_eindnetto > arb.prive_eindnetto
    # Gelijk tarief, klein bedrag onder heffingvrij → nagenoeg gelijk (privé ook belastingvrij).
    klein = vergelijk_lijfrente(20000, 0.06, 20, 2026, marginaal_nu=0.3756, tarief_uit=0.3756)
    assert abs(klein.voordeel) < 50
    # Gelijk tarief, groot bedrag boven heffingvrij → lijfrente wint door belastingvrije groei.
    groot = vergelijk_lijfrente(300000, 0.06, 20, 2026, marginaal_nu=0.3756, tarief_uit=0.3756)
    assert groot.voordeel > 0


def test_vermogensadvies_waterval():
    from belastingkern.vermogensadvies import vermogensadvies
    r = vermogensadvies(2026, nieuwe_inleg=30000, jaarruimte=20000, vrij_opneembaar=5000,
                        rendement=0.06, jaren=20, marginaal_nu=0.45, tarief_uit=0.1785)
    # 5.000 liquide → box 3; 20.000 → lijfrente (jaarruimte); overschot 5.000 → box 3.
    assert r.allocatie["lijfrente"] == 20000
    assert r.allocatie["box3"] == 10000
    assert r.allocatie["bv"] == 0
    assert {c.naam for c in r.containers} == {"lijfrente", "box3"}  # geen BV (niet-ondernemer)
    # Projectie: jaarlijkse lijfrente-inleg groeit tot een pot → jaarlijkse uitkering.
    P = r.projectie
    assert P["lijfrente_pot"] > r.allocatie["lijfrente"] * P["jaren_opbouw"]  # groei boven inleg
    assert abs(P["lijfrente_uitkering"] - P["lijfrente_pot"] / P["uitkeringsjaren"]) < 1


def test_advies_kwantificeert_suggesties():
    from belastingkern.advies import optimalisatie_advies
    from belastingkern.model import EigenWoning, Box3Vermogen
    a = optimalisatie_advies(
        2026, ondernemer_inkomen=60000, urencriterium=True, partner_inkomen=25000,
        eigen_woning=EigenWoning(woz_waarde=400000, betaalde_hypotheekrente=8000),
        box3=Box3Vermogen(overige_bezittingen=200000))
    assert any("Lijfrente" in s.titel for s in a.suggesties)
    assert a.totaal_potentieel > 0
    bes = [s.besparing for s in a.suggesties]
    assert bes == sorted(bes, reverse=True)  # aflopend gesorteerd
    assert a.rechtsvorm and {o["naam"] for o in a.rechtsvorm["opties"]} == {"meer_loon", "zzp", "bv"}


def test_kinderopvangtoeslag_in_bereken_toeslagen():
    from belastingkern.toeslagen import bereken_toeslagen, Huishoudprofiel
    p = laad_params(2026)
    prof = Huishoudprofiel(
        aantal_kinderen=1, kinderopvang_soort="dagopvang",
        kinderopvang_uren_per_maand=100, kinderopvang_uurtarief=11.0, kinderopvang_kinderen=1,
    )
    t = bereken_toeslagen(40000, p, profiel=prof)
    assert t.kinderopvangtoeslag > 0
    assert benadert(t.totaal, t.zorgtoeslag + t.kindgebonden_budget + t.huurtoeslag + t.kinderopvangtoeslag)


def test_beleggingsgroei_box3_vs_box1():
    from belastingkern.beleggingsgroei import vergelijk_beleggingsgroei
    # Hoog overig inkomen -> hoog marginaal tarief -> box 3 (forfait) gunstigst voor de groei.
    hoog = vergelijk_beleggingsgroei(100000, 0.10, 2026, overig_inkomen=80000)
    assert hoog.beste.naam == "box3"
    box3 = next(o for o in hoog.opties if o.naam == "box3")
    row = next(o for o in hoog.opties if o.naam == "row")
    assert box3.belasting < row.belasting
    assert len(hoog.opties) == 4 and all(0 <= o.effectief_tarief < 0.6 for o in hoog.opties)


def test_api_bereken_gecombineerd_inkomen():
    """Werkelijk-inkomen-endpoint: loon + winst stapelen in één box 1-berekening."""
    import json as _json
    from api import _bereken_handler
    r = _bereken_handler({"jaar": 2026, "loon": 40000, "winst": 25000, "urencriterium": True})
    # belastbaar = loon + (winst na zelfstandigenaftrek + MKB)
    belastbare_winst = (25000 - 1200) * (1 - 0.127)
    assert benadert(r["belastbaar_box1"], round(40000 + belastbare_winst, 2), marge=1.0)
    assert r["te_betalen"] > 0 and 0 < r["gemiddeld_tarief"] < 0.45
    _json.dumps(r)


def test_rapport_bevat_grondslag_en_aannames():
    import json as _json
    from belastingkern import Situatie, Huishoudprofiel
    from belastingkern.rapport import bouw_rapport, rapport_markdown
    s = Situatie(
        economische_waarde=120000,
        profiel=Huishoudprofiel(heeft_toeslagpartner=True, partner_inkomen=20000, aantal_kinderen=2),
        prive_vermogen=500000, verwacht_rendement=0.015,
    )
    r = bouw_rapport(s, 2026, datum="2026-06-29")
    assert r["advies"]["beste_route"] in ("werknemer", "zzp", "dga")
    assert r["wettelijke_grondslag"] and all("wetsartikel" in g for g in r["wettelijke_grondslag"])
    assert r["aannames_en_benaderingen"]
    assert "disclaimer" in r
    _json.dumps(r)  # formaat-agnostisch: JSON-serialiseerbaar
    md = rapport_markdown(r)
    assert "Wettelijke grondslag" in md and "Disclaimer" in md


def test_api_handlers_json_serialiseerbaar():
    import json as _json
    from api import _optimaliseer_handler, _vergelijk_handler
    o = _optimaliseer_handler(
        {"economische_waarde": 150000, "prive_vermogen": 500000, "verwacht_rendement": 0.015}
    )
    assert o["beste"] in ("werknemer", "zzp", "dga")
    _json.dumps(o)  # moet JSON-serialiseerbaar zijn
    v = _vergelijk_handler({"economische_waarde": 100000, "profiel": {"aantal_kinderen": 1}})
    assert {"werknemer", "zzp", "dga"} <= set(v)
    assert "toeslagen" in v["zzp"]
    _json.dumps(v)


def _run_zonder_pytest() -> int:
    fouten = 0
    for naam, fn in sorted(globals().items()):
        if naam.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"PASS {naam}")
            except AssertionError as e:
                fouten += 1
                print(f"FAIL {naam}: {e}")
    print(f"\n{'-'*40}\n{'GESLAAGD' if not fouten else f'{fouten} FOUT(EN)'}")
    return fouten


if __name__ == "__main__":
    raise SystemExit(_run_zonder_pytest())
