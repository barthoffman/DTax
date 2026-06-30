# Bronregister

Centraal overzicht van alle gebruikte bronnen, zodat we bij wetswijzigingen exact
weten welke teksten/versies opnieuw te controleren zijn.

## Hoe te gebruiken
- Elke bron heeft een **bron-ID** (bv. `B1-tarief`, `B3-03`, `PEN-09`).
- **Versie/geldigheidsdatum**: voor `wetten.overheid.nl` de toestand-/geldigheidsdatum;
  voor toelichtende pagina's de laatst-bijgewerkt- of belastingjaar-aanduiding.
- **Opgehaald op**: datum waarop wij de tekst raadpleegden (eerste ronde: 2026-06-28).
- Bij een update-check vergelijken we de huidige geldende versie met de hier vastgelegde.
- Detail per regel staat in de "## Bronnen"-tabel onderaan elk KB-bestand; dit register
  is de geaggregeerde index.

## Verificatie 2026-cijfers — geverifieerd op 2026-06-29

Alle vastgelegde 2026-waarden zijn op **2026-06-29** gecontroleerd tegen primaire/officiële
bronnen (belastingdienst.nl fisin2026 & tabellen, wetten.overheid.nl, rijksoverheid.nl, SVB,
UWV, Staatscourant). **Vrijwel alles BEVESTIGD.** Aandachtspunten:

| Item | Status |
|---|---|
| Box 1-schijven/tarieven, AOW-tarief, eigen woning, EWF, HRA-aftoptarief 2026 | BEVESTIGD |
| Hillen-aftrek 2026 = **71,867%** | BEVESTIGD (eerder onzeker) |
| Heffingskortingen (AHK, arbeidskorting, IACK, ouderen-, jonggehandicapten-) 2026 | BEVESTIGD |
| Arbeidskorting nihilgrens | CORRECTIE: € 132.921 → **€ 132.920** (verwerkt) |
| Onderneming (zelfst.aftrek € 1.200, MKB 12,7%, starters € 2.123) 2026 | BEVESTIGD |
| Vpb 19/25,8%, box 2 24,5/31% (grens € 68.843), gebruikelijk loon € 58.000 | BEVESTIGD |
| Zvw 6,10/4,85% (max € 79.409), jaarruimte € 35.589 (franchise € 19.172), AOW-bedragen | BEVESTIGD |
| Toeslagen 2026 (zorg, huur, KGB, kinderopvang-uurtarieven/percentages) | BEVESTIGD |
| **Box 3-forfaits banktegoeden 1,28% / schulden 2,70%** | BEVESTIGD maar **officieel VOORLOPIG** (definitief begin 2027) |
| **Huurtoeslag lineaire afbouw € 0,27 / € 0,22 (2026)** | bevestigd via (gouvernementele) secundaire bron; nieuwe systematiek — monitoren |
| **Whk gemiddeld ~1,52%** | indicatief/sectoraal, géén vast tarief |

---

## Update-kalender — wanneer komen de cijfers voor het volgende jaar (2027)?

Het Nederlandse fiscale jaar volgt een vaste ritmiek. Gebruik dit om jaarlijks de waarden te
verversen. **Vuistregel:** vrijwel alles verschijnt als **voorstel op Prinsjesdag (3e dinsdag
september)** en wordt **definitief in december** (Belastingplan → Staatsblad); de
Belastingdienst-`fisin<jaar>`-tabellen volgen rond **december/januari**.

| Categorie (params) | Geldig nu | Status | 2027-waarde beschikbaar | Check bij |
|---|---|---|---|---|
| Box 1-schijven/tarieven, AOW-tarief, EWF, HRA-aftoptarief, Hillen | 2026 | definitief | voorstel sep 2026 → def. dec 2026 | Belastingplan; `belastingdienst.nl/fisin2027` |
| Heffingskortingen (AHK, arbeidskorting, IACK, ouderen-) | 2026 | definitief | dec 2026 | `fisin2027` |
| Onderneming (zelfst.aftrek, MKB-vrijstelling, startersaftrek) | 2026 | definitief | dec 2026 | `fisin2027` |
| Vpb 19/25,8%, box 2 24,5/31% + grens, gebruikelijk loon | 2026 | definitief | voorstel sep 2026 → dec 2026 | Belastingplan |
| Jaarruimte/franchise/aftoppingsgrens (PEN-07/10) | 2026 | definitief | nov–dec 2026 | Belastingdienst; aftoppingsgrens bevroren t/m 2026 |
| AOW-bedragen (PEN-03) | 2026 | definitief | ~dec 2026 (per jan) **én** ~jun 2027 (per jul) | SVB (halfjaarlijks) |
| Toeslagen: zorg/huur/KGB/kinderopvang | 2026 | definitief | dec 2026 | Belastingdienst/Toeslagen |
| **Box 3-forfait banktegoeden (1,28%) + schulden (2,70%)** | 2026 | **VOORLOPIG** | **definitief begin 2027** (ná afloop jaar) | Belastingdienst box 3 — **expliciet nachecken** |
| Box 3 overige-forfait (6,00%), heffingvrij (€ 59.357), schuldendrempel (€ 3.800) | 2026 | definitief | dec 2026 | Belastingplan |
| Premies werknemersverz. (Awf/Aof) + Zvw-% en -max | 2025/2026 | definitief | ~nov 2026 | UWV; Belastingdienst |
| Lijfrente: TOL-max (€ 27.192 / € 26.781), looptijd/ingangsdatum (PEN-13/15) | 2026 | definitief | dec 2026 / `fisin2027` | Belastingdienst |
| Erfbelasting: latentie 30%, imputatie, vrijstellingen (PEN-14) | 2026 | structureel | vrijstellingen jaarlijks dec 2026 | Belastingdienst erfbelasting |

