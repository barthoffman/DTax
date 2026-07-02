# Deployment & infrastructuur — watmagwel.nl

Hoe de hele keten is opgezet (opgesteld 2026-07-02). Bewaar dit; het beschrijft waar alles
staat en hoe je het bedient.

---

## 1. Overzicht

```
browser → Cloudflare (HTTPS/edge) → Cloudflare Tunnel → container op de Mac mini (127.0.0.1:8010) → app
```

- **App**: dependency-vrij (Python-stdlib), draait in een Docker/OrbStack-container op de Mac mini.
- **Toegang**: e-mail-OTP-login (Gmail SMTP) + een door de admin beheerde allowlist.
- **Publiek bereikbaar** via de Cloudflare-tunnel; de origin heeft géén open inkomende poort.

| Onderdeel | Waarde |
|---|---|
| Test-URL (delen met testers) | **https://staging.watmagwel.nl** |
| Root (nu live op de mini, gereserveerd voor prod) | https://watmagwel.nl |
| Repo (GitHub, privé) | `git@github.com:barthoffman/DTax.git` |
| Lokale werkkopie | `/Users/barthoffman/Developer/Claude/Belastingen` |
| Host (Mac mini) | SSH-alias `barts-mac-mini` (user `bearings-staging`) |

---

## 2. Domein & DNS (Cloudflare)

- **Domein** `watmagwel.nl` — geregistreerd bij **Antagonist** (2026-07-02).
- **Nameservers** (bij Antagonist ingesteld → SIDN): `bowen.ns.cloudflare.com` + `jewel.ns.cloudflare.com`.
- **Cloudflare-zone** `watmagwel.nl` staat Active (zelfde account als `bearingsmodel.com`).
- **DNS-records** in de watmagwel.nl-zone (allemaal **Proxied / oranje**):

| Naam | Type | Wijst naar |
|---|---|---|
| `watmagwel.nl` (@) | Tunnel/CNAME | tunnel `bearings-staging` (`…cfargotunnel.com`) |
| `staging.watmagwel.nl` | Tunnel/CNAME | zelfde tunnel |
| `www` | — | bewust verwijderd (ingress staat wel klaar) |

> Universal SSL dekt `*.watmagwel.nl`, dus subdomeinen krijgen automatisch HTTPS.
> **DNSSEC**: bij Antagonist stond nog een DS-record; niet nodig, mag daar uit als je wilt.

---

## 3. Cloudflare Tunnel

- **Tunnel-naam**: `bearings-staging` — **ID**: `6b6313a1-39fa-4b7c-9b1c-3f6040f45ad5`
- Draait op de Mac mini via **launchd**: `com.cloudflare.cloudflared`
- Config: `~/.cloudflared/config.yml` (user `bearings-staging`); credentials-JSON + `cert.pem` staan in `~/.cloudflared/`.
- **Ingress-regels** (volgorde telt; catch-all 404 als laatste):

```yaml
ingress:
- hostname: staging.bearingsmodel.com   # ander product, niet aankomen
  service: http://localhost:80
- hostname: watmagwel.nl
  service: http://localhost:8010
- hostname: www.watmagwel.nl
  service: http://localhost:8010
- hostname: staging.watmagwel.nl
  service: http://localhost:8010
- service: http_status:404
```

**Config valideren / tunnel herstarten** (op de mini):
```bash
/usr/local/bin/cloudflared tunnel ingress validate
launchctl kickstart -k gui/$(id -u)/com.cloudflare.cloudflared    # ~2 sec blip, ook voor staging.bearingsmodel.com
```
> Let op: de `cloudflared`-`cert.pem` is alleen voor `bearingsmodel.com` geautoriseerd. DNS-records
> voor watmagwel.nl daarom **handmatig in het Cloudflare-dashboard** zetten (niet via `cloudflared tunnel route dns`).

---

## 4. De container op de Mac mini

