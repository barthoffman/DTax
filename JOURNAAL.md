# Journaal — beslissingen en bevindingen

Chronologisch log van belangrijke keuzes, bevindingen en open punten. Nieuwste
bovenaan. Elke entry: datum, type (BESLISSING / BEVINDING / CORRECTIE / OPEN PUNT),
korte tekst, en waar relevant de bron-ID of het KB-bestand.

> Onderhoud: dit journaal wordt elke werksessie bijgewerkt (zie `CLAUDE.md`).
> Datums zijn absoluut (geen "vandaag/gisteren").

---

## 2026-06-30 — Fase 24: git-repo, TOL-max geverifieerd, update-kalender

- **BESLISSING — git-repo opgezet** op `git@github.com:barthoffman/DTax.git` (main, initial commit
  52 bestanden, `.gitignore` voor `__pycache__`/logs/`.claude/settings.local.json`).
- **BEVINDING — max. tijdelijke oudedagslijfrente 2026 geverifieerd (PEN-15):** € 27.192
  (verzekering) / € 26.781 (banksparen/beleggingsrecht), 1e jaar; min. looptijd 5 jr. Bron:
  Belastingdienst fisin2026. In BEVINDINGEN §3 verwerkt; het eerder als "te verifiëren" gemarkeerde
  bedrag is nu vastgelegd.
- **BESLISSING — update-kalender** toegevoegd aan `bronregister.md`: per parameter-categorie wanneer
  de 2027-waarde beschikbaar komt (voorstel Prinsjesdag sep, definitief dec; `fisin2027` dec/jan;
  voorlopige box 3-forfaits pas begin 2027). Jaarlijkse update-actie beschreven.

---

## 2026-06-29 — Fase 23: pensioen-bewuste lijfrente-cap + lijfrente bij overlijden

- **BESLISSING — lijfrente-cap (omslagpunt lijfrente↔box 3) gebouwd** (was backlog V0). De
  allocator stopte de hele jaarruimte in lijfrente; nu vult hij tot de uitkering box 1 raakt tot
  de schijfgrens onder je marginale tarief nu (49,5%→€ 78.426, 37,56%→€ 38.883), gestapeld op
  `verwacht_pensioen` (AOW + 2e pijler). Rest → box 3. `vermogensadvies.py` (+`verwacht_pensioen`,
  `lijfrente_optimaal`), API, Advies-tab (veld + cap-uitleg). Voorbeeld 35.588 jaarruimte/20 jr:
  49,5% nu → vol; 37,56% nu → € 21.140 lijfrente + € 14.448 box 3; + € 30k pensioen → € 4.830.
- **BEVINDING — lijfrente bij overlijden (PEN-13, PEN-14).** Geverifieerd op 2026-06-29: bancaire
  lijfrente looptijd 20 jr (+ jaren tot AOW bij eerder starten; min. 5 jr ín AOW-jaar), uiterste
  ingangsdatum AOW-leeftijd + 5 jr (art. 3.126a). Bij overlijden: erfgenamen box 1 over uitkeringen
  (uitgestelde IB komt terug) + erfbelasting op waarde −30% latente IB; partner → imputatie (½ van
  pensioen/lijfrente op de vrijstelling), kind → geen imputatie. Levenslange verzekering zonder
  restitutie vervalt aan verzekeraar. Lijfrente = uitstel-, geen ontwijkingsvehikel. In BEVINDINGEN
  §3 verwerkt.

---

## 2026-06-29 — Fase 22: backlog aangelegd

- **OPEN PUNT — `BACKLOG.md` aangemaakt.** "NU" is nog niet compleet: de rekenkern ondersteunt
  IACK (`jongste_kind_leeftijd`), startersaftrek (`starter`), groene beleggingen
  (`groene_beleggingen`) en meewerkaftrek (`overige_ondernemersaftrek`), maar `optimalisatie_advies`
  geeft die velden niet door en toont ze niet. Plus niet-in-engine: KIA, giftenaftrek,
  partneralimentatie, specifieke zorgkosten. Prioriteit IACK + startersaftrek (afmakers). Verfijningen
  Vermogen/Straks (leegwaarderatio, Straks↔lijfrente, vastgoed in BV, heffingvrij gewogen gemiddelde)
  ook op de backlog. Zie `BACKLOG.md`.

---

## 2026-06-29 — Fase 21: realistisch lijfrente-opnametarief, box 2-dividendplanning, box 3-schulden

- **BEVINDING — opnametarief lijfrente is geen 17,85%.** De 17,85% (AOW-schijf 1) geldt alleen
  tot € 38.883 (2026); daarboven 37,56% (tot € 78.426), dan 49,5%. AOW (~€ 19.650 alleenstaand)
  + tweede-pijler pensioen vullen die schijf al; de lijfrente-uitkering stapelt erbovenop. Spaargeld/
  beleggingen tellen NIET mee (box 3). Voorbeeld € 35.588 inleg/15 jr/6%/marginaal 49,5%: voordeel
  zakt van € 26.994 (17,85%) naar € 10.183 (37,56%). Breakeven = marginaal tarief nu. Bron: B1-tarief
  (`schijven_vanaf_aow`).
- **BESLISSING — realistisch opnametarief berekenen.** `vergelijk_lijfrente` krijgt `overig_pensioen`
  + `uitkeringsjaren`; opnametarief = blended box 1-tarief op de uitkering (pot ÷ uitkeringsjaren)
  gestapeld op AOW + pensioen. UI: veld "Verwacht pensioen straks (van pensioenoverzicht)" in de
  Lijfrente-sub-tab; leeg = oude aanname. Bij hoog pensioen wint privé beleggen.
- **BESLISSING — lijfrente gesplitst over de flow.** Meerjarig groeivoordeel weg uit *Mijn belasting*
  (alleen de jaarlijkse aftrek-besparing blijft) → naar *Vermogen → Lijfrente*, voorgevuld met de
  jaarruimte en auto-doorgerekend. "Leg dit in" (NU) ↔ "groeit belastingvrij" (VERMOGEN).
- **BESLISSING — box 2-dividendplanning** (`dividendplan.py`, `/dividendplan`, sub-tab "Dividend"):
  optimaal spreiden onder de 24,5%-grens (€ 68.843 p.p., 2× met partner) i.p.v. 31%. Bron: DGA-04.
- **BESLISSING — BV-vermogen gesplitst** in BV-spaargeld + BV-beleggingen; uitkeer-route met de juiste
  box 3-forfaits (banktegoeden vs overige). Veld verhuisd naar *Vermogen* (zakelijk), alleen bij een BV.
- **BEVINDING — box 3-schulden & vastgoed.** 2e woning/verhuur = box 3 (waarde 6%, hypotheek = schuld
  2,70% na drempel € 3.800 p.p.); eigen woning = box 1. **Lenen om box 3-belasting te verlagen loont
  niet**: ~0,97%/jaar besparing (2,70% × 36%) vs 4–5% rente. UI: `mixSchulden`-veld + waarschuwing.
- **BESLISSING — UX**: lege-staat/uitlegscherm zolang geen inkomen ingevuld; "Je vermogen" toont nu
  het totale box 3-vermogen (incl. spaargeld + schulden) i.p.v. alleen beleggingen; progressieve
  onthulling met checkboxes (Partner/Kinderen/Woning/Spaargeld) en velden eronder.

---

## 2026-06-29 — Fase 20: bestaande DGA + gebruikelijk-loon-nuance + Loon-kolom

- **Inkomenstype "Winst via eigen BV (DGA)"**: `huidige_vorm` param in `optimalisatie_advies`;
  baseline = de huidige vorm (ZZP of bestaande BV) via `_operationeel`. Een bestaande DGA ziet nu
  zijn echte BV-IB als "Je betaalt nu" en krijgt geen overstap-suggestie als BV al optimaal is.
  Rechtsvorm-suggestie + UI-tekst nu "t.o.v. je huidige vorm" i.p.v. altijd ZZP.
- **UX**: "Loon"-kolom in de waarom-tabel + de meer_loon-optie alleen tonen als er echt loon is
  (`heeftLoon = s.loon > 0`).