**Jaarlijkse update-actie (begin van elk jaar):** loop deze tabel + de bron-tabellen hieronder
langs, vervang de `params/<jaar>.json`-waarden, en check expliciet de **voorlopige box 3-forfaits**
(die worden pas ná het jaar definitief). Stempel de nieuwe verificatiedatum bovenaan.

---

## Primaire wetten (wetten.overheid.nl) — kern voor update-checks
| BWBR | Wet | Gebruikt in | Toestand/versie vastgelegd |
|---|---|---|---|
| BWBR0011353 | Wet inkomstenbelasting 2001 | 01,02,03,04,06,07 | 2026-01-01 (t/m 2026-02-20) |
| BWBR0002471 | Wet op de loonbelasting 1964 | 07 | te verfijnen |
| BWBR0018472 | Algemene wet inkomensafhankelijke regelingen (Awir) | 05 | 2025-01-01 / 2026-01-01 |
| BWBR0002320 | Algemene wet inzake rijksbelastingen (AWR) | 05 | 2025-01-01 |
| BWBR0018451 | Wet op de zorgtoeslag | 05 | 2026-01-01 |
| BWBR0008659 | Wet op de huurtoeslag | 05 | 2026-01-01 (mogelijk hernummerd) |
| BWBR0022751 | Wet op het kindgebonden budget | 05 | 2025/2026-01-01 |
| BWBR0017017 | Wet kinderopvang | 05 | 2025-01-01 |
| BWBR0017321 | Besluit kinderopvangtoeslag | 05 | 2026-01-01 |
| BWBR0002221 | Algemene Ouderdomswet (AOW) | 07 | te verfijnen |

---

## 01 — Box 1: werk en woning
| Bron-ID | Type | Wet of Instantie | Artikel/Onderwerp | Versie/geldigheidsdatum | Opgehaald op | URL |
|---|---|---|---|---|---|---|
| B1-struct | wet | Wet IB 2001 (BWBR0011353) | art. 2.3, 2.4, 3.1 — boxen / belastbaar inkomen werk en woning | toestand 2025/2026-01-01 | 2026-06-28 | https://wetten.overheid.nl/BWBR0011353/2026-01-01 |
| B1-tarief | wet+toel. | Wet IB 2001 art. 2.10/2.10a; Belastingdienst | schijven/gecombineerde tarieven 2025/2026 onder+boven AOW | 2026-01-01 | 2026-06-28 | https://www.belastingdienst.nl/wps/wcm/connect/bldcontentnl/belastingdienst/prive/inkomstenbelasting/heffingskortingen_boxen_tarieven/boxen_en_tarieven/box_1/box_1 |
| B1-tariefMKB | toel. | MKB Servicedesk | schijven box 1 2025/2026, grens geboren vóór 1946 | 2025/2026 | 2026-06-28 | https://www.mkbservicedesk.nl/belastingen/inkomstenbelasting/belastingschijven-box-1 |
| B1-premies | toel. | Salaris Vanmorgen | premiepercentages 2026: AOW 17,90 / Anw 0,10 / Wlz 9,65 | besluit dec. 2025 | 2026-06-28 | https://www.salarisvanmorgen.nl/2025/12/05/premiepercentages-werknemers-en-volksverzekeringen-2026-vastgesteld/ |
| B1-aow | toel. | Rijksoverheid | AOW-leeftijd 2025–2031 (67 in 2025/2026) | actueel | 2026-06-28 | https://www.rijksoverheid.nl/onderwerpen/algemene-ouderdomswet-aow/aow-leeftijd |
| B1-loon | wet | Wet IB 2001 | afd. 3.3 art. 3.80–3.82 loon; afd. 3.5 periodieke uitkeringen | 2026-01-01 | 2026-06-28 | https://wetten.overheid.nl/BWBR0011353/2026-01-01/0/Hoofdstuk3 |
| B1-ewf | wet+toel. | Wet IB 2001 art. 3.112; Belastingdienst | EWF 0,35%; WOZ-grens villataks € 1.330.000/€ 1.350.000; 2,35% | 2026-01-01 | 2026-06-28 | https://www.belastingdienst.nl/wps/wcm/connect/nl/koopwoning/content/hoe-werkt-eigenwoningforfait |
| B1-hra | wet+toel. | Wet IB 2001 art. 3.120/3.119a/2.10/afd. 10bis.1; Belastingdienst | hypotheekrenteaftrek; max 37,48% (2025)/37,56% (2026) | 2026-01-01 | 2026-06-28 | https://www.belastingdienst.nl/wps/wcm/connect/nl/koopwoning/content/tariefsaanpassing-eigen-woning |
| B1-hillen | wet+toel. | Wet IB 2001 art. 3.123a; Belastingdienst/Rendement | aftrek geen/geringe eigenwoningschuld; 76,67% (2025), ±71,87% (2026, onzeker) | 2026-01-01 | 2026-06-28 | https://www.belastingdienst.nl/wps/wcm/connect/bldcontentnl/belastingdienst/prive/woning/eigenwoningforfait/geen_of_een_kleine_eigenwoningschuld/geen_of_een_kleine_eigenwoningschuld |

