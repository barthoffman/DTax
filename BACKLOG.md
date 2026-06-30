# Backlog

Levende lijst van nog te bouwen optimalisaties en verfijningen. Per item: wat, voor wie,
grootte-orde, status (rekenkern al klaar of nog bouwen), en geschatte inspanning.
Aangemaakt 2026-06-29. Afgeronde items verplaatsen naar JOURNAAL.

---

## "NU" — Mijn belasting (huidig jaar)

### A. Rekenkern ondersteunt het al — alleen koppelen in de advies-motor
De engine heeft het veld; `optimalisatie_advies` geeft het nog niet door en toont het niet als
optimalisatie-regel.

| # | Optimalisatie | Engine-veld | Voor wie | Grootte-orde | Inspanning |
|---|---|---|---|---|---|
| 1 | **IACK** (inkomensafhankelijke combinatiekorting) | `jongste_kind_leeftijd` | werkende ouders, jongste kind < 12 | tot ~€ 2.986/jr | klein — input "leeftijd jongste kind" bij Kinderen + doorgeven + regel |
| 2 | **Startersaftrek** | `starter` | nieuwe ZZP'er (eerste 3 jr, max 3×) | € 2.123 × marginaal (~€ 800–1.050) | klein — vinkje "starter" bij onderneming + doorgeven |
| 3 | **Groene beleggingen** | `groene_beleggingen` | box 3-belegger | vrijstelling ~€ 26k p.p. + heffingskorting 0,1% | klein/middel — input bij box 3 + tonen |
| 4 | **Meewerkaftrek** | `overige_ondernemersaftrek` | partner werkt mee in de zaak | variabel (% van winst) | klein — input meewerk-uren/forfait |

> Prioriteit: **1 (IACK)** maakt de net gebouwde Kinderen-toggle af; **2 (startersaftrek)** is breed
> relevant voor de ZZP-doelgroep. Samen de logische afmakers van "NU".

### B. Nog niet in de rekenkern — bouwen
| # | Optimalisatie | Voor wie | Inspanning |
|---|---|---|---|
| 5 | **KIA / kleinschaligheidsinvesteringsaftrek** | ondernemer met zakelijke investeringen | middel — investeringsbedrag-input + KIA-tabel (art. 3.41) |
| 6 | **Giftenaftrek** (m.n. periodieke giften) | gever aan ANBI | middel — aftrekpost + drempel/plafond |
| 7 | **Partneralimentatie (betaald)** | gescheiden, betaalt alimentatie | klein/middel — box 1-aftrekpost |
| 8 | **Specifieke zorgkosten** | hoge zorgkosten boven drempel | middel — drempel afhankelijk van inkomen |

---

## Vermogen / Straks — verfijningen (eerder besproken)

| # | Item | Waarom | Inspanning |
|---|---|---|---|
| ~~V0~~ | ~~**Pensioen-bewuste lijfrente-cap (omslagpunt lijfrente↔box 3)**~~ ✅ **GEBOUWD 2026-06-29** (fase 23) | — | — |
| V1 | **Leegwaarderatio verhuurwoningen** | box 3-waarde verhuurd huis = WOZ × ratio (<1), niet volle WOZ | klein/middel |
| V2 | **Straks ↔ lijfrente koppelen** | verwacht pensioen automatisch uit Straks-tab i.p.v. apart invullen | klein |
| V3 | **Vastgoed ín de BV** | eigen dynamiek (huur, WOZ, geen box 3-vrijstelling, overdrachtsbelasting) | middel |
| V4 | **Uitkeringsfase lijfrente jaar-voor-jaar** | nu lump-sum op pensioendatum; doorgroei tijdens uitkeren genegeerd (conservatief) | middel — **laag nut**, beide routes groeien evenredig |
| V5 | **Heffingvrij gewogen gemiddelde op BV spaar/beleggen-split** | nu volledig op beleggingen i.p.v. gewogen; ~€ 300–500/jr afwijking | klein |

---

## Onzeker / te verifiëren
- Box 3-forfaits banktegoeden (~1,28%) en schulden (~2,70%) 2026 zijn **voorlopig** — checken bij
  definitieve vaststelling (zie `bronnen/bronregister.md`).
- Hillen-percentage (aftrek geen/lage eigenwoningschuld) gemarkeerd onzeker in params.