- Docker via OrbStack: binary `~/.orbstack/bin/docker` (staat niet in de non-interactieve PATH → volledig pad gebruiken).
- Repo gecloned op: `~/DTax` (agent-forwarding gebruikt de GitHub-toegang van wie SSH't).
- **Container**: naam `watmagwel`, image `watmagwel`, `--restart unless-stopped` (overleeft reboots).

```bash
D=~/.orbstack/bin/docker
$D run -d --name watmagwel --restart unless-stopped \
  -p 127.0.0.1:8010:8000 \
  -v ~/DTax/rekenkern/.env:/app/rekenkern/.env:ro \
  -v ~/watmagwel-authdata:/app/rekenkern/authdata \
  watmagwel
```

| Wat | Waar |
|---|---|
| Poort (host → container) | `127.0.0.1:8010` → `8000` (alleen localhost; tunnel bereikt 'm) |
| SMTP-config (secret) | mount `~/DTax/rekenkern/.env` (read-only) — **niet in git** |
| Data (allowlist + sessies) | volume `~/watmagwel-authdata` → `/app/rekenkern/authdata` (persistent) |

**Status / logs / herstart:**
```bash
$D ps --filter name=watmagwel
$D logs --tail 50 watmagwel        # o.a. [AUTH]/SMTP-fouten
$D restart watmagwel
curl -s localhost:8010/health      # {"status":"ok"}
```

---

## 5. De app

- **Python-stdlib, geen dependencies.** `Dockerfile` gebruikt `python:3.12-slim` (host-Python is 3.9, te oud).
- `api.py` serveert `client/index.html` + de endpoints; bindt via env `HOST`/`PORT` (in de container `0.0.0.0:8000`).
- **Publieke endpoints** (geen login): `/`, `/health`, `/auth/*`, en de param-GET's (`/aow`, `/leegwaarde`, `/jaren`, `/grondslag`).
- **Achter login** (sessie vereist): alle reken-endpoints (`/advies`, `/vermogensadvies`, `/straks`, …) + `/admin/allowlist`.

---

## 6. Authenticatie (`auth.py`)

- **Model**: e-mail-OTP. Wie mag: de **admin** + iedereen op de **allowlist**.
- **Admin**: env `ADMIN_EMAIL` (default `bart.hoffman@gmail.com`) — mag altijd inloggen + beheert de allowlist via de knop **"Beheer toegang"**.
- **OTP**: 6 cijfers, 10 min geldig, eenmalig, max 5 pogingen, rate-limit 5/uur per adres.
- **Sessie**: HttpOnly-cookie, `SameSite=Lax`, 30 dagen; **Secure** alleen achter HTTPS (via `X-Forwarded-Proto` van de tunnel — lokaal http werkt dus ook).
- **Opslag** (in `authdata/`, gemount → persistent, **niet in git**): `allowlist.json`, `sessions.json`.
- **Dev-modus** (geen SMTP geconfigureerd): de OTP gaat naar het serverlog én komt in de `/auth/otp`-respons (`dev_code`), zodat je lokaal zonder mail kunt testen. Met SMTP verdwijnt dat automatisch.

### E-mail (Gmail SMTP)
Config staat in **`rekenkern/.env`** (gitignored; template in `.env.example`). Vereist: Gmail met **2FA aan** + een **app-wachtwoord**.
```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=bart.hoffman@gmail.com
SMTP_PASS=<gmail app-wachtwoord, 16 tekens zonder spaties>
SMTP_FROM=bart.hoffman@gmail.com
ADMIN_EMAIL=bart.hoffman@gmail.com
```
Wisselen van maildienst = alleen andere `SMTP_*`-waarden (bijv. Brevo `smtp-relay.brevo.com`) — geen codewijziging.

---

## 7. Deployen (nieuwe versie uitrollen)

Vanaf de lokale werkkopie, na `git push`:
```bash
./deploy.sh        # SSH → git pull → image bouwen → container vervangen → health-check
```
`deploy.sh` gebruikt **SSH-agent-forwarding** voor de GitHub-pull op de mini. Host override: `DEPLOY_HOST=... ./deploy.sh`.

---

## 8. Secrets & wat NIET in git staat

`.gitignore` sluit uit: `rekenkern/.env` (SMTP-wachtwoord) en `rekenkern/authdata/` (allowlist + sessietokens).
Die leven **alleen op de mini** (`~/DTax/rekenkern/.env`, `~/watmagwel-authdata/`) en lokaal.

---

## 9. Veelvoorkomende taken

| Taak | Hoe |
|---|---|
| Tester toevoegen | Inloggen als admin → **Beheer toegang** → e-mail toevoegen (die persoon krijgt dan een echte inlogcode per mail) |
| Update uitrollen | `git push` → `./deploy.sh` |
| Container herstarten | `ssh barts-mac-mini '~/.orbstack/bin/docker restart watmagwel'` |
| Tunnel herstarten | `ssh barts-mac-mini 'launchctl kickstart -k gui/$(id -u)/com.cloudflare.cloudflared'` |
| Logs bekijken | `ssh barts-mac-mini '~/.orbstack/bin/docker logs --tail 50 watmagwel'` |
| `www` activeren | DNS-record `www` (Tunnel/CNAME, proxied) toevoegen in Cloudflare — de ingress staat er al |
| Naar prod (root) | Root-DNS `watmagwel.nl` ompunten naar de prod-server; staging blijft op de mini |

---

## 10. Geleerde valkuilen (voor de volgende keer)

- **DNSSEC** bij de oude registrar (Antagonist) kan een verse Cloudflare-zone op "pending" houden / resolutie breken — laat de DS er bij twijfel afhalen.
- **Universal SSL** wordt pas ná zone-activatie geprovisioned (~15 min); tot dan geeft HTTPS een `handshake failure`. Even wachten.
- **Cookie `Secure`** werkt alleen over HTTPS — daarom conditioneel op `X-Forwarded-Proto` (anders werkt lokaal testen op http niet).
- **`cloudflared tunnel route dns`** maakte het record in de verkeerde zone (cert alleen voor bearingsmodel.com) → DNS **handmatig** in het dashboard zetten.
- Host-Python 3.9 is te oud → **container** met moderne Python (zoals de bestaande staging).