## 02 — Heffingskortingen
| Bron-ID | Type | Wet of Instantie | Artikel/Onderwerp | Versie | Opgehaald op | URL |
|---|---|---|---|---|---|---|
| HK-01 | wet | wetten.overheid.nl | Wet IB 2001 h8, art. 8.8–8.18 | toestand 2026-01-01 | 2026-06-28 | https://wetten.overheid.nl/BWBR0011353/2026-01-01/0/Hoofdstuk8 |
| HK-02 | tabel | Belastingdienst | AHK 2025 | 2025 | 2026-06-28 | belastingdienst.nl …/tabel-algemene-heffingskorting-2025 |
| HK-03 | tabel | Belastingdienst | AHK 2026 | 2026 | 2026-06-28 | belastingdienst.nl …/tabel-algemene-heffingskorting-2026 |
| HK-04 | tabel | Belastingdienst | Arbeidskorting 2025 | 2025 | 2026-06-28 | belastingdienst.nl …/tabel-arbeidskorting-2025 |
| HK-05 | tabel | Belastingdienst | Arbeidskorting 2026 | 2026 | 2026-06-28 | belastingdienst.nl …/tabel-arbeidskorting-2026 |
| HK-06 | tabel | Belastingdienst | IACK 2025 | 2025 | 2026-06-28 | belastingdienst.nl …/inkomensafhankelijke-combinatiekorting-2025 |
| HK-07 | overzicht | CijferMeester | heffingskortingen IB 2026 | 2026 | 2026-06-28 | https://cijfermeester.nl/tarieven-heffingskortingen-en-bedragen-inkomstenbelasting-2026/ |
| HK-08 | overzicht | CijferMeester | heffingskortingen IB 2025 | 2025 | 2026-06-28 | https://cijfermeester.nl/tarieven-heffingskortingen-en-bedragen-inkomstenbelasting-2025/ |
| HK-09 | toel. | Rijksoverheid | verzilvering / welke kortingen | actueel | 2026-06-28 | https://www.rijksoverheid.nl/vraag-en-antwoord/inkomstenbelasting/wat-is-een-heffingskorting-en-welke-heffingskortingen-zijn-er |
| HK-10 | toel. | Belastingdienst | uitbetaling minstverdienende partner (< 1963) | actueel | 2026-06-28 | https://www.belastingdienst.nl/wps/wcm/connect/nl/aftrek-en-kortingen/content/heffingskortingen-laten-uitbetalen |
| HK-11 | toel. | Deloitte | Belastingplan 2026 tarieven/kortingen | 2026 | 2026-06-28 | https://www.deloitte.com/nl/nl/services/tax/blogs/pakket-belastingplan-2026-tarieven-heffingskortingen.html |
| HK-12 | toel. | Civra | afschaffing IACK per 2027 + overgangsrecht | actueel | 2026-06-28 | https://civra.nl/artikelen/inkomstenbelasting/afschaffing-inkomensafhankelijke-combinatiekorting-iack-per-2027-en-overgangsrecht |

