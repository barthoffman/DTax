"""Omslagpunten tussen rechtsvormen: bij welke winst is ZZP vs DGA (vs werknemer)
fiscaal even duur? Het verschil in totale heffing is NIET monotoon — er kunnen
meerdere omslagpunten zijn (de DGA is alleen in een venster optimaal). Daarom scannen
we een raster op tekenwissels en bisecteren we elk interval.
"""

from __future__ import annotations

from dataclasses import dataclass

from .vergelijking import Vorm, vergelijk


def _score(vorm: str, V: float, jaar: int, *, inclusief_zvw: bool, urencriterium: bool) -> float:
    """Netto besteedbaar (hoger = beter): incl. Zvw, WW/WIA, pensioen én vaste kosten."""
    v = vergelijk(V, jaar, inclusief_zvw=inclusief_zvw, urencriterium=urencriterium)
    return getattr(v, vorm).netto_besteedbaar


def _bisect(f, lo: float, hi: float, flo: float, iters: int = 60) -> float:
    for _ in range(iters):
        mid = (lo + hi) / 2
        fm = f(mid)
        if (fm > 0) == (flo > 0):
            lo, flo = mid, fm
        else:
            hi = mid
    return round((lo + hi) / 2)


def omslagpunten(
    vorm_a: str,
    vorm_b: str,
    jaar: int,
    *,
    lo: float = 30000.0,
    hi: float = 800000.0,
    stap: float = 2500.0,
    inclusief_zvw: bool = True,
    urencriterium: bool = True,
) -> list[float]:
    """Alle winsten V waarbij totale heffing(vorm_a) == totale heffing(vorm_b),
    gevonden via rasterscan + bisectie. Kan 0, 1 of meer punten teruggeven."""

    def f(V: float) -> float:
        return (
            _score(vorm_a, V, jaar, inclusief_zvw=inclusief_zvw, urencriterium=urencriterium)
            - _score(vorm_b, V, jaar, inclusief_zvw=inclusief_zvw, urencriterium=urencriterium)
        )

    punten: list[float] = []
    vorige_V = lo
    vorige_f = f(lo)
    V = lo + stap
    while V <= hi:
        huidige_f = f(V)
        if vorige_f == 0:
            punten.append(round(vorige_V))
        elif (huidige_f > 0) != (vorige_f > 0):
            punten.append(_bisect(f, vorige_V, V, vorige_f))
        vorige_V, vorige_f = V, huidige_f
        V += stap
    return punten


@dataclass
class Segment:
    ondergrens: float
    bovengrens: float | None  # None = oneindig
    vorm: str


@dataclass
class OptimaleRoute:
    jaar: int
    inclusief_zvw: bool
    omslagpunten_zzp_dga: list[float]
    segmenten: list[Segment]

    def advies(self) -> str:
        regels = [
            f"Optimale rechtsvorm — belastingjaar {self.jaar} "
            f"({'incl. Zvw' if self.inclusief_zvw else 'kaal'})",
        ]
        if self.omslagpunten_zzp_dga:
            punten = ", ".join(f"€ {p:,.0f}".replace(",", ".") for p in self.omslagpunten_zzp_dga)
            regels.append(f"  omslagpunt(en) ZZP/DGA: {punten}")
        for s in self.segmenten:
            onder = f"€ {s.ondergrens:,.0f}".replace(",", ".")
            boven = "∞" if s.bovengrens is None else f"€ {s.bovengrens:,.0f}".replace(",", ".")
            regels.append(f"  {onder:>10} – {boven:<10} -> {s.vorm}")
        return "\n".join(regels)


def _beste_vorm(V: float, jaar: int, *, inclusief_zvw: bool, urencriterium: bool) -> str:
    v = vergelijk(V, jaar, inclusief_zvw=inclusief_zvw, urencriterium=urencriterium)
    return max(v.vormen, key=lambda x: x.netto_besteedbaar).naam


def bepaal_optimale_route(
    jaar: int,
    *,
    inclusief_zvw: bool = True,
    urencriterium: bool = True,
    lo: float = 30000.0,
    hi: float = 800000.0,
) -> OptimaleRoute:
    punten = omslagpunten(
        "zzp", "dga", jaar, lo=lo, hi=hi,
        inclusief_zvw=inclusief_zvw, urencriterium=urencriterium,
    )
    # Bouw segmenten uit de breekpunten; bepaal de goedkoopste vorm per segment
    # (werknemer meegenomen — die blijkt nergens optimaal, maar we checken het echt).
    grenzen = [lo, *punten, hi]
    segmenten: list[Segment] = []
    for onder, boven in zip(grenzen[:-1], grenzen[1:]):
        midden = (onder + boven) / 2
        vorm = _beste_vorm(
            midden, jaar, inclusief_zvw=inclusief_zvw, urencriterium=urencriterium
        )
        # Voeg samen met vorig segment als dezelfde vorm
        if segmenten and segmenten[-1].vorm == vorm:
            segmenten[-1].bovengrens = boven
        else:
            segmenten.append(Segment(ondergrens=onder, bovengrens=boven, vorm=vorm))
    if segmenten:
        segmenten[0].ondergrens = lo
        segmenten[-1].bovengrens = None  # tot oneindig (geëxtrapoleerd boven hi)
    return OptimaleRoute(
        jaar=jaar,
        inclusief_zvw=inclusief_zvw,
        omslagpunten_zzp_dga=punten,
        segmenten=segmenten,
    )
