# Rekenkern (fase 2)

Python-rekenkern voor de Nederlandse inkomstenbelasting. Zet de regels uit de
knowledge base om in berekeningen. **Versie-data en logica zijn gescheiden:**

- `params/<jaar>.json` — alle jaarlijks wijzigende bedragen/percentages, met
  `_bron`-verwijzingen naar `../bronnen/bronregister.md`. Bij een wetswijziging pas je
  in beginsel alléén deze file aan.
- `belastingkern/` — de rekenlogica (verandert niet per jaar).

## Gebruik

```bash
cd rekenkern
python3 tests/test_kern.py          # tests (9 stuks, handmatig nagerekend)
python3 cli.py --jaar 2026 --loon 45000 --woz 350000 --rente 7000
```

Of vanuit code:

```python
from belastingkern import Persoon, EigenWoning, Box3Vermogen, bereken_persoon

p = Persoon(loon=45000, eigen_woning=EigenWoning(woz_waarde=350000,
            betaalde_hypotheekrente=7000))
print(bereken_persoon(p, 2026).samenvatting())
```

## Wat zit er in v1

| Onderdeel | Status |
|---|---|
| Box 1 schijventarief (onder/boven AOW) | ✅ |
| Eigenwoningforfait + hypotheekrente + Hillen | ✅ |
| Tariefsaanpassing eigen woning (art. 2.10) | ✅ (vereenvoudigd) |
| Algemene heffingskorting (afbouw op verzamelinkomen) | ✅ |
| Arbeidskorting (4 trajecten) | ✅ (onder AOW exact; boven AOW benaderd) |
| IACK, ouderenkorting, alleenst.-ouderen, jonggehandicapten | ✅ |
| Box 3 forfaitair (3 categorieën, heffingvrij, schuldendrempel, groen) | ✅ |
| Verzilvering / verdamping (art. 8.8) | ✅ |

## Nog NIET in v1 (bewuste afbakening — zie JOURNAAL.md)

- **Ondernemersfaciliteiten** (zelfstandigenaftrek, MKB-winstvrijstelling, KIA): winst
  uit onderneming wordt nu 1-op-1 als box 1-inkomen genomen. → aparte module fase 2b.
- **Box 3 tegenbewijs / werkelijk rendement (OWR)**: alleen forfaitair gerekend.
- **Toeslagen** (zorg/huur/kindgebonden/kinderopvang): aparte module.
- **Pensioen-jaarruimte** (art. 3.127) als aftrek/optimalisatie.
- **Automatische partner-toerekening-optimalisatie** (art. 2.17): `bereken_huishouden`
  rekent nu beide partners door zoals ingevuld, optimaliseert de verdeling nog niet.
- **Uitbetaling minstverdienende partner** (art. 8.9, geboren < 1963).

Deze v1 is een **schatting**, geen aangifte. Onzekere 2026-cijfers (box 3-forfaits,
Hillen-%) zijn in de output als waarschuwing zichtbaar.