## 03 — Box 3: sparen en beleggen
| Bron-ID | Type | Wet of Instantie | Artikel/Onderwerp | Versie | Opgehaald op | URL |
|---|---|---|---|---|---|---|
| B3-01 | wet | Wet IB 2001 (BWBR0011353) | hfst. 5; art. 5.2/5.3, 2.13 (incl. Overbruggingswet) | geldend | 2026-06-28 | https://wetten.overheid.nl/BWBR0011353/ |
| B3-02 | toel. | Belastingdienst | berekening box 3-inkomen 2025 | 2025 | 2026-06-28 | https://www.belastingdienst.nl/wps/wcm/connect/nl/box-3/content/berekening-box-3-inkomen-2025 |
| B3-03 | toel. | Belastingdienst | berekening box 3-inkomen 2026 (banktegoeden/schulden voorlopig) | 2026 | 2026-06-28 | https://www.belastingdienst.nl/wps/wcm/connect/nl/box-3/content/berekening-box-3-inkomen-2026 |
| B3-04 | vakmedia | Accountancy Vanmorgen | definitieve forfaits 2025 (vastgesteld 2026-02-20) | 2026-03-30 | 2026-06-28 | https://www.accountancyvanmorgen.nl/2026/03/30/forfaitaire-rendementspercentages-box-3-2025-bekend/ |
| B3-05 | toel. | Belastingdienst | heffingvrij vermogen | actueel | 2026-06-28 | https://www.belastingdienst.nl/wps/wcm/connect/nl/box-3/content/heffingsvrij-vermogen |
| B3-06 | toel./vakmedia | MKB Servicedesk / Stolwijk | tarieven/bedragen 2025-2026 | 2026 | 2026-06-28 | https://www.mkbservicedesk.nl/belastingen/inkomstenbelasting/box-3-tarieven-en-vrijstellingen |
| B3-07 | toel./vakmedia | Belastingdienst / Fiscaal Rendement | groene beleggingen 2025/2026, afbouw 2027/2028 | 2025/2026 | 2026-06-28 | https://www.rendement.nl/inkomen-uit-sparen-en-beleggen/nieuws/vrijstelling-groene-beleggingen-vervalt-pas-per-2028.html |
| B3-08 | toel. | Belastingdienst | box 3-inkomen verdelen met partner (art. 2.17) | actueel | 2026-06-28 | https://www.belastingdienst.nl/wps/wcm/connect/nl/box-3/content/box-3-inkomen-opnieuw-verdelen |
| B3-09 | toel./vakmedia | Belastingbespaarders / EY | tegenbewijsregeling/OWR, HR-arresten juni 2024 | dec. 2025 | 2026-06-28 | https://belastingbespaarders.nl/opgaaf-werkelijk-rendement-box-3/ |
| B3-10 | overheid/vakmedia | Rijksoverheid / Deloitte | Wet werkelijk rendement box 3 (36748), status feb. 2026 | feb. 2026 | 2026-06-28 | https://www.rijksoverheid.nl/themas/werk/inkomstenbelasting/plannen-werkelijk-rendement-box-3/tijdlijn-werkelijk-rendement-box-3 |
| B3-11 | wetstoel. | Min. Financiën (MvT Overbruggingswet box 3, 36204) | peildatumarbitrage 1 okt–31 mrt | 2022/2023 | 2026-06-28 | https://www.rijksfinancien.nl/sites/default/files/bestanden/belastingplan-2023/12-Overbruggingswet-box-3-MvT.pdf |
| B3-12 | wetstoel. | Via Juridica | art. 5.5 (heffingvrij vermogen) / art. 5.3 | actueel | 2026-06-28 | https://www.viajuridica.nl/informatiesoorten/wetstoelichtingen/heffingvrij-vermogen-art-5-5-wet-ib-2001 |

## 04 — Aftrekposten en fiscale-partnertoerekening
> Volledige tabel (prefix `AFT-`, 23 bronnen) staat onderaan `knowledge-base/04-aftrekposten-toerekening.md`. Kernbronnen:

| Bron-ID | Type | Wet of Instantie | Artikel/Onderwerp | Versie | Opgehaald op | URL |
|---|---|---|---|---|---|---|
| AFT-WET-217 | wet/comm. | Via Juridica (Wet IB 2001) | art. 2.17 vrije toerekening gemeenschappelijke bestanddelen | bijgewerkt 2026-06-24 | 2026-06-28 | https://www.viajuridica.nl/ (art. 2.17) |
| AFT-WET-h6 | wet | Wet IB 2001 (BWBR0011353) | hoofdstuk 6 persoonsgebonden aftrek; art. 6.1, 6.2, 6.2a | toestand 2025-01-01 | 2026-06-28 | https://wetten.overheid.nl/BWBR0011353 |
| AFT-giften | wet+toel. | Wet IB 2001 art. 6.34/6.38/6.39; PwC/Van Ree | gewone giften (1%/10%); periodieke giften plafond € 1.500.000 per 2025 | 2025/2026 | 2026-06-28 | (zie KB 04) |
| AFT-zorg | wet+toel. | Wet IB 2001 art. 6.17 e.v. | specifieke zorgkosten; drempels 2025/2026; verhogingsfactor | 2025/2026 | 2026-06-28 | (zie KB 04) |
| AFT-alimentatie | wet | Wet IB 2001 art. 6.3 | partneralimentatie, aftrek tegen getemporiseerd toptarief | 2025/2026 | 2026-06-28 | (zie KB 04) |
| AFT-tarief210a | wet+toel. | Wet IB 2001 art. 2.10a; Belastingdienst | tariefaanpassing aftrek max 37,48%/37,56% | 2025/2026 | 2026-06-28 | (zie KB 04) |

