"""Invoermodel: de gegevens die een inwoner (of het dashboard) aanlevert.

Bewust simpel gehouden: bedragen in hele euro's per jaar, percentages niet hier maar
in de params. Eigen woning en box 3-vermogen zijn per persoon; voor fiscale partners
kan de toerekening later worden geoptimaliseerd (zie engine.bereken_huishouden).
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class EigenWoning:
    """Gegevens eigen woning (box 1, afdeling 3.6 Wet IB 2001)."""

    woz_waarde: float = 0.0
    eigenwoningschuld: float = 0.0
    betaalde_hypotheekrente: float = 0.0  # aftrekbare rente + financieringskosten


@dataclass
class Box3Vermogen:
    """Vermogen voor box 3 op peildatum 1 januari (Wet IB 2001 hoofdstuk 5)."""

    banktegoeden: float = 0.0
    overige_bezittingen: float = 0.0
    schulden: float = 0.0
    groene_beleggingen: float = 0.0  # deel van banktegoeden/overige dat groen is
    werkelijk_rendement_pct: float | None = None  # tegenbewijsregeling: indien lager dan forfait


@dataclass
class Onderneming:
    """IB-onderneming (eenmanszaak/vof). `winst` = fiscale winst vóór ondernemersaftrek
    en MKB-winstvrijstelling. De engine zet dit om naar belastbare winst (box 1)."""

    winst: float = 0.0
    voldoet_urencriterium: bool = False     # ≥ 1.225 uur → zelfstandigenaftrek
    starter: bool = False                   # recht op startersaftrek
    overige_ondernemersaftrek: float = 0.0  # S&O-aftrek, meewerkaftrek, stakingsaftrek


@dataclass
class Persoon:
    """Eén belastingplichtige.

    `loon` = loon/uitkering/pensioen/AOW (box 1, loon uit (vroegere) dienstbetrekking).
    `arbeidsinkomen` voor de arbeidskorting = loon + winst + resultaat overige werkzaamheden.
    """

    naam: str = "persoon"
    geboortejaar: int | None = None
    aow_gerechtigd: bool = False

    # Inkomsten (box 1)
    loon: float = 0.0                       # loon uit TEGENWOORDIGE dienstbetrekking
    uitkering_pensioen: float = 0.0         # AOW, pensioen, uitkeringen (vroegere arbeid)
    winst_uit_onderneming: float = 0.0      # reeds belastbare winst (eenvoudige route)
    onderneming: "Onderneming | None" = None  # volledige route incl. ondernemersaftrek
    resultaat_overige_werkzaamheden: float = 0.0

    # Aftrekposten box 1 tegen het volle marginale tarief (lijfrente/uitgaven inkomensvoorziening,
    # afd. 3.7 — níet afgetopt door art. 2.10a).
    aftrekposten_box1: float = 0.0
    # Persoonsgebonden aftrek (afd. 6: giften, betaalde partneralimentatie, specifieke zorgkosten) —
    # verlaagt box 1 én valt onder de tariefaanpassing van art. 2.10a (max aftrektarief ~37,56%).
    persoonsgebonden_aftrek: float = 0.0

    # Vermogen / woning
    eigen_woning: EigenWoning = field(default_factory=EigenWoning)
    box3: Box3Vermogen = field(default_factory=Box3Vermogen)

    # Situatie voor heffingskortingen
    heeft_fiscale_partner: bool = False
    jongste_kind_leeftijd: int | None = None  # voor IACK (kind < 12)
    iack_recht_behouden: bool = True          # False als kind geboren ná 31-12-2024
    recht_alleenstaande_ouderenkorting: bool = False
    recht_jonggehandicaptenkorting: bool = False

    @property
    def arbeidsinkomen(self) -> float:
        """Grondslag arbeidskorting/IACK: alléén inkomen uit tegenwoordige arbeid.

        Pensioen, AOW en uitkeringen tellen hier NIET mee (loon uit vroegere arbeid)."""
        return (
            self.loon
            + self.winst_uit_onderneming
            + self.resultaat_overige_werkzaamheden
        )

    @property
    def box1_bruto_inkomen(self) -> float:
        """Alle box 1-inkomsten vóór aftrek en eigen woning."""
        return self.arbeidsinkomen + self.uitkering_pensioen


@dataclass
class Huishouden:
    """Eén of twee fiscale partners."""

    persoon: Persoon
    partner: Persoon | None = None
