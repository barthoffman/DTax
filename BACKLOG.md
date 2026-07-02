# Backlog

Levende lijst van nog te bouwen optimalisaties en verfijningen. Per item: wat, voor wie,
grootte-orde, status (rekenkern al klaar of nog bouwen), en geschatte inspanning.
Aangemaakt 2026-06-29. Afgeronde items verplaatsen naar JOURNAAL.

---

## "NU" — Mijn belasting (huidig jaar)

### A. Rekenkern ondersteunt het al — alleen koppelen ✅ AFGEROND
IACK, startersaftrek, groene beleggingen en meewerkaftrek zijn gekoppeld (2026-06-30/07-01) plus
de arbeidsbeloning-optimalisatie en de partner-jaarruimte-suggestie. Zie JOURNAAL fase 27–28. Blok
A is leeg.

### B. Nog niet in de rekenkern — bouwen
| # | Optimalisatie | Voor wie | Inspanning |
|---|---|---|---|
| ~~KIA~~ | ✅ **KIA / kleinschaligheidsinvesteringsaftrek** (gebouwd 2026-07-01, JOURNAAL fase 29) | — | — |
| 1 | **Giftenaftrek** (m.n. periodieke giften) | gever aan ANBI | middel — aftrekpost + drempel/plafond |
| 2 | **Partneralimentatie (betaald)** | gescheiden, betaalt alimentatie | klein/middel — box 1-aftrekpost |
| 3 | **Specifieke zorgkosten** | hoge zorgkosten boven drempel | middel — drempel afhankelijk van inkomen |

> Ook gebouwd 2026-07-01 (fase 29): **jaarruimte-correctie factor A** (werkgeverspensioen verlaagt de
> ruimte), **reserveringsruimte-inhaal** (met pensioen-bewuste cap), en de expliciete **cap-uitleg**
> (rendement vs flexibiliteit boven de grens). Zie JOURNAAL.

---

## Vermogen / Straks — verfijningen (eerder besproken)

| # | Item | Waarom | Inspanning |
|---|---|---|---|
| V1 | **Leegwaarderatio verhuurwoningen** | box 3-waarde verhuurd huis = WOZ × ratio (<1), niet volle WOZ | klein/middel |
| V2 | **AOW naar `params`** | pensioen-inputs zijn al geünificeerd (fase 26–28); alleen de AOW-bedragen (€ 20.929/€ 14.379) staan nog hardcoded in de client — verplaats naar `params` (sourced PEN-03) | klein |
| V3 | **Vastgoed ín de BV** | eigen dynamiek (huur, WOZ, geen box 3-vrijstelling, overdrachtsbelasting) | middel |
| V4 | **Uitkeringsfase lijfrente jaar-voor-jaar** | nu lump-sum op pensioendatum; doorgroei tijdens uitkeren genegeerd (conservatief) | middel — **laag nut**, beide routes groeien evenredig |
| V5 | **Heffingvrij gewogen gemiddelde op BV spaar/beleggen-split** | nu volledig op beleggingen i.p.v. gewogen; ~€ 300–500/jr afwijking | klein |

---

## Onzeker / te verifiëren
- Box 3-forfaits banktegoeden (~1,28%) en schulden (~2,70%) 2026 zijn **voorlopig** — checken bij
  definitieve vaststelling (zie `bronnen/bronregister.md`).
- Hillen-percentage (aftrek geen/lage eigenwoningschuld) gemarkeerd onzeker in params.