## 05 — Toeslagen
> Volledige tabel (prefix `TOE-`, 28 bronnen) onderaan `knowledge-base/05-toeslagen.md`. Wettekst-kern:

| Bron-ID | Type | Wet of Instantie | Artikel/Onderwerp | Versie | Opgehaald op | URL |
|---|---|---|---|---|---|---|
| TOE-AWIR-2025 | wet | Awir (BWBR0018472) | art. 2,3,5,7,8,16,19,20 | 2025-01-01 | 2026-06-28 | https://wetten.overheid.nl/BWBR0018472/2025-01-01 |
| TOE-AWIR-2026 | wet | Awir (BWBR0018472) | art. 7 lid 3/4, art. 8 | 2026-01-01 | 2026-06-28 | https://wetten.overheid.nl/BWBR0018472/2026-01-01 |
| TOE-AWR | wet | AWR (BWBR0002320) | art. 5a partner; art. 21e inkomensgegeven | 2025-01-01 | 2026-06-28 | https://wetten.overheid.nl/BWBR0002320/2025-01-01 |
| TOE-WZT | wet | Wet op de zorgtoeslag (BWBR0018451) | art. 1,2,3 | 2026-01-01 | 2026-06-28 | https://wetten.overheid.nl/BWBR0018451/2026-01-01 |
| TOE-WHT | wet | Wet op de huurtoeslag (BWBR0008659) | art. 5,13,14,16/17,19/20,27 | 2026-01-01 (mogelijk hernummerd) | 2026-06-28 | https://wetten.overheid.nl/BWBR0008659/2026-01-01 |
| TOE-WKGB | wet | Wet kindgebonden budget (BWBR0022751) | art. 2,3 | 2025/2026-01-01 | 2026-06-28 | https://wetten.overheid.nl/BWBR0022751/2026-01-01 |
| TOE-WKO | wet | Wet kinderopvang (BWBR0017017) | art. 1.6, 1.7 | 2025-01-01 | 2026-06-28 | https://wetten.overheid.nl/BWBR0017017/2025-01-01 |
| TOE-BESLUIT-KOT | wet (AMvB) | Besluit kinderopvangtoeslag (BWBR0017321) | art. 4 max. uurprijs; bijlage I | 2026-01-01 | 2026-06-28 | https://wetten.overheid.nl/BWBR0017321 |
| TOE-EK-36311 | dossier | Eerste Kamer | Wet vereenvoudiging huurtoeslag (Stb. 2024, 425) | 2024 | 2026-06-28 | https://www.eerstekamer.nl/wetsvoorstel/36311_vereenvoudiging_van_de |
| TOE-RO-bijnagratis | nieuws | Rijksoverheid | bijna gratis kinderopvang (invoering 2029) | 2025-10-17 | 2026-06-28 | https://www.rijksoverheid.nl/actueel/nieuws/2025/10/17/wetsvoorstel-voor-bijna-gratis-kinderopvang-openbaar |

## 06 — Eigen onderneming
> Volledige tabel (prefix `OND-`, 28 bronnen) onderaan `knowledge-base/06-onderneming.md`. Kern:

| Bron-ID | Type | Wet of Instantie | Artikel/Onderwerp | Versie | Opgehaald op | URL |
|---|---|---|---|---|---|---|
| OND-WET-3.2 | wet | Wet IB 2001 | afd. 3.2 / art. 3.2–3.6 (winst, urencriterium) | toestand 2026-02-21 | 2026-06-28 | https://wetten.overheid.nl/BWBR0011353 |
| OND-WET-3.76 | wet | Wet IB 2001 | art. 3.76 zelfstandigen-/startersaftrek | toestand 2026-02-21 | 2026-06-28 | https://wetten.overheid.nl/BWBR0011353 |
| OND-WET-3.79a | wet | Wet IB 2001 | art. 3.79a MKB-winstvrijstelling (12,7%) | toestand 2026-02-21 | 2026-06-28 | https://wetten.overheid.nl/BWBR0011353 |
| OND-IV-3.79a | wet (comm.) | InView (Wolters Kluwer) | art. 3.79a — 12,7% geldig vanaf 2025-01-01 | 2025-01-01 | 2026-06-28 | https://www.inview.nl/ (art. 3.79a) |
| OND-OP-zelfst | toel. | Ondernemersplein | zelfstandigenaftrek afbouw 2026 → ~€ 900 | wetswijz. 2026 | 2026-06-28 | https://ondernemersplein.overheid.nl/wetswijzigingen/zelfstandigenaftrek-verder-omlaag-0/ |
| OND-BD-kia26 | toel. | Belastingdienst | KIA-tabel 2026 | 2026 | 2026-06-28 | belastingdienst.nl …/kleinschaligheidsinvesteringsaftrek-2026 |
| OND-RO-bp2023 | wetgeving/MvT | Rijksoverheid/Min. Fin. | afschaffing FOR 2023 + art. 10a.29 overgangsrecht | Belastingplan 2023 | 2026-06-28 | https://www.rijksfinancien.nl/belastingplan-memorie-van-toelichting/2023/d17e10433 |

