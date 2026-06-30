# Werkafspraken — Belastingen-dashboard

Project: dashboard dat een Nederlandse inwoner helpt zijn fiscale positie wettelijk
te optimaliseren (zie `README.md`).

## Vaste werkwijze (elke sessie volgen)

1. **Journaal bijhouden — automatisch.** Werk `JOURNAAL.md` bij zodra er een
   belangrijke **beslissing**, **bevinding**, **correctie** of een nieuw **open punt**
   ontstaat. Nieuwste datum bovenaan, type-label gebruiken (BESLISSING / BEVINDING /
   CORRECTIE / OPEN PUNT), en de bron-ID of het KB-bestand vermelden. Doe dit zonder
   dat de gebruiker er apart om vraagt.
2. **Bronnen registreren.** Elk nieuw bedrag/percentage/regel krijgt een bron-ID en
   komt in `bronnen/bronregister.md` (wet, artikel, URL, versie/geldigheidsdatum,
   opgehaald-op). Primaire bron = `wetten.overheid.nl`.
3. **Geen cijfer zonder bron.** Markeer voorlopige/onzekere cijfers expliciet.
4. **Datums absoluut** (bv. 2026-06-28), nooit "vandaag/gisteren".
5. **Twee belastingjaren** parallel onderhouden: 2025 én 2026.
6. **Interpretatieruimte markeren.** Waar de wet onduidelijk is, noteren als kandidaat
   voor "onderbouwd standpunt richting Belastingdienst".

## Mappen
- `knowledge-base/` — inhoudelijke modules (00 t/m 07).
- `bronnen/bronregister.md` — centraal bron-/versieregister voor update-checks.
- `JOURNAAL.md` — log van beslissingen en bevindingen.
