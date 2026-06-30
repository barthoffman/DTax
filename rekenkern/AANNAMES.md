# Modelaannames rekenkern

Expliciete aannames en vereenvoudigingen van de rekenkern. De kern is een
**schatting, geen aangifte**. Bedragen in hele euro's per jaar; percentages in de
params als fractie (0,3575 = 35,75%). Bron-ID's verwijzen naar `../bronnen/bronregister.md`.

## Algemeen / vergelijkingsraam
- **A1 — Invariant V.** In de rechtsvormvergelijking is `V` = de **totale economische
  waarde/kosten op activiteitsniveau, inclusief werkgeverslasten**. Voor de werknemer
  wordt het brutoloon uit V teruggerekend; voor de ZZP is V de fiscale winst; voor de
  DGA de bv-winst vóór DGA-loon. Zo zijn de drie vormen eerlijk vergelijkbaar.
- **A2 — Peiljaren.** 2025 en 2026 worden parallel onderhouden; sommige 2026-cijfers
  zijn voorlopig (zie waarschuwingen in de output en `JOURNAAL.md`).

## Zvw (Zorgverzekeringswet bijdrage)
- **Z1 — Eenmalig.** Elke vorm betaalt de inkomensafhankelijke Zvw-bijdrage **precies
  één keer**; geen stapeling. De IB-engine (`bereken_persoon`) rekent zelf géén Zvw —
  `vergelijking.py` telt de bijdrage per vorm eenmalig op.
- **Z2 — Variant per vorm.** Werknemer: **werkgeversheffing** (hoog %, werkgeverskant).
  ZZP en DGA: **lage inkomensafhankelijke bijdrage** (zelf betaald), omdat de
  majoriteits-DGA en de IB-ondernemer niet verzekeringsplichtig zijn voor de
  werknemersverzekeringen.
- **Z3 — Gemaximeerd.** De bijdrage is begrensd op het **maximumbijdrage-inkomen**
  (2025 € 75.864 / 2026 € 79.409). Boven dat inkomen is de Zvw een vast bedrag en
  verandert de marginale vergelijking niet meer.
- **Z4 — Grondslag.** Werknemer: brutoloon. ZZP: belastbare winst (na ondernemersaftrek
  en MKB-winstvrijstelling). DGA: **alleen het gebruikelijk loon**. **Box 2-dividend is
  Zvw-vrij** (Z4 is de kern van het DGA-voordeel in het middenvenster).
- **Z5 — Vereenvoudiging.** De nominale zorgpremie (vaste premie aan de verzekeraar) is
  voor elke vorm gelijk en blijft buiten de vergelijking. Een eventuele
  pensioen-/lijfrentepremie verlaagt de Zvw-grondslag in het model niet.

## DGA / bv
- **D1 — Volledige uitkering.** De bv keert het gebruikelijk loon uit en deelt de
  resterende winst na Vpb **volledig uit als dividend** (box 2). Je kunt niet bij het geld
  zonder Vpb én box 2 te betalen; **box 2-uitstel is alleen timing, geen lagere totale
  druk** en wordt niet als voordeel gemodelleerd.
- **D2 — Gebruikelijk loon** = hoogste van normbedrag (2025 € 56.000 / 2026 € 58.000) en
  een eventueel hoger zakelijk loon, **begrensd op de beschikbare winst**. Dit is de
  **optimistische** aanname (dividend-maximaliserend). **LET OP:** voor inkomen dat de DGA
  consumeert ('eigen gebruik') eist de Belastingdienst loon op het niveau van een
  **vergelijkbare dienstbetrekking** — dan verdampt het dividendvoordeel. Instelbaar via
  `gebruikelijk_loon` (zet = V om de arbeids-/consumptiesituatie te tonen).
- **D3 — Echt BV-voordeel.** Het tariefvoordeel geldt alleen voor winst die het
  gebruikelijk loon overstijgt en die je **niet consumeert**. Het structurele voordeel is
  vooral **uitstel** voor niet-geconsumeerd vermogen. De vaak genoemde **afzondering van
  privévermogen** (beperkte aansprakelijkheid) is in de praktijk **beperkt**: financiers
  eisen meestal een persoonlijke borgstelling (hoofdelijke aansprakelijkheid) en
  bestuurdersaansprakelijkheid (onbehoorlijk bestuur, niet-gemelde betalingsonmacht,
  belasting/premies) kan privé doorwerken. Reële bescherming resteert vooral tegen
  **niet-gegarandeerde** claims van derden (onverzekerde/tort-aansprakelijkheid). Niet-fiscaal.
- **D4 — Vaste kosten.** Boekhouding/jaarrekening (BV ~€ 2.000, ZZP ~€ 900/jr) = aftrekbaar.
  Oprichtingskosten (BV ~€ 600, KvK ~€ 80) = eenmalig, **niet-aftrekbaar**, geamortiseerd
  over de horizon (default 10 jr; aanname: men switcht niet terug). Alle bedragen indicatief
  en instelbaar; geen wettelijke parameters.