## 07 — Pensioen
| Bron-ID | Type | Wet of Instantie | Artikel/Onderwerp | Versie | Opgehaald op | URL |
|---|---|---|---|---|---|---|
| PEN-01 | wet | Wet IB 2001 (BWBR0011353) | art. 3.127 jaarruimte/reserveringsruimte | toestand 2026-01-01 | 2026-06-28 | https://wetten.overheid.nl/BWBR0011353/2026-01-01/0/Hoofdstuk3/Afdeling3.7/Artikel3.127 |
| PEN-02 | wet/uitleg | Wet IB 2001 art. 5.16/5.17 (via ABP) | nettolijfrente/nettopensioen — box 3-vrijstelling | 2025/2026 | 2026-06-28 | https://www.abp.nl/pensioen-bij-abp/wat-is-pensioen/nettopensioen |
| PEN-03 | instantie | SVB | AOW-bedragen 2026 | per 2026-01-01 | 2026-06-28 | https://www.svb.nl/nl/aow/bedragen-aow/aow-bedragen |
| PEN-04 | instantie/media | MAX Vandaag (SVB-cijfers) | AOW-bedragen per 2025-01-01 | per 2025-01-01 | 2026-06-28 | https://www.maxvandaag.nl/sessies/themas/geld-werk-recht/de-aow-bedragen-per-1-januari-2025-op-hoeveel-geld-heeft-u-recht/ |
| PEN-05 | overheid | Rijksoverheid | AOW-leeftijd 2025–2031 + koppeling levensverwachting | actueel | 2026-06-28 | https://www.rijksoverheid.nl/themas/belastingen-uitkeringen-en-toeslagen/algemene-ouderdomswet-aow/aow-leeftijd |
| PEN-06 | Belastingdienst | Centraal Aanspreekpunt Pensioenen | AOW-inbouwbedragen/-franchises 2025/2026 | 2025/2026 | 2026-06-28 | https://centraalaanspreekpuntpensioenen.belastingdienst.nl/publicaties/overzicht-aow-inbouwbedragen-en-aow-franchises/ |
| PEN-07 | secundair | Evi van Lanschot | jaarruimte 2026 (franchise € 19.172, max € 35.589, reservering € 42.753) | 2026 | 2026-06-28 | https://www.evivanlanschot.nl/kennis/pensioen/jaarruimte-2026-berekenen-hoeveel-mag-ik-inleggen-op-mijn-lijfrenterekening |
| PEN-08 | secundair | MoneyWise.nl | jaarruimte 2025 (franchise € 18.475, max € 35.798, reservering € 42.108) | 2025 | 2026-06-28 | https://www.moneywise.nl/lijfrente/jaarruimte/2025/ |
| PEN-09 | Belastingdienst | Belastingdienst.nl | afbouw aftrektarief art. 2.10; lijfrente NIET hieronder | 2025/2026 | 2026-06-28 | https://www.belastingdienst.nl/wps/wcm/connect/nl/aftrek-en-kortingen/content/afbouw-tarief-aftrekposten-bij-hoog-inkomen |
| PEN-10 | vakliteratuur | TaxLive / Montae | aftoppingsgrens € 137.800 bevroren 2025/2026 | 2024/2025 | 2026-06-28 | https://www.taxlive.nl/nl/documenten/nieuws/aftoppingsgrens-pensioen-en-lijfrenten-bevroren-in-2025-en-2026-slordige-wetgeving/ |
| PEN-11 | wetstoel. | Via Juridica / CAP Belastingdienst | uitfasering PEB en ODV art. 38n–38q Wet LB | versie 2025-10-17 | 2026-06-28 | https://www.viajuridica.nl/informatiesoorten/wetstoelichtingen/uitfasering-pensioen-in-eigen-beheer-art-38n-38q-wet-lb |
| PEN-12 | naslag/wettekst | Wet LB 1964 (BWBR0002471) / NDFR | omkeerregel h. IIB art. 18–19f; Wtp (2023-07-01) | actueel | 2026-06-28 | https://nl.wikipedia.org/wiki/Wet_op_de_loonbelasting_1964 |
| PEN-13 | wet/Belastingdienst | Wet IB 2001 art. 3.126a + Kennisgroepen Belastingdienst | bancaire (banksparen) lijfrente: standaardlooptijd 20 jr; start vóór AOW → 20 jr + jaren tot AOW; start ín/na AOW-jaar → min. 5 jr mits onder max. jaarbedrag tijdelijke oudedagslijfrente; uiterste ingangsdatum = AOW-leeftijd + 5 jr (art. 3.126a lid 4) | toestand 2026 | 2026-06-29 | https://kennisgroepen.belastingdienst.nl/publicaties/kg07020226-uiterste-ingangsdatum-als-de-opbouwfase-van-de-lijfrente-eindigt-5-jaar-na-de-aow-leeftijd/ |
| PEN-14 | Belastingdienst/wet | Successiewet 1956 art. 20 (latentie) / art. 32 (imputatie) + Belastingdienst.nl | geërfde lijfrente(rekening): erfgenamen betalen box 1 over de uitkeringen (uitgestelde IB komt terug); erfbelasting op de waarde ná aftrek **30% latente inkomstenbelasting**; bij ervende **partner** geldt **imputatie** (½ waarde van pensioen-/lijfrente-aanspraken gaat van de partnervrijstelling af), bij een **kind** geen imputatie | 2026 | 2026-06-29 | https://www.belastingdienst.nl/wps/wcm/connect/nl/erfbelasting/content/lijfrente-of-pensioen-na-overlijden-partner-betaal-ik-erfbelasting |
| PEN-15 | Belastingdienst (officieel) | Belastingdienst fisin2026 — Uitgaven voor inkomensvoorzieningen | **max. jaarbedrag tijdelijke oudedagslijfrente 2026 (1e jaar): € 27.192 (verzekering) / € 26.781 (banksparen/beleggingsrecht)**; min. looptijd 5 jr; start niet vóór AOW-leeftijd, uiterlijk 5 jr erna | belastingjaar 2026, GEVERIFIEERD | 2026-06-30 | https://www.belastingdienst.nl/wps/wcm/connect/fisin/fisin2026/uitgaven_voor_inkomensvoorzieningen |

