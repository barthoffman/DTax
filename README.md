# Belastingen-dashboard — Nederlandse inwoner

Doel: een Nederlandse inwoner vult op een simpel dashboard gegevens in, waarna we
laten zien hoe de fiscale positie **wettelijk geoptimaliseerd** kan worden, met zo
realistisch mogelijke inschattingen. Onduidelijke punten kunnen met onderbouwde
interpretatie bij de Belastingdienst worden ingediend; die markeren we expliciet.

## Aanpak in fasen

1. **Juridische knowledge base** (huidige fase) — per onderwerp de relevante
   wetsartikelen, bedragen/percentages voor **2025 én 2026**, en de optimalisatie-
   aandachtspunten. Met een centraal **bronregister** zodat we bij wetswijzigingen
   precies weten welke teksten/versies opnieuw gecheckt moeten worden.
2. **Rekenkern** — de regels uit de knowledge base omzetten in berekeningen.
3. **Dashboard** — invulscherm + optimalisatie-advies.

## Scope (vastgesteld 2026-06-28)

- Box 1: werk, woning, uitkeringen, AOW/pensioen
- Heffingskortingen
- Box 3: sparen en beleggen
- Aftrekposten & fiscale-partnertoerekening
- Toeslagen (zorg, huur, kindgebonden budget, kinderopvang)
- Eigen onderneming (winst uit onderneming, ondernemersfaciliteiten)
- Belastingjaren: **2025 en 2026** naast elkaar

## Bronbeleid

- **Primaire bron** voor wettekst: `wetten.overheid.nl` (heeft versiebeheer via
  `geldigheidsdatum` in de URL — essentieel voor het later checken op updates).
- **Toelichtende bron**: belastingdienst.nl en rijksoverheid.nl. Let op: de
  WCM-`connect`-URLs van de Belastingdienst zijn instabiel (geven 404's); we
  bewaren waar mogelijk de stabiele/short-URL of het onderwerp i.p.v. de diepe link.
- Elk bedrag/percentage en elke regel verwijst naar een bron-ID in
  `bronnen/bronregister.md`.

## Onderhoud — jaarlijkse update naar het nieuwe belastingjaar

De fiscale cijfers veranderen elk jaar. Drie lagen houden het dashboard up-to-date:

1. **Wekker (primair) — attenderingsservice.** Abonneer op
   [officielebekendmakingen.nl](https://www.officielebekendmakingen.nl/) met de **zoekopdracht**
   `"Bijstellingsregeling directe belastingen"` (Staatscourant). Dé regeling die bijna alle
   geïndexeerde bedragen vaststelt verschijnt **eind december**; je krijgt dan automatisch een mail.
2. **Vangnet — GitHub Action.** `.github/workflows/fiscale-cijfers-check.yml` draait 1e & 15e van
   nov–feb (+ handmatig via *Run workflow*) en opent een **issue** zodra `rekenkern/params/<jaar>.json`
   voor het nieuwe jaar nog ontbreekt, mét bronchecklist en -status.
3. **Handleiding — bronregister.** De **update-kalender** in `bronnen/bronregister.md` zegt per
   parameter wanneer de nieuwe waarde beschikbaar komt en waar te checken (incl. de notificatie-bronnen
   `UPD-01..05`).

**Update-actie:** komt de mail/het issue → start een sessie en zeg *"update naar `<jaar>`"*. Dan worden
de Bijstellingsregeling + `fisin<jaar>` opgehaald, `rekenkern/params/<jaar>.json` + het bronregister
bijgewerkt, en de tests gedraaid. Let op de **voorlopige box 3-forfaits** (banktegoeden/schulden) — die
worden pas ná afloop van het jaar definitief.

## Mappenstructuur

```
knowledge-base/
  00-overzicht.md            kaart van boxen + onderwerpen
  01-box1-werk-woning.md
  02-heffingskortingen.md
  03-box3-vermogen.md
  04-aftrekposten-toerekening.md
  05-toeslagen.md
  06-onderneming.md
bronnen/
  bronregister.md            centraal register: wet, artikel, URL+versie, opgehaald op
```

## Status (bijgewerkt 2026-06-28)

| Onderdeel | Status |
|---|---|
| Projectopzet | gereed |
| Box 1 / woning (`01`) | knowledge base v1 gereed |
| Heffingskortingen (`02`) | knowledge base v1 gereed |
| Box 3 (`03`) | knowledge base v1 gereed |
| Aftrekposten & toerekening (`04`) | knowledge base v1 gereed |
| Toeslagen (`05`) | knowledge base v1 gereed |
| Onderneming (`06`) | knowledge base v1 gereed |
| Pensioen (`07`) | knowledge base v1 gereed |
| Centraal bronregister | samengevoegd |
| Journaal + werkafspraken | ingericht (`JOURNAAL.md`, `CLAUDE.md`) |
| Rekenkern (Python) | box 1 + heffingskortingen + box 3 + onderneming + box 2 + Zvw + WW/WIA + toeslagen, 27 tests groen |
| Rechtsvormvergelijking | werknemer / ZZP / DGA incl. Zvw, WW/WIA, pensioen, toeslagen (`vergelijk.py`, `omslagpunt.py`) |
| Optimalisatiemotor | `optimaliseer.py` — beste route incl. box 3 (fictief) vs vermogen-in-BV; `Situatie` = invoermodel |
| JSON-API | `api.py` (stdlib) — `/vergelijk`, `/optimaliseer`, `/toerekening`, `/rapport`, `/jaren`, `/health`; contract in `API.md` |
| Use case + rapport | `USECASE.md` (bevindingen) + `/rapport` (presenteerbaar, mét wettelijke grondslag + aannames) |
| Fiscale modules compleet | box 1/2/3 (+tegenbewijs), heffingskortingen, onderneming, Zvw, WW/WIA, toeslagen (zorg/huur/KGB/kinderopvang), pensioen-jaarruimte, partnertoerekening, vaste/oprichtingskosten — 40 tests groen |
| Openstaand (verfijning) | huurtoeslag 2025 exact, kinderopvang-staffel exact, box 3-partner-AHK-effect; dataverificatie 2026-cijfers |
| Dashboard-client | `client/index.html` (dependency-vrij), geserveerd door de API op `GET /` |

Zie `JOURNAAL.md` voor beslissingen, bevindingen en open punten, en
**`BEVINDINGEN.md`** voor de inhoudelijke conclusies in gewone taal (rechtsvorm, BV-uitstel,
lijfrente, box 3) — bedoeld om de keuzes zélf te kunnen begrijpen en voorleggen.

## Zo start je het dashboard

```bash
cd rekenkern
python3 api.py            # API + dashboard op http://127.0.0.1:8000
```
Open `http://127.0.0.1:8000`, vul je gegevens in → advies + downloadbaar rapport voor de boekhouder.

## Hosting & deployment

De app draait live op **https://staging.watmagwel.nl** (achter e-mail-OTP-login), via een
Cloudflare-tunnel naar een container op de Mac mini. De volledige opzet — tunnel, container,
DNS, auth/SMTP, het `./deploy.sh`-commando en geleerde valkuilen — staat in
**[`DEPLOYMENT.md`](DEPLOYMENT.md)**.
