# Belasting-API (contract)

Dependency-vrije JSON HTTP-API over de rekenkern (`api.py`, Python stdlib). Het contract
ontkoppelt de client — `http.server` kan later naar FastAPI zonder contractwijziging.

Starten: `python3 api.py [--poort 8000]`

## Endpoints

### `GET /health`
→ `{"status": "ok"}`

### `GET /jaren`
→ `{"jaren": [2025, 2026]}` (afgeleid uit `params/*.json`)

### `POST /vergelijk`
Rechtsvormvergelijking werknemer / ZZP / DGA.

Request:
```json
{
  "jaar": 2026,
  "economische_waarde": 100000,
  "urencriterium": true,
  "inclusief_zvw": true,
  "inclusief_wnv": true,
  "pensioen_pct": 0.0,
  "profiel": { "heeft_toeslagpartner": true, "aantal_kinderen": 2 }
}
```
Response: `{jaar, bruto, werknemer, zzp, dga, spreiding_pp}` waar elke vorm bevat:
`inkomstenheffing, zvw, werknemersverzekeringen, totale_belasting, totale_wig,
effectief_tarief, effectief_wig, netto_besteedbaar, verzamelinkomen,
netto_inclusief_toeslagen` en (indien profiel) `toeslagen{zorgtoeslag, kindgebonden_budget, totaal}`.

### `POST /optimaliseer`
Optimalisatieadvies (beste route incl. vermogensdimensie box 3 vs BV).

Request:
```json
{
  "jaar": 2026,
  "economische_waarde": 150000,
  "prive_vermogen": 500000,
  "verwacht_rendement": 0.015,
  "urencriterium": true,
  "profiel": { "aantal_kinderen": 0 }
}
```
Response:
```json
{
  "jaar": 2026,
  "beste": "dga",
  "besparing_vs_slechtste": 22332.37,
  "break_even_rendement": 0.0556,
  "uitkomsten": [
    {"naam": "dga", "inkomen_netto": 94877.0, "vermogen_last": 2913.0,
     "totaal_netto": 91963.44, "toelichting": "vermogen in BV (...)"}
  ],
  "tips": ["..."]
}
```

### `POST /bereken`
Werkelijke situatie: meerdere inkomstenbronnen samen in één box 1-berekening (geen
optimalisatie). Voor wie parttime onderneemt én in dienst is, of meerdere baantjes heeft.

Request: `{"jaar":2026,"loon":40000,"winst":25000,"uitkering_pensioen":0,"resultaat_overige_werkzaamheden":0,"urencriterium":true,"aow_gerechtigd":false,"eigen_woning":{...},"box3":{...}}`
(meerdere banen → tel het loon op; meerdere ondernemingen → tel de winst op.)
Response: `{bruto_inkomen, belastbaar_box1, heffing_box1, heffing_box3, verzamelinkomen, heffingskortingen, kortingen{...}, verzilverd, verdampt, te_betalen, netto, gemiddeld_tarief, waarschuwingen[]}`.

### `POST /mix`
Gegeven een vast loon, de gunstigste vorm voor EXTRA activiteit (marginaal bovenop het loon).

Request: `{"jaar":2026,"vast_loon":40000,"extra_waarde":30000,"urencriterium":false,"gebruikelijk_loon":null}`
Response: `{jaar, vast_loon, extra_waarde, basis_belasting, beste, opties[{naam,label,totale_belasting,marginale_belasting,netto_extra,marginaal_tarief}], waarschuwingen[]}`.

`/bereken` accepteert optioneel een `partner`-blok (zelfde velden) → `partner` + `huishouden`-totalen in de respons.
`/optimaliseer` en `/rapport` accepteren `spaargeld` (banktegoeden) náást `prive_vermogen` (beleggingen) — apart belast in box 3.

### `POST /toerekening`
Optimale verdeling van de eigen woning tussen twee fiscale partners (art. 2.17).

Request: `{"jaar":2026,"inkomen_a":120000,"inkomen_b":20000,"woz_waarde":400000,"hypotheekrente":7000}`
Response: `{optimale_fractie_partner_a, totaal_optimaal, totaal_5050, besparing_vs_5050, toelichting}`

### `POST /rapport`
Presenteerbaar rapport (voor boekhouder/Belastingdienst): invoer → motor → gestructureerd,
herleidbaar resultaat. Zelfde body als `/optimaliseer`, plus optioneel `"formaat":"markdown"`.

- Default → JSON: `{metadata, invoer, advies, wettelijke_grondslag[], aannames_en_benaderingen[], disclaimer}`.
- `"formaat":"markdown"` → `{formaat:"markdown", inhoud:"# Fiscaal optimalisatierapport ..."}`.

Het rapport is **formaat-agnostisch**; render JSON naar PDF/HTML/print in een losse laag.

## Conventies
- Bedragen in euro's; percentages als fractie (`0.0556` = 5,56%).
- Velden grotendeels optioneel met defaults; alleen `economische_waarde` is verplicht
  bij `/optimaliseer`. Ontbrekende verplichte velden → `400 {"error": ...}`.
- CORS open (`Access-Control-Allow-Origin: *`) voor een lokale browserclient.
