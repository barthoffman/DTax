"""Rekenkern Nederlandse inkomstenbelasting (box 1 + heffingskortingen + box 3).

De jaarlijks wijzigende cijfers staan in `params/<jaar>.json` (met bron-ID's naar
`bronnen/bronregister.md`); de rekenlogica staat in deze package. Bij een
wetswijziging hoeft in beginsel alleen de params-file te worden bijgewerkt.

Belangrijkste ingang: `bereken_persoon(persoon, jaar)` en `bereken_huishouden(...)`.
"""

from .model import Persoon, EigenWoning, Box3Vermogen, Onderneming, Huishouden
from .params import laad_params, Params
from .engine import bereken_persoon, bereken_huishouden, ResultaatPersoon
from .toeslagen import Huishoudprofiel
from .optimalisatiemotor import Situatie, Advies, optimaliseer

__all__ = [
    "Persoon",
    "EigenWoning",
    "Box3Vermogen",
    "Onderneming",
    "Huishouden",
    "Huishoudprofiel",
    "laad_params",
    "Params",
    "bereken_persoon",
    "bereken_huishouden",
    "ResultaatPersoon",
    "Situatie",
    "Advies",
    "optimaliseer",
]