- **BEVINDING (gebruiker + bron)**: voor een parttime DGA is de **doelmatigheidsmarge** (75%/25%
  korting) afgeschaft per 2023; een lager gebruikelijk loon dan het normbedrag mág nog wél áls je
  het onderbouwt (meest vergelijkbare dienstbetrekking), met "aantoonbaar deeltijdwerk" als geldige
  grond, bewijslast bij de DGA. Bron: jongbloed-fiscaaljuristen.nl, dezaak.nl (zie bronregister
  DGA-08). Dashboard vangt dit met het handmatige gebruikelijk-loon-veld (default = normbedrag).
- **BEVINDING**: een DGA die (ook) in dienst treedt — baan-loon stapelt met gebruikelijk loon in
  box 1 (hoger marginaal), loon/dividend-balans schuift richting dividend. Model deed dit al correct.
- 51 tests groen.

## 2026-06-29 — Fase 19: consistente optimale route (correctie dubbeltelling)

- **CORRECTIE (gebruiker)**: de optimalisaties werden los op de ZZP-situatie berekend en opgeteld,
  terwijl ze interacteren. Sterkst bij rechtsvorm ↔ lijfrente: jaarruimte ZZP € 35.588 vs BV
  € 11.648 (op gebruikelijk loon). `advies.py` herstructureerd: **rechtsvorm EERST**, dan een
  "operationele persoon" voor de gekozen vorm (BV: loon+gebruikelijk loon, dividend via box 2,
  Vpb+overhead), en lijfrente/toerekening worden HIEROP doorgerekend. `_huishouden` kreeg
  box2 + extra_heffing.
- **Effect** (0 loon + 250k ZZP, partner 45k, BV aangeraden): totaal potentieel **€ 21.302 →
  € 7.901**; lijfrente nu € 11.648 @ 37,6% i.p.v. € 35.588 @ ~49,5%. De som klopt nu wél.
- **Bevestigd (gebruiker)**: gebruikelijk loon € 58k is loonkosten (van winst af vóór Vpb),
  belast in box 1 i.p.v. Vpb+box 2 — zat al correct in de motor.
- 51 tests groen.

## 2026-06-29 — Fase 18: flow als primaire navigatie