- **D5 — Excessief lenen** (€ 500.000) en herinvestering in de bv blijven buiten beschouwing.

## Onderneming (IB-ondernemer / ZZP)
- **O1 — Volgorde.** winst − ondernemersaftrek = winst na ondernemersaftrek; daarover de
  MKB-winstvrijstelling (12,7%); resultaat = belastbare winst (box 1).
- **O2 — Zelfstandigenaftrek** wordt voor niet-starters begrensd tot de winst (geen
  verlies creëren); het niet-benutte deel is voortwentelbaar maar wordt **niet
  bijgehouden**.
- **O3 — MKB-winstvrijstelling** alleen over **positieve** winst na ondernemersaftrek.
- **O4 — Tariefaanpassing (art. 2.10a)** drukt ook op ondernemersaftrek + MKB-vrijstelling
  (afgetopt aftrektarief, max 37,48% (2025) / 37,56% (2026) in de topschijf).

## Box 1 / heffingskortingen / box 3
- **B1 — Arbeidskorting boven AOW-leeftijd** is benaderd via een schaalfactor
  (max_aow / max_onder_aow); exacte AOW-segmenttabel staat nog niet in de params.
- **B2 — Verzilvering (art. 8.8):** heffingskorting maximaal de verschuldigde heffing;
  het meerdere verdampt. **Uitbetaling minstverdienende partner (art. 8.9, geboren
  < 1963) is niet gemodelleerd.**
- **B3 — Box 3** is alleen **forfaitair**; de tegenbewijsregeling/werkelijk rendement
  (OWR) wordt nog niet doorgerekend. Heffingvrij vermogen per persoon.
- **B4 — Pensioen-equivalent** is een aftrekbare reservering (`pensioen_pct × V`), gelijk
  voor elke vorm; **geen belasting** (blijft vermogen), verlaagt wel de actuele heffing.

## Werknemersverzekeringen (WW/WIA)
- **W1 — Werkgeverslast in V.** WW (Awf) + WIA (Aof) + Whk zijn werkgeverspremies die
  deel zijn van de totale kosten V; voor de werknemer wordt het brutoloon eruit
  teruggerekend. **Default-profiel: kleine werkgever, vast contract** (Awf laag + Aof laag
  + Whk gemiddeld), gemaximeerd op het maximumpremieloon (= max. Zvw-bijdrageloon).
- **W2 — Whk indicatief.** Whk is een gemiddelde; feitelijk werkgever-specifiek. Markeren
  als variabel.
- **W3 — DGA/ZZP niet verzekerd.** Geen WW/WIA-premie én geen WW/WIA-recht; privé-AOV is
  niet gemodelleerd.
- **W4 — Premie met aanspraak.** WW/WIA telt niet mee in `totale_belasting` (zuivere druk)
  maar wel in `totale_wig`. Reden: het koopt verzekering, het is geen zuivere heffing.

## Box 3-tegenbewijs, pensioen, toeslagen, toerekening
- **TB1 — Tegenbewijs box 3.** Bij `werkelijk_rendement_pct` lager dan het forfait wordt
  over het werkelijke rendement geheven (eenzijdig naar beneden). In de motor staat
  `tegenbewijs_box3=True` default → box 3 ≤ BV op tariefbasis (BV-voordeel = enkel uitstel).
- **PEN1 — Jaarruimte (art. 3.127).** Factor A (werkgeverspensioen-aangroei) = 0 tenzij
  opgegeven; geldt dus zuiver voor ZZP/DGA. Premiegevend inkomen ≈ economische waarde.
- **HT1 — Huurtoeslag.** 2026 lineaire afbouw = exact; **2025 = benadering** (officieel
  kwadratische eigen-bijdrage), gemarkeerd via param `structuur`. Hoge aftoppingsgrens bij
  ≥ 3 personen, anders lage. Jongeren < 23 niet apart gemodelleerd.
- **KOT1 — Kinderopvangtoeslag.** Vergoedings% lineair benaderd tussen de twee
  inkomensankers (officieel staffel Bijlage I). Per kind; situationeel (opvangsoort/uren/tarief).
- **AR1 — Toerekening (art. 2.17).** Optimizer dekt alleen de eigen woning. Toeslagen zijn
  toerekening-invariant (gezamenlijk toetsingsinkomen). Box 3-grondslagverdeling is voor
  partners tarief-invariant (2× heffingvrij, vlak 36%); effect alleen via AHK-afbouw —
  niet in de optimizer.

## Nog niet gemodelleerd (op de rol)
- Huurtoeslag 2025 exact (kwadratische eigen-bijdrage); kinderopvang-staffel exact (Bijlage I).
- Box 3-partnerverdeling AHK-afbouweffect in de toerekening-optimizer.
- Privé-AOV / broodfonds als ZZP/DGA-equivalent van WW/WIA.