## DGA / bv (Vpb + box 2 + gebruikelijk loon)
| Bron-ID | Type | Wet of Instantie | Artikel/Onderwerp | Versie | Opgehaald op | URL |
|---|---|---|---|---|---|---|
| DGA-01 | wet | Wet Vpb 1969 (BWBR0002672) | art. 22 tarief (19% tot € 200.000; 25,8% daarboven) | 2026-01-01 | 2026-06-28 | https://wetten.overheid.nl/BWBR0002672/2026-01-01 |
| DGA-02 | toel. | Belastingdienst | Vpb-tarieven 2023–2026 | actueel | 2026-06-28 | https://www.belastingdienst.nl/wps/wcm/connect/bldcontentnl/belastingdienst/zakelijk/winst/vennootschapsbelasting/tarieven_vennootschapsbelasting |
| DGA-03 | wet | Wet IB 2001 (BWBR0011353) | art. 2.12 tarief box 2 (24,5% / 31%) | 2026-01-01 | 2026-06-28 | https://wetten.overheid.nl/BWBR0011353/2026-01-01 |
| DGA-04 | vakmedia | Fiscaal Rendement | box 2-grens 2025 € 67.804 / 2026 € 68.843 (partners ~2×) | 2026 | 2026-06-28 | https://www.rendement.nl/aanmerkelijk-belang/nieuws/inkomensgrens-lage-tarief-box-2-stijgt-in-2026.html |
| DGA-05 | vakmedia | deZaak / MKB-Servicedesk | box 2 tarieven/grens 2026 | 2026 | 2026-06-28 | https://www.dezaak.nl/financien/belastingen/belasting-box-2-aanmerkelijk-belang-wat-houdt-het-in/ |
| DGA-06 | vakmedia | aaff | normbedrag gebruikelijk loon 2025 € 56.000 / 2026 € 58.000 | 2025/2026 | 2026-06-28 | https://www.aaff.nl/artikelen/normbedrag-gebruikelijk-loon-dga |
| DGA-07 | wet+duiding | Wet LB 1964 art. 12a / Vakstudie | gebruikelijk loon hoofdregel; doelmatigheidsmarge vervallen 2023 | actueel | 2026-06-28 | https://www.inview.nl/document/inod029b0932e3a2fdb77e9f4977f912bf80 |
| DGA-08 | vakmedia | Jongbloed / De Zaak | parttime DGA mag lager gebruikelijk loon dan normbedrag mits onderbouwd (meest vergelijkbare dienstbetrekking); "aantoonbaar deeltijdwerk" geldige grond; bewijslast bij DGA | 2026 | 2026-06-29 | https://www.jongbloed-fiscaaljuristen.nl/tips_trucs/tips_dga/gebruikelijk_loon_parttime_dga/ |
| DGA-09 | toel. | Belastingdienst | Wet excessief lenen, drempel € 500.000 | actueel | 2026-06-28 | https://www.belastingdienst.nl/wps/wcm/connect/bldcontentnl/belastingdienst/prive/werk_en_inkomen/bijzondere_situaties/geld_lenen_van_uw_bv/excessief-lenen-van-bv-beperkt |