- **BESLISSING (gebruiker)**: de hoofdtabs vervangen door een **horizontale flow-navigatie**
  bovenaan (minimale labels; info op de pagina's). NU → Privé vermogen → Privé straks, met een
  tweede "+ BV"-baan (Zakelijk vermogen → Bedrijf straks, opnemen → privé box 2). Klik = navigeren
  naar tab + sub-tab; actieve stap gemarkeerd.
- **Zonder BV geen zakelijke baan**: de "+ BV"-baan verschijnt alleen als er een bestaand
  BV-vermogen is ingevuld (`mixBv > 0`). Hoofdtabs (`#hoofdtabs`) verborgen maar functioneel.
- 51 tests groen (UI-only wijziging).

## 2026-06-29 — Fase 17: privé/zakelijk scheiden + model-diagram

- **CORRECTIE**: de allocator toonde de BV-container voor iederéén met winst (ook ZZP zonder BV).
  Nu alleen als je een BV hébt (bestaand BV-vermogen) of als een BV wordt aangeraden
  (rechtsvorm.beste == "bv"). Containers gelabeld **privé** / **zakelijk**.
- **Model-diagram** bovenaan (klikbaar → tabs): NU → Vermogen (privé: sparen/beleggen/lijfrente;
  zakelijk: BV) → Straks. Maakt de potjes en de stroom expliciet voor leken.
- **BEVINDING (gebruiker)**: geen "zakelijke lijfrente" meer — pensioen in eigen beheer is per
  2017 afgeschaft (alleen afbouwende ODV rest). DGA bouwt lijfrente privé op. De BV is een aparte
  entiteit die zakelijk kan sparen/beleggen (buffers, Vpb op rendement) en zelfstandig doordraait;
  opnemen naar privé = box 2. Opgenomen in [[bv-uitstel-inzicht]].
- 51 tests groen.

## 2026-06-29 — Fase 16: overzichtelijk (inklappen) + vangrails

- **Mijn belasting volledig inklapbaar**: elke uitkomst (rechtsvorm met geneste "Waarom",
  vermogen, lijfrente, "wat is verstandig") is nu een `<details>` met het kerncijfer in de
  titel. Hoofdregel zichtbaar, precieze opbouw openklikken. Sluit aan op de missie: belasting
  begrijpelijk maken voor leken.
- **Vangrail extreme horizon**: bij > 45 jaar (bv. leeftijd 4 → 63 jaar) een waarschuwing dat de
  projectie illustratief is (constante inleg/rendement, nominale bedragen lopen extreem op).
- **Spaargeld groeit mee**: bestaand spaargeld groeit tegen de banktegoeden-rente (forfait
  ~1,28%) door naar pensioen; Straks-knop vult het doorgegroeide saldo in.
- 51 tests groen.

## 2026-06-29 — Fase 15: UX + spreiding/uitkeringsrecht

- **BEVINDING (lijfrente, twee fasen)**: opbouwfase (pot) → uitkeringsfase (op pensioendatum
  eenmalig een **uitkeringsrecht** kopen dat de periodieke uitkering regelt). Opname-in-één-keer
  mag niet (revisierente). Spreiden is de fiscale optimalisatie: vlakker/langer spreiden houdt
  meer in de lage AOW-schijf (~17,9%). Looptijd binnen wettelijke grenzen (banksparen ≥5 jr,
  verzekeraar levenslang). Opgenomen in `BEVINDINGEN.md`. Zie [[bv-uitstel-inzicht]].
- **Spreiding instelbaar**: "Uitkeringsjaren" in de allocator (was vast 20) → projectie + Straks
  reageren erop.
- **UX**: per-persoon uitsplitsing inklapbaar (`<details>`), select-on-focus bij getalvelden,
  `value="0"` → `placeholder="0"`, leeftijd-label verduidelijkt, box 3-velden in Straks gevuld
  vanuit NU (bestaand vermogen doorgegroeid + nieuwe inleg).
- 51 tests groen.

## 2026-06-29 — Fase 14: inflatiecorrectie in de projectie

- **Inflatie toegevoegd** aan de vermogensprojectie (default 2%): naast nominale potten/uitkeringen
  nu ook **reëel** (euro's van nu). Voorbeeld: € 27.589 nominaal → € 18.567 reëel na 20 jaar @2%.
- **BEVINDING**: inflatie deflateert lijfrente/box 3/BV ~evenredig → verandert de **keuze** tussen
  containers nauwelijks, maar is cruciaal voor de getoonde **koopkracht** (voorkomt dat een grote
  nominale pot misleidt). Tweede-orde: box 3/BV worden nominaal belast (forfait/Vpb), dus in hoge
  inflatie iets ongunstiger dan lijfrente — maar dat zit al in het nominale model.
- 51 tests groen.

## 2026-06-29 — Fase 13: opbouw → uitkering gekoppeld (sluitstuk)

- **Projectie in de allocator** (`vermogensadvies` + `_fv_annuity`): de jaarlijkse inleg per
  container groeit (annuïteit-FV) tot een **pot bij pensioen**; pot ÷ uitkeringsjaren =
  jaarlijkse uitkering. Lijfrente belastingvrij (box 1 bij opname), box 3 netto, BV ×(1−Vpb).
- **Straks-knop "Vul in vanuit mijn opbouw"**: leest tab 1 (`tab1Body`) + allocator (`vaBody`),
  neemt de geprojecteerde uitkeringen over (lijfrente-uitkering, BV-dividend, box 3-vermogen)
  en rekent de pensioenfase door. Hiermee loopt het hele model van inleg-NU tot uitkering-STRAKS
  in één doorrekening — de cirkel die de gebruiker beschreef.
- Helpers `tab1Body()`/`vaBody()` ontdubbelen de verzoekopbouw over de tabs. 51 tests groen.

## 2026-06-29 — Fase 12: levensloop NU → groei → STRAKS

- **Tab "Straks" (pensioenfase)** + `/straks`: AOW + pensioen/lijfrente-uitkering (box 1 op
  AOW-tarieven + ouderenkorting) + BV-dividend (box 2) + box 3. Toont wat je STRAKS betaalt en
  netto overhoudt — sluit de cirkel: opname is weer inkomen, maar tegen lagere AOW-tarieven.
  Dat maakt het uitstelvoordeel van lijfrente/pensioen concreet.
- **Tab 1 uitgebreid**: leeftijd (→ AOW-datum, 67 − leeftijd = horizon voor de allocator) +
  bestaand BV-vermogen (gevraagd "bij belasting NU"). De allocator leest beide.
- **Lijfrente zit vast tot pensioen** (gebruikerspunt): daarom is het in de allocator de
  "vastzetten"-container en wordt het in Straks een uitkering; de leeftijd bepaalt wanneer.
- Drie hoofdtabs nu: Mijn belasting (NU) · Vermogen & BV (groei) · Straks (pensioen). 50 tests groen.

## 2026-06-29 — Fase 11: vermogensallocatie (unificatie tab 2)

- **`vermogensadvies.py` + `/vermogensadvies` + sub-tab "Advies"** (standaard in Vermogen & BV):
  unificeert lijfrente / box 3 / BV-retentie tot één **watervalallocatie** van de nieuwe inleg,
  + analyse bestaand box 3- en BV-vermogen. **Prefilt vanuit Mijn belasting** (besparing als
  nieuwe inleg, box 3-vermogen, jaarruimte, marginaal tarief, rendement, horizon) — geen dubbele
  invoer. Eigen velden: bestaand BV-vermogen + "vrij/liquide houden".
- **Model (gebruiker)**: tab 1 = stroom (wat betaal/bespaar ik nu), tab 2 = voorraad (waar laat
  ik het renderen). De cirkel is in de modellen al gesloten: elke projectie rekent de
  eindheffing bij opname (box 2 / box 1) al mee.
- **Liquiditeitsregel**: vrij te houden bedrag = noodbuffer (3–6 mnd lasten) + geplande uitgaven
  vóór pensioen → box 3; de rest tot de jaarruimte → lijfrente; overschot → gunstigste rest.
- Detail-sub-tabs (Beleggingsgroei/BV-uitstel/Lijfrente) blijven als verdieping. 50 tests groen.

## 2026-06-29 — Fase 10: lijfrente-model, uitsplitsing & uitleg

- **Lijfrente-doorrekening** (`lijfrente.py` + `/lijfrente` + sub-tab Vermogen & BV): meerjarig
  lijfrente (aftrek + belastingvrije groei + box 1 bij opname) vs. privé box 3. Met
  breakeven-opnametarief. Heffingvrij toegepast op de privé-route.
- **BEVINDING (pensioen, geverifieerd tegen Brand New Day-FAQ)**: lijfrenteverzekering /
  banksparen / pensioenbeleggen zijn verschillende **producten** maar fiscaal **identiek**
  (derde pijler, afd. 3.7 Wet IB): zelfde aftrek, box 3-vrijstelling, box 1 bij opname.
  Verschil: uitkeringsduur (verzekering kan levenslang; banksparen vaste termijn 5–30 jr),
  overlijden (banksparen/beleggen → erfgenamen; verzekering kan aan verzekeraar vervallen),
  kosten/risico. Gebruikersaanname "uitkeren = geen voordeel" onderschat de box 3-vrijstelling
  + tariefarbitrage. Zie [[bv-uitstel-inzicht]].
- **BV-opstartkosten** nu in de rechtsvormvergelijking (geamortiseerde oprichting naast
  jaarlijkse administratie) + zichtbaar als regel.
- **Uitsplitsing terug + componenten-tabel** in *Mijn belasting*: per-persoon breakdown
  (box 1/box 3/te betalen) + loon/ZZP/DGA-tabel met normbedrag, Vpb, box 2 → verklaart wáárom
  ZZP/BV wint. Plus regel "belastingdruk daalt van X naar X−potentieel".
- 49 tests groen.

## 2026-06-29 — Fase 9: rechtsvorm + vermogen gekoppeld aan de persoon

- **Ondernemingsvorm-tab vervallen.** De ZZP/BV/loon-vergelijking gebeurt nu vóór de persoon
  in *Mijn belasting*, inclusief een **omslagpunt**: vanaf welk ondernemersinkomen wint de BV
  (situatie-afhankelijk; zonder ander inkomen ± € 130.000). `advies.py` scant dit via
  `bereken_mix`. Nog 2 tabs: Mijn belasting + Vermogen & BV.
- **Vermogensanalyse gekoppeld** aan de box 3-beleggingen + rendement/horizon uit *Mijn
  belasting*: `optimalisatie_advies` geeft nu een `vermogen`-blok (box 3-last nu +
  BV-uitstel-vergelijking via `vergelijk_uitstel`). UI toont box 3-kosten/jaar + of
  accumuleren in een BV of box 3 meer oplevert + omslagrendement. Kanttekening in de UI:
  alleen actionabel voor ondernemers die winst kunnen oppotten (privé al-belast vermogen
  verplaats je niet naar een BV).
- **Inzicht (uitleg aan gebruiker)**: twee losse BV-voordelen — (1) inkomenskant: winst boven
  gebruikelijk loon @38,8% < 49,5% (= omslagpunt); (2) vermogenskant: uitstel, alleen gunstig
  bij groot + gematigd rendement (<~11%) + lang + niet-consumeren. Anders wint box 3
  (heffingvrij + tegenbewijs). Zie [[bv-uitstel-inzicht]].
- 49 tests groen.

## 2026-06-29 — Fase 8: perspectiefwissel naar de gebruiker

- **MISSIE (gebruiker)**: het dashboard laat mensen de fiscale keuze zélf begrijpen/voorleggen
  zonder eerst een expert nodig te hebben. Begin bij de gebruiker, niet bij de belastingstructuur.
- **Geen "optimaliseer ja/nee"-schakelaar meer.** Iedereen wil de beste route binnen de wet;
  toon die meteen. "Mijn belasting" is nu de standaard-tab en het hoofdscherm.
- **Eén invoerscherm** met "+ inkomensbestanddeel" (dynamische lijst, hergebruikt `bronRij`).
  Het ondernemersinkomen dat je invult ÍS de variabele die geoptimaliseerd wordt.
- `advies.py` omgebouwd: parameter `ondernemer_inkomen` (i.p.v. losse winst+extra); baseline =
  loon + ondernemersinkomen als ZZP; `rechtsvorm`-vergelijking (ZZP/BV/loon) in de respons +
  "BV i.p.v. ZZP"-suggestie. UI toont meteen: wat je nu betaalt + beste rechtsvorm
  (BV wel/niet verstandig) + gekwantificeerde optimalisaties. Rapport (`mdAdvies`) idem.
- 49 tests groen.

## 2026-06-29 — Fase 7: dashboard naar 3 tabs

- **BESLISSING** — 5 tabs → **3**: **Ondernemingsvorm** (vergelijk), **Mijn belasting**
  (Werkelijk + Mix samengevoegd, met schakelaar "optimaliseer een extra activiteit: ja/nee"),
  **Vermogen & BV** (Beleggen + BV-uitstel via sub-tabs). Werkelijk losse tab vervallen
  (geabsorbeerd: extra=0 = je echte belasting). `bereken_mix` kreeg een **winst-basis**
  (`vast_winst`) zodat een ZZP'er z'n echte situatie ook ziet.
- **CORRECTIE/verduidelijking (gebruiker)** — Het uitstel-omslagpunt ~11,4% is het
  RENDEMENT op het opgepotte kapitaal, NIET de winst. < 11,4% rendement + accumuleren →
  BV; daarboven box 3.
- **Volgende (gebruiker: ja)** — optimalisatiemotor verbreden: lijfrente/jaarruimte,
  partnertoerekening, box 3-mix, toeslaggrenzen — naast de rechtsvorm/BV. Nog te doen.
- 48 tests groen.

## 2026-06-29 — Fase 6: uitstelmodel + kinderopvang-UI + dataverificatie

- **CORRECTIE eerdere claim** — "box 3 ≤ BV, uitstel illusoir" was te stellig. Het hangt af
  van CONSUMEREN vs ACCUMULEREN. `uitstel.py` + `POST /uitstel` + tab "BV-uitstel": geld in
  de BV laten (jaarlijks Vpb ~19%, box 2 uitgesteld) vs nu uitkeren (box 2) + privé box 3.
  Box 2 valt weg in de vergelijking (beide betalen 'm); winnaar = snelste jaarlijkse netto
  groei. **Omslagrendement = forfait×36%/Vpb ≈ 11,4%**: eronder wint de BV (accumulatie),
  erboven box 3 (forfait ondertaxeert hoog rendement). Bevestigt: BV is een echt
  ACCUMULATIE-/uitstelvehikel bij gematigd rendement — niet voor consumptie.
- **Kinderopvangtoeslag in de UI** (Mix-tab): velden soort/uren/tarief/aantal; backend
  `bereken_toeslagen` rekent per kind. Tevens bug gefixt: `_profiel_from_json` parste
  rekenhuur niet → huurtoeslag kwam nooit aan via de API; nu wel.
- **Dataverificatie 2026 (2026-06-29)**: 3 agents, alles BEVESTIGD tegen primaire bronnen
  (incl. Hillen 71,867%). Correctie arbeidskorting-nihilgrens € 132.921 → € 132.920.
  Box 3-forfaits banktegoeden/schulden officieel nog voorlopig; Whk indicatief. Stempel in
  `bronregister.md`.
- **Design (gebruiker)**: tabs samenvoegen tot 3 — Vergelijk ondernemingsvorm / Belastingdruk
  individu (optimaliseer ja-nee = Werkelijk+Mix) / Waar helpt een BV (uitstel). + bredere
  optimalisatiemotor (lijfrente, toerekening, box 3-mix, toeslaggrenzen). Volgende stap.
- 48 tests groen.

## 2026-06-29 — Fase 5b: box 3-categorieën in Beleggen + USECASE-bevindingen

- **BEVINDING (vraag gebruiker)** — Box 3 kent precies **drie categorieën** (Overbruggingswet):
  banktegoeden/spaargeld (~1,28%), overige bezittingen/beleggingen (6,00%), schulden (~2,70%,
  boven drempel). Meer niet. De Beleggen-tab behandelde alles als beleggingen; nu gesplitst.
  `box3_last` verwerkt nu ook schulden. Effect: € 100k spaargeld → box 3 € 187 vs beleggingen
  € 878 (factor ~4,7).
- **DOC** — Beleggings-bevindingen vastgelegd als **Use case 2 — de belegger** in `USECASE.md`
  (kwalificatie box 3 ↔ box 1, marginale-tarief-afhankelijkheid, optimalisatieprincipe, paradox).
- 46 tests groen.

## 2026-06-29 — Fase 5: vierde scenario "Beleggen" (kwalificatie groei)

- **BESLISSING** — `beleggingsgroei.py` + `POST /beleggingsgroei` + 4e tab "Beleggen":
  hoe wordt beleggings-GROEI belast — **box 3** (forfait/tegenbewijs) vs **box 1 ROW**
  (art. 3.90/3.91) vs **box 1 winst** (MKB) vs **BV** (Vpb+box 2). Geen vrije keuze maar
  kwalificatie (normaal vermogensbeheer); expliciet als interpretatieruimte/onderbouwd
  standpunt gemarkeerd.
- **BEVINDING** — Het hangt af van het **marginale tarief**:
  - hoog overig inkomen (€ 80k): box 3 **8,8%** « BV 38,9% « winst 50,4% « ROW 56%
    (de hoge box 1-tarieven incl. arbeidskorting-afbouw + tariefaanpassing).
  - géén overig inkomen: ROW/winst **0%** (heffingskortingen absorberen) < box 3 8,8%.
  → Voor de vermogende belegger is box 3 (normaal vermogensbeheer) veruit het gunstigst;
  het risico is herkwalificatie naar box 1 bij te actief/arbeidsintensief beleggen.
- 46 tests groen. Rapport ook voor deze modus.

- **BEVINDING (vraag gebruiker)** — Box 3 bepaalt de mix-keuze NIET: het is een constante
  over alle drie de opties (zelfde vermogen/persoon). Met én zonder box 3 is het verschil
  ZZP↔BV identiek (€ 59). Wat de keuze tipt is het **urencriterium** (zelfstandigenaftrek):
  mét → ZZP wint (€ 335); zonder → BV (€ 59). Dubbeltje op z'n kant bij € 280k.
- **BESLISSING** — Box 3 was wel onverklaard in de detail. Nu een **uitsplitsing**
  (grondslag − heffingvrij vermogen, forfaitair % sparen/beleggen, tegenbewijs ja/nee) in
  zowel Mix als Werkelijk: € 200k − € 59.357 heffingvrij, 2,93% forfait × 36% = € 1.485
  (effectief 0,7% van het vermogen — dát is het box 3-"voordeel"). 45 tests groen.

- **BESLISSING** — Mix toont nu onder de vergelijkingstabel de **volledige uitsplitsing van
  de beste optie** (jij/partner: box 1/2/3, kortingen, Vpb+overhead voor BV, huishoudtotaal),
  zoals "Werkelijk". `bereken_mix` geeft `detail_beste` terug.
- **TRANSPARANTIE (vraag gebruiker)** — Toeslagen waren onzichtbaar omdat ze bij hoog
  inkomen € 0 zijn; nu expliciet gemeld ("geen zorg-/huur-/KGB boven de afbouwgrenzen").
  **Kinderopvangtoeslag** is wél in de engine maar nog NIET in de UI gekoppeld (situationeel:
  opvanguren/-tarief; géén harde inkomensgrens). Als waarschuwing benoemd; UI-koppeling open.
- 45 tests groen.

- **FIX** — Number-inputs met grote `step` (bv. WOZ step 10.000) markeerden geldige
  bedragen als ongeldig (€ 575.000); + de Bereken-knop was per ongeluk een submit-knop
  → formuliervalidatie blokkeerde herberekening. Opgelost: knop `type="button"` en alle
  bedragvelden `step="any"`.
- **BESLISSING** — Mix toont nu ook de **totale belastingdruk** (huishouden-belasting +
  gemiddeld tarief), en het **rapport is in elke modus** te genereren (vergelijk via
  `/rapport`; werkelijk/mix client-side opgebouwd + `GET /grondslag` voor wettelijke
  grondslag + disclaimer). Zo hoeft niemand na het invullen van tab te wisselen. 45 tests groen.

- **BESLISSING** — Persona's per tab: **Vergelijken** (BV-/rechtsvorm-interesse),
  **Werkelijk** (gewone individuen), **Mix** (werken + iets ernaast). Mix is nu een
  **volledige situatie**: vast loon + extra + partner + box 3 + eigen woning + kinderen
  → per vorm van de extra het **huishouden-netto** (incl. toeslagen). `bereken_mix`
  uitgebreid; `/mix` accepteert de volledige context.
- **CORRECTIE (gebruiker) — afscherming privévermogen is grotendeels een wassen neus.**
  Banken eisen meestal een **persoonlijke borgstelling** (hoofdelijke aansprakelijkheid);
  **bestuurdersaansprakelijkheid** werkt privé door. Reële bescherming resteert vooral
  tegen niet-gegarandeerde claims van derden. Eerder te stellig als BV-voordeel neergezet;
  nu genuanceerd in motor-tip, mix-waarschuwing, `AANNAMES.md` (D3) en `USECASE.md`.
  Het structurele BV-voordeel blijft daarmee vooral **uitstel** voor niet-geconsumeerd vermogen.
- 45 tests groen.

---

## 2026-06-29 — Fase 4c: mix-modus, partner, box 3 sparen/beleggen

Drie uitbreidingen op verzoek (44 tests groen):
- **Mix (derde tab)** — `mix.py` + `POST /mix`: gegeven vast loon, gunstigste vorm voor
  EXTRA activiteit (meer loon / ZZP / BV), marginaal bovenop het loon. Bevinding: kleine
  bijverdienste (< normbedrag) → BV zinloos (alles loon + overhead, 56% marginaal); ZZP
  wint via MKB-vrijstelling (42%). Maakt de gebruikelijk-loon-/eigen-gebruik-logica concreet.
- **Partner in "Werkelijk inkomen"** — `/bereken` accepteert een `partner`-blok (eigen
  inkomstenbronnen) → per persoon + huishoudtotalen.
- **Box 3 sparen vs beleggen** — `box3_last` is nu categorie-bewust (banktegoeden-forfait
  ~1,3% vs overige ~6%); `Situatie` splitst `spaargeld` en `prive_vermogen` (beleggingen).
  Dashboard heeft aparte velden. De engine kon dit al per categorie; de motor trok het recht.
- Dashboard: 3 tabs (Vergelijken / Werkelijk / Mix), box 3-splitsing, partner-bronnen.

---

## 2026-06-29 — Fase 4b: licht/donker-thema + "werkelijk inkomen"-modus

- **FIX** — Cosmetische bug: duizendtal-opmaak (`,`→`.`) werd op hele tip-zinnen toegepast
  → komma's werden punten. Nu alleen op het bedrag (zichtbaar geworden door de live pagina).
- **BESLISSING** — Licht/donker-toggle in het dashboard (CSS-variabelen per thema,
  onthouden in `localStorage`).
- **BESLISSING** — Onderscheid blootgelegd: **optimalisatievraag** (welke rechtsvorm bij V?)
  vs. **werkelijke-situatievraag** (gegeven mijn inkomstenbronnen, wat is mijn belasting?).
  Tweede modus toegevoegd: **"Werkelijk inkomen"** met **toevoegbare inkomstenbronnen**
  (loon/winst/uitkering/ROW). Meerdere banen → loon optellen; meerdere ondernemingen →
  winst optellen; alles stapelt in één progressieve box 1-berekening. Endpoint `POST /bereken`
  (hergebruikt `bereken_persoon`, dat dit al kon — zie €240k-hybride). 41 tests groen.

- **BESLISSING** — Dependency-vrije client `client/index.html` (vanilla HTML/CSS/JS, geen
  build-stap), geserveerd door de API op `GET /` (same-origin → geen CORS-issues). Eén
  commando: `python3 api.py` → dashboard op http://127.0.0.1:8000.
- Invoer (situatie + huishouden + vermogen) → `POST /optimaliseer` → advies + tabel + tips;
  knop → `POST /rapport` (markdown) met downloadbare uitdraai voor de boekhouder.
- End-to-end getest (pagina geserveerd, alle door de JS gelezen velden aanwezig, rapport ok).
  Hiermee is het oorspronkelijke doel bereikt: een inwoner kan gegevens invullen en het
  advies + rapport zien. 40 tests groen.
- **Aanbeveling vastgelegd:** verdere *fiscale* verfijning = diminishing returns (m.n.
  gebruikelijk loon = onderhandelpunt, schijnprecisie-risico). Prioriteit hierna:
  **dataverificatie** van als secundair/benadering gemarkeerde 2026-cijfers vóór echt gebruik.

---

## 2026-06-29 — Fase 3f: oprichtingskosten + gebruikelijk loon ("eigen gebruik")

### Beslissingen
- **BESLISSING** — Eenmalige oprichtingskosten (BV ~€ 600, ZZP/KvK ~€ 80) geamortiseerd
  over een **horizon** (default **10 jaar**, want aanname gebruiker: *men switcht niet
  terug* wegens afzondering privévermogen → lange horizon → klein effect, ~€ 60/jr DGA).
  Notariskosten doorgaans niet-aftrekbaar → als cash-out gemodelleerd.
- **BESLISSING** — **Gebruikelijk loon instelbaar** (`gebruikelijk_loon`). Default =
  normbedrag (€ 58k) = de optimistische, dividend-maximaliserende aanname.

### Bevinding — "eigen gebruik": geen BV-winst (gebruiker)
- **BEVINDING** — Het hele DGA-voordeel hangt aan een **laag gebruikelijk loon**. Voor
  inkomen dat je consumeert ('eigen gebruik') eist de Belastingdienst loon op het niveau
  van een **vergelijkbare dienstbetrekking**. Demo V € 120k, 2026:
  - loon = normbedrag → DGA netto € 75.616 > ZZP € 74.381 (voordeel **+€ 1.235**).
  - loon = € 120k (arbeid bepaalt loon) → DGA netto € 66.718 < ZZP € 74.381 (**−€ 7.663**).
  → Bij eigen gebruik **verdampt het voordeel en wordt de BV zelfs slechter** (geen
  ondernemersaftrek/MKB, wel overhead). Bevestigt de aanname van de gebruiker.
- **CONCLUSIE** — Echt BV-voordeel = **afzondering privévermogen** (aansprakelijkheid,
  niet-fiscaal) + **uitstel voor vermogen dat NIET wordt geconsumeerd**. Niet voor consumptie.

---

## 2026-06-29 — Fase 3e: vaste kosten BV/ZZP (overhead)

- **BESLISSING** — Administratie-/boekhoudkosten per rechtsvorm toegevoegd (param
  `vaste_kosten_indicatief`, instelbaar; **indicatief, niet wettelijk**): werknemer € 0,
  ZZP € 900, BV € 2.000/jr (marktindicatie 2026). Gemodelleerd als **aftrekbaar**
  (verlagen de grondslag) én als cash-out in `netto_besteedbaar`.
- **BESLISSING** — Omslagpunt-zoeker vergelijkt nu op **netto besteedbaar** i.p.v. kale
  belasting (vaste kosten/WW-WIA/pensioen tellen mee). `_score`/`_beste_vorm`.
- **BEVINDING** — De BV-overhead verschuift het DGA-venster naar binnen:
  **€ 102.159/406.108 → € 108.874/393.178** (2026). Bij V € 120k krimpt het DGA-voordeel
  van € 11.200 naar **€ 9.977**; marge DGA↔ZZP nog ~€ 1.300. Eenmalige oprichtingskosten
  (~€ 400-800) nog niet meegenomen (genoteerd in rapport-aannames).

---

## 2026-06-29 — Fase 3d: use case + presenteerbaar rapport

- **BESLISSING** — Use case vastgelegd in `USECASE.md`: één huishouden (V € 120k, partner
  € 20k, 2 kinderen, € 7k HRA, € 500k vermogen) doorloopt de bevindingen uit de
  verkennende vragen (rechtsvormvenster, werknemer vs ZZP, hybride-progressie,
  partnertoerekening, box 3 vs BV + tegenbewijs, jaarruimte). Uitkomst: DGA optimaal,
  ~€ 11.200/jr beter; vermogenslast gelijk (tegenbewijs) € 2.059; jaarruimte € 30.248.
- **BESLISSING** — Aanname: gebruikers willen een **uitdraai voor boekhouder/Belastingdienst**.
  `rapport.py` + `POST /rapport`: **formaat-agnostisch** rapport met (1) invoer+uitkomst,
  (2) **wettelijke grondslag** (wetsartikel + bron-ID + versie per onderdeel), (3) aannames/
  benaderingen expliciet, (4) disclaimer. Optioneel `formaat:"markdown"`. Presentatie
  (PDF/HTML/print) is een losse renderlaag. 37 tests groen.

---

## 2026-06-28 — Fase 3c: openstaande fiscale stukken afgemaakt

Vijf stukken toegevoegd (alle params-gedreven, 36 tests groen):
- **Box 3-tegenbewijs** (zie 3b): heft op werkelijk rendement indien lager dan forfait;
  neutraliseert het spaar-BV-voordeel (box 3 36% < BV 38,8%).
- **Pensioen-jaarruimte (art. 3.127)** — `pensioen.py`: max. aftrekbare lijfrente
  (30% × (premiegevend − franchise) − 6,27×factor A, gemaximeerd). Factor A = 0 voor
  ZZP/DGA. Als tip in de motor + API-veld `jaarruimte_lijfrente`.
- **Huurtoeslag** — `toeslagen.huurtoeslag`: staffel (100/65/40%) + inkomensafbouw.
  **2026 exact (lineair); 2025 BENADERING** (officieel kwadratische eigen-bijdrage) —
  onderscheiden via param-vlag `structuur`. Dit is de concrete plek waar 2025↔2026 een
  echte structuurwijziging heeft (Wet vereenvoudiging huurtoeslag); het param-vlag-patroon
  houdt het één codepad maar markeert de benadering.
- **Kinderopvangtoeslag** — `toeslagen.kinderopvangtoeslag`: max. uurtarief × vergoede uren
  × inkomensafhankelijk %; vergoedings% lineair benaderd tussen de twee inkomensankers.
  Situationeel (opvangsoort/uren/tarief), standalone (niet auto-gekoppeld).
- **Partnertoerekening (art. 2.17)** — `toerekening.py`: optimale verdeling eigen woning
  over partners. Bevestigt: (120k,20k) → 100% bij hoogverdiener (€ 767 besparing,
  lage partner verzilvert niet); (120k,120k) → indifferent (aftopping 37,56%). Box 3-split
  is voor partners tarief-invariant (alleen AHK-afbouw, tweede orde) — genoteerd, niet
  in de optimizer. API-endpoint `/toerekening`.

### Open punten
- Huurtoeslag 2025 exact (kwadratische eigen-bijdrageformule) en de exacte
  vergoedings-staffel kinderopvang (Bijlage I) nog te verfijnen.
- Box 3-partnerverdeling AHK-effect (tweede orde) nog niet in de toerekening-optimizer.

---

## 2026-06-28 — Fase 3b: box 3 = fictief rendement; JSON-API

### Correctie (gebruiker)
- **CORRECTIE** — Box 3 heft een **fictief (forfaitair) rendement**, niet de werkelijke
  winst. Bij **hoog** werkelijk rendement is box 3 daardoor **goedkoper** dan de BV (het
  forfait ondertaxeert). Motor aangepast: DGA-vermogenslast = **min(box 3, BV)** — bij
  laag rendement BV, bij hoog rendement privé in box 3. Break-even ≈ 5,6% (2026).
  Bevestigd in demo: 10% rendement → iedereen box 3 (€ 9.518); 1,5% → DGA via BV (€ 2.913).
- Kanttekening voor later: de **tegenbewijsregeling** laat box 3 op werkelijk rendement
  heffen als dat lager is dan het forfait (eenzijdig naar beneden) — nog niet gemodelleerd.

### API
- **BESLISSING** — Engine ontsloten als **dependency-vrije JSON HTTP-API** (`api.py`,
  Python stdlib `http.server`). Endpoints `/health`, `/jaren`, `/vergelijk`, `/optimaliseer`;
  CORS open. Contract in `API.md`. Aanbeveling: later FastAPI zonder contractwijziging.
  `Situatie` is het invoermodel. End-to-end getest (28 tests groen).

---

## 2026-06-28 — Fase 3: optimalisatiemotor (incl. box 3 vs vermogen in de BV)

### Beslissing
- **BESLISSING** — `optimalisatiemotor.py`: één `Situatie` (V, profiel, vermogen,
  verwacht rendement) → `optimaliseer()` rangschikt werknemer/ZZP/DGA op **totaal netto**
  = netto besteedbaar + toeslagen − vermogenslast. `Situatie` wordt het invoermodel van
  het dashboard.
- **BESLISSING** — Vermogensdimensie toegevoegd: privévermogen → **box 3** (forfaitair);
  vermogen in de BV → alleen **werkelijk rendement** via Vpb + box 2. Break-evenrendement
  waar beide gelijk zijn: **≈ 5,6%** (2026). Onder dat rendement is de BV goedkoper voor
  vermogen (spaar-/beleggings-BV bespaart box 3); erboven is het box 3-forfait gunstiger.

### Bevinding
- **BEVINDING** — De box 3-dimensie **versterkt het DGA-voordeel** bij laagrenderend
  vermogen. Voorbeeld V = € 150k + € 500k spaargeld (1,5% rendement), 2026: DGA totaal
  netto € 91.963 vs ZZP € 80.194 vs werknemer € 69.631 — DGA € 22.332/jr beter, waarvan
  ~€ 6.600 puur box 3-vermijding (vermogenslast € 2.913 in BV vs € 9.518 in box 3).
- Dit bevestigt het punt van de gebruiker: voor een vermogende DGA is het **vermijden van
  box 3 door vermogen in de BV te houden** een zelfstandig, materieel voordeel — naast het
  inkomensvoordeel in het DGA-venster.

---

## 2026-06-28 — Fase 2h: toeslagen gekoppeld aan de rechtsvormvergelijking

### Bevinding
- **BESLISSING** — `vergelijk()` accepteert nu een `Huishoudprofiel`; per rechtsvorm wordt
  het **verzamelinkomen = toetsingsinkomen** bepaald en daaruit zorgtoeslag + KGB berekend.
  Nieuw: `Vorm.verzamelinkomen`, `.toeslagen`, `.netto_inclusief_toeslagen`.
- **BEVINDING (onderkant-dynamiek)** — Voor dezelfde V verschilt het toetsingsinkomen sterk:
  **DGA = volledig V** (loon, geen ondernemersaftrek, geen dividend onder ~€58k) → **hoogste
  toetsingsinkomen → minste toeslag**; **ZZP = laagste** (zelfstandigenaftrek + MKB) → meeste
  toeslag; werknemer ertussen (brutoloon is bovendien teruggerekend uit V).
- **BEVINDING** — Voorbeeld gezin (2 kinderen, 1 verdiener + partner), V = € 50k, 2026:
  zorgtoeslag ZZP € 1.170 vs DGA **€ 156**; netto+toeslagen ZZP € 46.622 vs werknemer
  € 41.389 vs DGA € 41.207. **De DGA is aan de onderkant dubbel slecht** (hoogste belasting
  én minste toeslag); de ZZP-voorsprong wordt versterkt. Bevestigt: toeslagen bijten alleen
  aan de onderkant en draaien daar de rangorde niet, maar vergroten de ZZP-marge.

---

## 2026-06-28 — Fase 2g: toeslagen + architectuurverificatie params↔logica

### Toeslagen
- **BESLISSING** — Toeslagenmodule (`toeslagen.py`) met de twee zuiver inkomensafhankelijke
  toeslagen: **zorgtoeslag** (lineaire afbouwbenadering tussen afgeleid drempelinkomen en
  inkomensgrens) en **kindgebonden budget** (exacte afbouw: afbouwpunt + %). Vermogenstoets
  op box 3-grondslag, peildatum 1 jan. Toetsingsinkomen = verzamelinkomen.
- **OPEN PUNT** — Huurtoeslag (vraagt rekenhuur) en kinderopvangtoeslag (vraagt opvanguren/
  -kosten) nog niet gemodelleerd. **LET OP structuurwijziging:** huurtoeslag is per **2026**
  vereenvoudigd (lineaire afbouw + afschaffing harde huurgrens, Stb. 2024, 425) — dat is een
  **logica**verschil 2025↔2026, geen louter getalverschil (zie verificatie hieronder).

### Architectuurverificatie — "alleen cijfers wijzigen, module gelijk" (gebruikersaanname)
- **BEVINDING (bevestigd)** — Params-**structuur** 2025 vs 2026 is **identiek** (zelfde
  sleutels → zelfde codepaden). 74 waarden gewijzigd (indexatie + tariefaanpassingen),
  39 ongewijzigd (structurele tarieven: EWF 0,35%, toptarief 49,5%, box 2 24,5/31%,
  box 3 36%, Vpb, MKB 12,7%, schuldendrempel € 3.800, urencriterium 1.225, …).
- **BEVINDING** — **Geen jaar-afhankelijke logica** in `belastingkern/`: geen enkele
  `if jaar ==`-vertakking; de enige "2025/2026" in code staan in docstrings/commentaar
  (IACK-uitleg, wetcitaten). Alle bedragen komen via `p[...]` uit de params.
- **CONCLUSIE** — Aanname klopt **voor indexatie + tariefwijzigingen**. Ze **breekt bij
  structurele wetswijzigingen** (andere rekenregel, niet alleen een getal). Eerstvolgende
  concrete geval: **huurtoeslag-vereenvoudiging 2026**; verder box 3-stelsel 2028 en
  IACK-afschaffing 2027. Ontwerpregel: getallen → params; structurele varianten → param-vlag
  waar mogelijk (bv. box 3 `*_voorlopig`), pas geversioneerde logica als het echt moet.
- Cosmetisch: urencriterium "1.225" staat ook hardcoded in een melding-string terwijl het
  in params staat (`urencriterium_uren`) — kan uit params gelezen worden.

---

## 2026-06-28 — Fase 2f: werknemersverzekeringen (WW/WIA); thesis bevestigd

### Beslissing
- **BESLISSING** — WW/WIA (Awf + Aof + Whk) toegevoegd als **werkgeverslast in V**
  (`socialezekerheid.werknemersverzekeringen`). Default-profiel kleine werkgever/vast
  contract: 2025 ≈ 10,35% / 2026 ≈ 10,53% van het loon tot het maximumpremieloon
  (€ 75.864 / € 79.409). DGA (a.b.) en ZZP zijn **niet verzekerd** → geen premie, geen recht.
- **BESLISSING** — Onderscheid in `Vorm`: `totale_belasting` (zuivere druk: IB/Vpb/box2 + Zvw)
  vs. `totale_wig` (incl. WW/WIA). WW/WIA = premie **met aanspraak** (verzekering), geen
  zuivere belasting.

### Bevinding — thesis bevestigd (2026)
- **BEVINDING** — Door WW/WIA in V mee te nemen daalt het brutoloon → de **zuivere
  belastingdruk van de werknemer zakt naar ≈ de ZZP**: op € 100k werknemer **34,7%** vs
  ZZP **35,1%** vs DGA 35,3% (spreiding **0,6pp**!). De eerdere ~4pp werknemer-kloof was
  dus vrijwel volledig de **WW/WIA-premie** — die de werknemer als verzekering terugkrijgt.
- **BEVINDING** — Op de **totale wig** (incl. WW/WIA) is de werknemer juist het duurst
  (~8–10pp boven ZZP/DGA), maar dat verschil koopt WW/WIA-dekking die ZZP/DGA missen
  (zij dekken dat privé via AOV/broodfonds). → **"totale economische positie ± gelijk"
  is verdedigbaar in de middenmoot.**
- Eindbeeld thesis: in de middenmoot (€ 50k–100k) liggen alle drie de vormen, mits Zvw én
  WW/WIA correct meegenomen, **dicht bij elkaar**; de echte afwijking blijft het
  **DGA-venster** (~€ 102k–406k) waar box 2 het wint.

---

## 2026-06-28 — Fase 2e: omslagpunten ZZP/DGA (twee, niet één)

### Bevinding
- **BEVINDING** — Het verschil in totale heffing ZZP↔DGA is **niet monotoon**: er zijn
  **twee omslagpunten**. De DGA is alleen optimaal in een **venster**; daarbuiten wint de
  ZZP. Optimale route = **ZZP → DGA → ZZP**.
  - 2026 (incl. Zvw): ZZP < **€ 102.159** | DGA € 102.159–**€ 406.108** | ZZP daarboven.
  - 2025 (incl. Zvw): ZZP < € 103.801 | DGA € 103.801–€ 391.243 | ZZP daarboven.
  - Kaal (zonder Zvw) liggen de punten op € 111.135 / € 380.609 (2026).
- **WAAROM het tweede punt** — bij zeer hoge winst loopt de DGA-druk op (box 2 31% boven
  ± € 68.843 + Vpb 25,8% boven € 200.000 ≈ 48,8%), terwijl de **MKB-winstvrijstelling
  (12,7%)** het ZZP-toptarief structureel onder ~44% houdt. Daardoor wint de ZZP weer.
- **BEVINDING** — Werknemer is **nergens** de goedkoopste vorm (in deze heffing-only framing).
- Tooling: `omslagpunt.py` + `optimalisatie.omslagpunten()` (rasterscan + bisectie, vindt
  álle tekenwissels). Test `test_omslagpunten_zzp_dga_2026` borgt route zzp→dga→zzp.

---

## 2026-06-28 — Fase 2d: Zvw + pensioen-equivalent; thesis verfijnd

### Beslissingen
- **BESLISSING** — Zvw toegevoegd (`socialezekerheid.py`): werkgeversheffing (werknemer)
  vs. lage bijdrage (ZZP/DGA); geen Zvw over box 2-dividend. Vergelijkingsraam expliciet
  **V = totale economische kosten incl. werkgeverslasten** (werknemersloon wordt uit V
  teruggerekend). Pensioen-equivalent als optionele aftrekbare reservering (geen belasting).
- **BEVINDING (correctie eerdere framing)** — DGA-tabel rekende al op vólledige uitkering
  (Vpb + box 2); box 2-uitstel is enkel timing, geen lagere totale druk. Punt gebruiker bevestigd.

### Bevinding — thesis "totale druk ± gelijk" (incl. Zvw, 2026)
- **BEVINDING** — Zvw is de **gelijkmaker tussen ZZP en DGA**: op € 75k–100k convergeren ze
  tot **binnen ~0,2–1 pp** (100k: WN 39,4% / ZZP 35,1% / DGA 35,3%). In de middenmoot
  (€ 50k–100k) landen de drie vormen binnen ~4–8 pp → **thesis houdt stand voor "de meeste
  mensen"**.
- **BEVINDING (weerlegging aan de bovenkant)** — Boven ± € 120k wint de **DGA structureel**
  (Vpb 19% + box 2 24,5% ≈ 38,8% < box 1-toptarief 49,5%); spreiding loopt weer op naar
  ~7–8 pp. Er bestaat dus wél een optimale route voor hogere inkomens (DGA). Klassieke
  boxenarbitrage; niet gelijkgetrokken.
- **BEVINDING** — Pensioen-equivalent verlaagt alle vormen ~gelijk; spreiding nauwelijks
  kleiner (100k: 4,3 → 3,8 pp). **Pensioen is niet de gelijkmaker; Zvw wel.**
- **NUANCE** — Werknemer blijft ~4 pp boven ZZP/DGA in pure heffing; dat verschil
  correspondeert met werknemersverzekeringen (WW/WIA) die hier niet als waarde zijn geteld.
  Eindoordeel: **directioneel bevestigd in de middenmoot, weerlegd aan de bovenkant.**

### Open punten
- **OPEN PUNT** — Zvw-grondslag ZZP vereenvoudigd = belastbare winst (na MKB); lijfrente-
  premie verlaagt de Zvw-grondslag niet in het model. Te verfijnen.
- **OPEN PUNT** — Werknemersverzekeringen (WW/WIA) en de waarde daarvan niet gemodelleerd;
  bepalen mede of de werknemer-kloof "echt" is. Toeslagen (lage inkomens) nog te koppelen.

---

## 2026-06-28 — Fase 2c: ondernemersmodule + DGA + rechtsvormvergelijking (thesis-toets)

### Beslissingen
- **BESLISSING** — Ondernemersmodule toegevoegd (zelfstandigenaftrek, startersaftrek,
  MKB-winstvrijstelling 12,7%, urencriterium) en de tariefaanpassing (art. 2.10a)
  gegeneraliseerd zodat die ook op ondernemersaftrek/MKB drukt.
- **BESLISSING** — Engine uitgebreid met **box 2** (dividend telt mee in het
  verzamelinkomen → afbouw heffingskortingen, en wordt apart belast). DGA-module
  (Vpb + gebruikelijk loon + box 2) en `vergelijking.py` (werknemer/ZZP/DGA) gebouwd.
- **BESLISSING** — Vergelijkingsinvariant: **V = economische waarde vóór IB/Vpb** op
  activiteitsniveau (brutoloon / fiscale winst / bv-winst vóór DGA-loon).

### Bevinding — thesis "druk is gelijkgetrokken"
- **BEVINDING** — De pure IB/Vpb-druk is **NIET gelijk**: spreiding **5–8 procentpunt**
  tussen de rechtsvormen (2025 en 2026 vrijwel identiek). Er bestaat dus wél een
  optimale route, en die **verschuift met inkomen**:
  - **ZZP goedkoopst tot ± € 100k–120k** (zelfstandigenaftrek + MKB-winstvrijstelling).
  - **DGA goedkoopst boven ± € 120k** (Vpb 19% + box 2 24,5% ≈ 38,8% < box 1-toptarief).
  - **Werknemer structureel het duurst** in deze framing; gelijk aan DGA zolang
    V ≤ gebruikelijk loon (dan geen dividend).
- **NUANCE / OPEN PUNT** — De vergelijking laat **Zvw, werkgeverslasten, pensioenopbouw,
  box 2-uitstel en toeslagen** buiten beschouwing. Juist die sluiten de kloof: Zvw raakt
  ZZP/DGA, werkgever betaalt premies + pensioen bovenop het werknemersloon. De thesis is
  daarmee **directioneel verdedigbaar voor de totale economische druk, maar de zuivere
  belastingcijfers weerleggen strikte gelijkheid**. Toets: Zvw + pensioen-equivalent
  toevoegen en kijken of de spreiding richting nul gaat. → volgende experiment.

---

## 2026-06-28 — Fase 2: rekenkern v1 (Python)

### Beslissingen
- **BESLISSING** — Rekenkern in **Python** (op verzoek). Architectuur: **versie-data
  (`rekenkern/params/<jaar>.json`) gescheiden van logica (`belastingkern/`)**, met
  `_bron`-verwijzingen naar het bronregister. Bij wetswijziging volstaat in beginsel
  het aanpassen van de params-file.
- **BESLISSING** — v1-afbakening: box 1 (incl. eigen woning/Hillen/tariefsaanpassing),
  alle heffingskortingen, box 3 forfaitair, en verzilvering (art. 8.8). Bewust nog
  NIET: ondernemersfaciliteiten, box 3-tegenbewijs (OWR), toeslagen, pensioen-jaarruimte,
  automatische partnertoerekening (art. 2.17), uitbetaling art. 8.9. Zie `rekenkern/README.md`.

### Bevindingen & correcties
- **CORRECTIE (model)** — Pensioen/AOW/uitkeringen zijn box 1-inkomen maar tellen **niet**
  mee voor de arbeidskorting (alleen loon uit tegenwoordige arbeid + winst + resultaat).
  Model gesplitst in `loon` vs `uitkering_pensioen`; `arbeidsinkomen` is de
  arbeidskorting-grondslag.
- **BEVINDING** — 9 tests met handmatig nagerekende waarden slagen; demo-CLI rekent
  werknemer-, gepensioneerde- en ZZP-scenario's correct door. Onzekere 2026-cijfers
  (box 3-forfaits, Hillen-%) verschijnen als waarschuwing in de output.

### Open punten
- **OPEN PUNT** — ZZP-scenario rekent winst nu 1-op-1 als box 1-inkomen; zonder
  zelfstandigenaftrek + MKB-winstvrijstelling is de uitkomst voor ondernemers te hoog.
  Prioriteit voor fase 2b (ondernemersmodule).
- **OPEN PUNT** — Arbeidskorting boven AOW-leeftijd is benaderd via schaalfactor
  (max_aow / max_onder_aow); exacte AOW-segmenttabel nog niet in de params.

---

## 2026-06-28 — Projectstart en eerste juridische inventarisatie

### Beslissingen
- **BESLISSING** — Scope vastgesteld: Box 1 + heffingskortingen, Box 3, aftrekposten
  & fiscale-partnertoerekening, toeslagen, eigen onderneming, én pensioen. Belasting-
  jaren **2025 en 2026** naast elkaar. Eerste levering = juridische knowledge base.
- **BESLISSING** — Bronbeleid: **wetten.overheid.nl is de primaire bron** voor wettekst
  (heeft versiebeheer via `geldigheidsdatum`/toestand in de URL). Belastingdienst- en
  rijksoverheid-pagina's zijn toelichtend.
- **BESLISSING** — De Belastingdienst WCM `connect/...` diep-links zijn instabiel
  (gaven al een 404 bij de door de gebruiker aangeleverde tarieven-URL). We leunen
  voor harde regels op wetten.overheid.nl en bewaren onderwerp i.p.v. fragiele links.
- **BESLISSING** — Elk bedrag/percentage krijgt een **bron-ID** in
  `bronnen/bronregister.md`, zodat we bij wetswijzigingen exact weten welke versie te
  hercontroleren is.
- **BESLISSING** — Dit journaal + een project-`CLAUDE.md` borgen dat beslissingen en
  bevindingen voortaan automatisch worden gelogd.
- **BESLISSING** — Pensioen toegevoegd als aparte module (`07-pensioen.md`) op verzoek.

### Bevindingen & correcties (per module)
- **CORRECTIE (04-aftrek)** — Plafond **periodieke giften is € 1.500.000** per fiscaal
  paar sinds 1-1-2025 (was € 250.000 in 2023–2024). [AFT]
- **CORRECTIE (06-onderneming)** — **MKB-winstvrijstelling blijft 12,7%** in 2025 én
  2026; de voorgestelde verlaging naar 12,03% is bij amendement teruggedraaid en heeft
  nooit gegolden. [OND]
- **BEVINDING (06-onderneming)** — **Zelfstandigenaftrek** daalt hard: € 2.470 (2025)
  → € 1.200 (2026), afbouwpad richting ~€ 900 in 2027. [OND]
- **BEVINDING (02-heffingskortingen)** — **IACK** wordt afgeschaft per **2027** (niet
  2025); geen recht meer voor kinderen geboren ná 2024; afbouw in stappen tot nihil
  in 2035. [HK]
- **BEVINDING (07-pensioen)** — **Lijfrentepremie valt NIET onder de tariefaanpassing
  art. 2.10**; aftrek dus tegen het volle marginale tarief (~49,5%). Sterke
  optimalisatieknop voor hoge inkomens. [PEN-09]
- **BEVINDING (07-pensioen)** — Aftoppingsgrens pensioen/lijfrente **€ 137.800**
  bevroren in 2025 én 2026. AOW-leeftijd **67 jaar** in beide jaren. [PEN-10][PEN-05]
- **CORRECTIE (05-toeslagen)** — Harde **inkomens**grens huurtoeslag verviel al per
  **2020** (niet 2025); de structuurwijziging (lineaire afbouw, afschaffing harde
  huurgrens) is per **2026**. [TOE]
- **BEVINDING (05-toeslagen)** — "Bijna gratis kinderopvang" is uitgesteld naar
  **2029** (was 2025→2027→2029); wetsvoorstel in consultatie. [TOE]
- **BEVINDING (03-box3)** — Box 3-tarief 36% beide jaren; forfait overige bezittingen
  6,00% (2026, vast), banktegoeden/schulden 2026 nog **voorlopig**. [B3]

### Open punten (te verifiëren bij volgende update)
- **OPEN PUNT** — Diverse **2026-bedragen komen uit secundaire bronnen** (accountants/
  intermediairs) i.p.v. een primaire Belastingdienst-tabel: o.a. art. 3.127 jaar-/
  reserveringsruimte 2026 [PEN-07], enkele heffingskortingen 2026 [HK-07/11], Hillen
  2026 (~71,87%, versnelde afbouw — onzeker) [B1-hillen].
- **OPEN PUNT (03-box3)** — **Wet werkelijk rendement box 3** (beoogd 2028) is politiek
  onzeker (dreigende verwerping Eerste Kamer; minister kondigde aanpassingen aan). Als
  planning behandelen, niet als geldend recht. [B3-10]
- **OPEN PUNT (03-box3)** — Definitieve box 3-forfaits 2026 (banktegoeden, schulden)
  worden pas begin 2027 vastgesteld; nu als VOORLOPIG gemarkeerd. [B3-03]
- **OPEN PUNT (05-toeslagen)** — Mogelijke artikelhernummering Wet op de huurtoeslag
  door de vereenvoudiging per 2026; per datumversie controleren. [TOE-WHT]
- **OPEN PUNT** — wetten.overheid.nl gaf via geautomatiseerd ophalen vaak alleen de
  inhoudsopgave/structuur terug, niet de volledige artikeltekst. Artikelnummers en
  toestandsdatums zijn bevestigd; exacte artikelteksten deels via commentaarbronnen
  (Via Juridica, InView). Bij twijfel handmatig de wettekst-toestand checken.
