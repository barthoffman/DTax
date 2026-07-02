"""E-mail-OTP-authenticatie — stdlib-only, geen dependencies.

Wie mag inloggen: de **admin** (env ``ADMIN_EMAIL``, default bart.hoffman@gmail.com)
plus elk adres op de **allowlist** (door de admin toegevoegd). Login gaat via een
6-cijferige code per mail (of, zonder SMTP-config, via het serverlog — dev-modus).
Na verificatie een sessietoken in een HttpOnly-cookie.

Opslag: JSON-bestanden in ``authdata/`` (allowlist + sessies overleven een herstart).
OTP-codes en rate-limiting staan in het geheugen (kortlevend).

SMTP later inpluggen via env-vars: ``SMTP_HOST``, ``SMTP_PORT`` (default 587),
``SMTP_USER``, ``SMTP_PASS``, ``SMTP_FROM``. Zolang ``SMTP_HOST`` leeg is → dev-modus.
"""

from __future__ import annotations

import json
import os
import secrets
import smtplib
import time
from email.message import EmailMessage
from pathlib import Path

_DIR = Path(__file__).resolve().parent / "authdata"
_DIR.mkdir(exist_ok=True)
_ALLOW = _DIR / "allowlist.json"
_SESS = _DIR / "sessions.json"

ADMIN_EMAIL = (os.environ.get("ADMIN_EMAIL") or "bart.hoffman@gmail.com").strip().lower()
OTP_TTL = 600              # code 10 minuten geldig
SESSION_TTL = 30 * 86400   # sessie 30 dagen
MAX_TRIES = 5              # max verkeerde pogingen per code
RATE_WINDOW = 3600         # rate-limit-venster (1 uur)
RATE_MAX = 5               # max OTP-aanvragen per e-mail per venster

_otps: dict[str, dict] = {}    # email -> {code, expires, tries}
_rate: dict[str, list] = {}    # email -> [timestamps]


def _norm(email) -> str:
    return (email or "").strip().lower()


def _load(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def _save(path: Path, data) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


# --- allowlist -------------------------------------------------------------
def load_allowlist() -> list[str]:
    return _load(_ALLOW, [])


def _save_allowlist(lst) -> None:
    _save(_ALLOW, sorted({_norm(e) for e in lst if _norm(e)}))


def is_admin(email) -> bool:
    return _norm(email) == ADMIN_EMAIL


def is_allowed(email) -> bool:
    e = _norm(email)
    return bool(e) and (e == ADMIN_EMAIL or e in load_allowlist())


def add_email(email) -> list[str]:
    lst = load_allowlist()
    e = _norm(email)
    if e and e not in lst:
        lst.append(e)
        _save_allowlist(lst)
    return load_allowlist()


def remove_email(email) -> list[str]:
    _save_allowlist([e for e in load_allowlist() if e != _norm(email)])
    return load_allowlist()


# --- sessies ---------------------------------------------------------------
def create_session(email) -> str:
    tok = secrets.token_urlsafe(32)
    s = _load(_SESS, {})
    s[tok] = {"email": _norm(email), "expires": time.time() + SESSION_TTL}
    _save(_SESS, s)
    return tok


def session_email(tok) -> str | None:
    if not tok:
        return None
    s = _load(_SESS, {})
    rec = s.get(tok)
    if not rec:
        return None
    if rec["expires"] < time.time():
        s.pop(tok, None)
        _save(_SESS, s)
        return None
    return rec["email"]


def delete_session(tok) -> None:
    s = _load(_SESS, {})
    if s.pop(tok, None) is not None:
        _save(_SESS, s)


# --- OTP -------------------------------------------------------------------
def _rate_ok(email) -> bool:
    now = time.time()
    e = _norm(email)
    hits = [t for t in _rate.get(e, []) if t > now - RATE_WINDOW]
    if len(hits) >= RATE_MAX:
        _rate[e] = hits
        return False
    hits.append(now)
    _rate[e] = hits
    return True


def request_otp(email) -> dict:
    """Genereert + verstuurt een OTP als het adres bekend is. Lekt dat niet naar buiten:
    de respons is altijd hetzelfde (geen e-mail-enumeratie)."""
    e = _norm(email)
    if is_allowed(e) and _rate_ok(e):
        code = f"{secrets.randbelow(1_000_000):06d}"
        _otps[e] = {"code": code, "expires": time.time() + OTP_TTL, "tries": 0}
        _send_otp(e, code)
    return {"sent": True}


def verify_otp(email, code) -> str | None:
    """Controleert de code; bij succes → nieuw sessietoken, anders None."""
    e = _norm(email)
    rec = _otps.get(e)
    if not rec or rec["expires"] < time.time():
        return None
    rec["tries"] += 1
    if rec["tries"] > MAX_TRIES:
        _otps.pop(e, None)
        return None
    if str(code).strip() != rec["code"]:
        return None
    _otps.pop(e, None)
    return create_session(e)


def _send_otp(email, code) -> None:
    host = os.environ.get("SMTP_HOST")
    text = (f"Je inlogcode voor het Belastingen-dashboard is: {code}\n\n"
            f"De code is 10 minuten geldig. Niet aangevraagd? Negeer deze mail.")
    if not host:  # dev-modus: geen SMTP geconfigureerd → naar het serverlog
        print(f"[AUTH][dev] OTP voor {email}: {code}  (10 min geldig)", flush=True)
        return
    msg = EmailMessage()
    msg["Subject"] = "Je inlogcode voor het Belastingen-dashboard"
    msg["From"] = os.environ.get("SMTP_FROM") or os.environ.get("SMTP_USER") or ADMIN_EMAIL
    msg["To"] = email
    msg.set_content(text)
    user, pw = os.environ.get("SMTP_USER"), os.environ.get("SMTP_PASS")
    with smtplib.SMTP(host, int(os.environ.get("SMTP_PORT", 587)), timeout=15) as smtp:
        smtp.starttls()
        if user:
            smtp.login(user, pw)
        smtp.send_message(msg)