> Onzeker/te verifiëren: box 2-grenzen 2025/2026 en gebruikelijk loon komen deels uit
> vakmedia (wettekst-fetch afgekapt). Vpb 19%/25,8% en box 2 24,5%/31% breed bevestigd.

## Zvw (Zorgverzekeringswet inkomensafhankelijke bijdrage)
| Bron-ID | Type | Instantie | Onderwerp | Versie | Opgehaald op | URL |
|---|---|---|---|---|---|---|
| ZVW-BD | toel. | Belastingdienst | percentages werkgeversheffing / lage bijdrage Zvw | actueel | 2026-06-28 | https://www.belastingdienst.nl/wps/wcm/connect/bldcontentnl/belastingdienst/prive/werk_en_inkomen/zorgverzekeringswet/veranderingen-bijdrage-zvw/percentages-zvw |
| ZVW-VR2025 | toel. | Van Ree Accountants | 2025: wg 6,51% / laag 5,26% / max € 75.864 | 2025 | 2026-06-28 | https://www.vanreeaccountants.nl/newsitem/maximumpremieloon-en-percentages-zvw-2025/ |
| ZVW-SVM2026 | toel. | Salaris Vanmorgen | 2026: wg 6,10% / laag 4,85% / max € 79.409 (vastgesteld nov. 2025) | 2026 | 2026-06-28 | https://www.salarisvanmorgen.nl/2025/11/13/inkomensafhankelijke-bijdrage-zvw-en-maximumbijdrageloon-2026-vastgesteld/ |

## Werknemersverzekeringen (WW/WIA — werkgeverspremies)
| Bron-ID | Type | Instantie | Onderwerp | Versie | Opgehaald op | URL |
|---|---|---|---|---|---|---|
| WV-01 | officieel | Min. SZW / Staatscourant | premiepercentages werknemers-/volksverzekeringen 2026 (Awf, Aof) | Stcrt. 2025, 42324 | 2026-06-28 | https://zoek.officielebekendmakingen.nl/stcrt-2025-42324.html |
| WV-02 | officieel | Rijksoverheid | max. premieloon/bijdrageloon 2026 € 79.409 | 2026 | 2026-06-28 | https://open.overheid.nl/documenten/916b30f3-eafd-4acf-bd5a-f58319dae544/file |
| WV-03 | officieel | UWV | gedifferentieerde premies WGA/ZW 2026 (gem. WGA 0,96% / ZW 0,56%) | premienota 2026 | 2026-06-28 | https://www.uwv.nl/nl/publicaties/kennis/2025/gedifferentieerde-premies-wga-en-ziektewet-2026 |
| WV-04 | officieel | UWV | gedifferentieerde premies WGA/ZW 2025 (gem. WGA 0,83% / ZW 0,50%) | premienota 2025 | 2026-06-28 | https://www.uwv.nl/nl/publicaties/premienota/2024/gedifferentieerde-premies-wga-en-ziektewet-2025 |
| WV-07 | vakmedia | Salaris Vanmorgen | definitieve premies 2025 (Awf 2,74/7,74; Aof 6,28/7,64; max € 75.864) | 2024-11-27 | 2026-06-28 | https://www.salarisvanmorgen.nl/2024/11/27/definitieve-premiepercentages-werknemers-en-volksverzekeringen-2025-vastgesteld/ |
| WV-11 | voorlichting | KVK | DGA en werknemersverzekeringen (wel/niet verzekerd) | actueel | 2026-06-28 | https://www.kvk.nl/geldzaken/de-dga-en-werknemersverzekeringen/ |

> Whk is een **indicatief gemiddelde** (werkgever-specifiek). Aof-percentages zijn incl.
> Wko-opslag (0,50%) — niet nogmaals optellen.

---

## Toelichtende bronnen (algemeen)
| Bron-ID | Instantie | Onderwerp | Opgehaald op | URL |
|---|---|---|---|---|
| RO-rijksbelastingen | Rijksoverheid | overzicht rijksbelastingen | 2026-06-28 | https://www.rijksoverheid.nl/themas/belastingen-uitkeringen-en-toeslagen/belasting-betalen/overzicht-rijksbelastingen |

## Bekende instabiele bronnen
| Beschrijving | Probleem | Alternatief |
|---|---|---|
| Belastingdienst WCM `connect/...` diep-links | geven soms 404 / wisselen | zoek op onderwerp; gebruik wetten.overheid.nl voor de wettekst |
| wetten.overheid.nl via geautomatiseerd ophalen | levert soms alleen inhoudsopgave i.p.v. artikeltekst | artikelnr + toestandsdatum wel betrouwbaar; tekst evt. via Via Juridica/InView |
