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
| ~~1~~ | ✅ **Giftenaftrek** (gebouwd 2026-07-02, gewoon + periodiek + drempel/plafond, GIFT-*) | — | — |
| ~~2~~ | ✅ **Partneralimentatie** (gebouwd 2026-07-02, persoonsgebonden aftrek + aftopping, ALIM) | — | — |
| ~~3~~ | ✅ **Specifieke zorgkosten** (gebouwd 2026-07-02, drempelstaffel, ZORG-*) | — | — | **Blok B compleet.** |

> Ook gebouwd 2026-07-01 (fase 29): **jaarruimte-correctie factor A** (werkgeverspensioen verlaagt de
> ruimte), **reserveringsruimte-inhaal** (met pensioen-bewuste cap), en de expliciete **cap-uitleg**
> (rendement vs flexibiliteit boven de grens). Zie JOURNAAL.

---

## Vermogen / Straks — verfijningen (eerder besproken)

| # | Item | Waarom | Inspanning |
|---|---|---|---|
| ~~V1~~ | ✅ **Leegwaarderatio verhuurwoningen** (gebouwd 2026-07-02, LEEG-*; vervalt per 2027) | — | — |
| V2 | **AOW naar `params`** | pensioen-inputs zijn al geünificeerd (fase 26–28); alleen de AOW-bedragen (€ 20.929/€ 14.379) staan nog hardcoded in de client — verplaats naar `params` (sourced PEN-03) | klein |
| ~~V3~~ | ✅ **Vastgoed ín de BV** (gebouwd 2026-07-02, box 3 vs BV-vergelijking, OVB-*) | — | — |
| ~~V4~~ | ⏸️ **Uitkeringsfase lijfrente jaar-voor-jaar** — **bewust niet gebouwd** (2026-07-02): lijfrente én box 3 groeien tijdens de uitkering evenredig → verandert de keuze niet, puur cosmetisch. | — | — |
| ~~V5~~ | ⏸️ **Heffingvrij-verdeling op de privé-kant van de BV-vergelijking** — **bewust niet gebouwd** (2026-07-02): heffingvrij is puur box 3/privé (de BV-kant krijgt het terecht níet — Vpb + box 2). Nuance: bij "uitkeren naar box 3" wordt het heffingvrij nu vól op het beleggingen-deel toegepast i.p.v. gewogen over spaar+beleggen → ~€ 300–500/jr in een niche (bestaand BV-vermogen mét beide). Vól op beleggingen = de hoogste-forfait-toewijzing (taxpayer-optimaal); fix raakt de gedeelde uitstel-module voor weinig winst. | — | — |

---

## Product / later (niet-fiscaal)
- **Positionering**: *wij maken de **schatting**, de boekhouder doet de **controle en het
  advies***. Doorgevoerd in de UI-teksten (2026-07-02): header-tagline, welkom-disclaimer,
  "Advies"-subtab → "Schatting", rapport-titel → "Fiscale schatting".
- **Meeneembare PDF voor de boekhouder** — aan het eind een **PDF-export** die de gebruiker
  meeneemt naar de boekhouder (voor de controle + het advies). Waarschijnlijk **betaald**.
  De `.md`-export is nu verborgen (boekhouders werken niet met Markdown); de bouwstenen staan
  er nog (`rapportBtn` met class `hide`, functies `rapport()`/`mdAdvies()` etc.) → basis voor
  de PDF. Later: gestructureerd formaat dat aansluit op aangifte/boekhoudsoftware.

---

## Onzeker / te verifiëren
- Box 3-forfaits banktegoeden (~1,28%) en schulden (~2,70%) 2026 zijn **voorlopig** — checken bij
  definitieve vaststelling (zie `bronnen/bronregister.md`).
- Hillen-percentage (aftrek geen/lage eigenwoningschuld) gemarkeerd onzeker in params.
