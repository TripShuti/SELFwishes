# SELFwishes

Self-hosted Genshin Impact wish history tracker with manual browser-based imports,
PS5 cross-save support, pity statistics, and multiple accounts.

<img width="1145" height="1684" alt="2d3dddce-1798-4c18-98cb-62f6baf14ef7" src="https://github.com/user-attachments/assets/524ddf10-5876-4911-9c99-0ee585b0947c" />

## Features

- Import directly from a signed-in HoYoverse browser session, without installing the game on PC.
- Support PS5 progress linked to a global HoYoverse account.
- Update manually from the browser or a saved server connection; no scheduled updates.
- Keep existing history, deduplicate wishes, and show new wish counts by banner.
- Track character, weapon, standard, beginner, and Chronicled Wish statistics and pity.
- Switch between accounts, compare statistics, and browse a sortable, paginated wish table.
- Use the responsive dashboard on desktop or mobile.
- Keep importing with a game history URL as an alternative.

## Quick start

```bash
git clone https://github.com/TripShuti/SELFwishes
cd SELFwishes
docker compose up -d --build
```

Open `http://localhost:6767`, or your server's address. The included Compose file
stores data at `/opt/selfwishes/data` on the host. Use HTTPS when connecting a
browser to a server on another device: account cookies sent over plain HTTP are
not encrypted in transit.

Docker builds both browser connector ZIP packages automatically. No game client,
SSH connection, or local Python helper is needed for the browser workflow.

## Connect your browser

The connector runs in the browser where you sign in to HoYoverse. SELFwishes can
run on that same computer or on a separate home server. For PS5, use the HoYoverse
account linked to your PSN progress and select its matching Genshin UID.

### 1. Install the connector

Open **Set up the browser connector once** in SELFwishes and download the package
for your browser. The download links are served by your own SELFwishes instance.

| Browser | Installation and current support |
| --- | --- |
| Chrome / Edge / Chromium, desktop | Download the Chromium ZIP, unzip it, open the browser's Extensions page, enable **Developer mode**, choose **Load unpacked**, and select the extracted folder. |
| Firefox / LibreWolf 142+, desktop | Download the Firefox ZIP and unzip it. Open `about:debugging#/runtime/this-firefox`, choose **Load Temporary Add-on**, and select `manifest.json`. This unsigned development installation lasts until the browser restarts. Permanent installation in standard Firefox requires Mozilla signing. |
| Firefox on Android | Not tested or packaged for mobile installation. General Firefox extension support does not guarantee this connector works there. |
| Chrome on Android / Safari on iPhone | These packages do not support these browsers. Use an existing saved server connection from the mobile website instead. |

The ZIP packages are development builds, not signed browser-store releases.
For the Firefox signing requirement, see [Mozilla's distribution documentation](https://extensionworkshop.com/documentation/publish/signing-and-distribution-overview/).

### 2. Enable your SELFwishes address

1. Open the SELFwishes service tab.
2. Click the connector's toolbar icon. It opens a separate setup tab.
3. Check the displayed service address, including its port.
4. Click **Enable for this service** and approve the browser's permission request.
5. Click **Return to SELFwishes**.

Setup uses a full tab so the permission prompt does not disappear when a popup
closes. If permission is already granted, setup can finish without another prompt.
To test the prompt again, revoke the service's site permission in the browser's
extension manager, then repeat setup. Restarting the browser is not a reliable
way to reset granted permissions.

Enable only a SELFwishes server you own and trust: it will receive account session
cookies. Approving a hostname grants browser-level site access; the connector
additionally checks the exact approved origin, including its scheme and port.

### 3. Sign in and update

1. Sign in at [HoYoverse Account](https://account.hoyoverse.com/) in the same browser
   and profile. Use the account associated with the character you want to import.
2. Open SELFwishes and select that character's account, or use **Import** to connect
   another HoYoverse account.
3. Click **Update from browser**. The connector sends the selected session cookies
   to your server, which obtains a fresh wish-history key and imports new wishes.
4. Check the result panel: it shows the number of **new wishes**, the UID, check
   time, and counts by banner. **0 new wishes** means the available history is
   already up to date.

The first import reads the available history. Later browser/saved-connection
updates stop at wishes already stored. Old local history is retained. If a banner
request fails, the import reports an error rather than silently saving a partial
update. The app cannot recover old wishes no longer available from HoYoverse
unless they were saved elsewhere.

Each HoYoverse account needs its own connection. Selecting another UID does not
reuse the first account's authorization. If the browser login belongs to a
different UID, the server rejects the mismatch before saving the connection.
Chinese-server browser authentication is not implemented; this workflow uses
`hk4e_global`.

## Update later, renew, or disconnect

- **Update from browser** reconnects using the current browser login, then updates.
- **Use saved connection** uses the account cookies already stored on your server.
  The original computer and browser do not need to be running. This also works
  from the mobile website until the saved authorization expires.
- If authorization expires, sign in to HoYoverse again and click **Update from browser**.
- Updates happen only when requested. There is no background scheduler.

To remove a saved connection while keeping imported wishes:

```bash
docker exec selfwishes python -m app.connect_hoyo disconnect YOUR_GENSHIN_UID
```

Disconnect each associated UID if one HoYoverse account has several characters.
Removing the server copy does not revoke any copies of the same session held
elsewhere.

When updating an unpacked connector, replace its files and reload it from the
browser's extension manager. For temporary Firefox installs, use **Reload** in
`about:debugging`. Reload the SELFwishes page after updating the connector.

## How browser imports work

```text
HoYoverse login in your browser
  -> connector -> your approved SELFwishes server
  -> genAuthKeyByCookieToken -> fresh webview_gacha authkey
  -> getGachaLog -> new wishes -> SQLite and recalculated statistics
```

A normal website cannot read another site's protected cookies. The connector uses
the browser's cookies API, checks the requesting service origin and cookie store,
and forwards only `account_id_v2`, `account_mid_v2`, and `cookie_token_v2`.
Cookie stores and domains are kept separate. The page and content script receive
connection metadata and success/error messages, not the cookies or authkey.

The server verifies the UID and uses fixed HoYoverse API endpoints. HoYoverse
requests use HTTPS. Authkeys remain in memory during an import; saved account
cookies allow a new authkey to be obtained on each later update. The service does
not ask for or store your HoYoverse password.

## Credentials and security

An `authkey` is a temporary credential for reading wish history. The saved account
cookies have broader authorization and must be treated as account secrets.

| Stored file | Contents |
| --- | --- |
| `wishes.db` | Imported wishes, account metadata, and statistics. No account cookies or authkeys. |
| `.hoyo-sessions.json` | Saved HoYoverse account cookies and connection metadata, in plaintext, with file mode `0600`. |

File permissions limit ordinary filesystem access, but they are not encryption.
Root, Docker administrators, compromised server software, or someone with access
to a credential-containing backup could read this file. Build artifacts and Git
exclude saved sessions. The HTTP API does not return cookies, and the static
file handler blocks paths outside its public directory.

The app has **no built-in user authentication**. Keep it on a trusted LAN/VPN.
Anyone who can reach the unprotected app can read its wish history and invoke its
exposed operations. Before public exposure, add access control; if using proxy
login, verify that extension requests are supported, since the connector does
not forward the website's login cookies.

Use HTTPS for remote connections and protect backups. Do not enable request-body
logging for the connection endpoint, or log full HoYoverse URLs: wish-history URLs
contain authkeys. The application sanitizes expected upstream errors, but proxy,
debugging, or third-party logging configuration can still expose secrets.

## Alternative: import a game history URL

The original **Import** form still accepts a wish-history URL containing `authkey`.
For a Windows PC game client:

1. Open Genshin Impact and load **Wish History**.
2. Follow the current [Paimon.moe URL extraction guide](https://paimon.moe/wish/import).
3. Paste the resulting URL into SELFwishes -> **Import with a history URL**.

The optional `scripts/connect_hoyoverse.py` helper can also connect a LibreWolf
session through SSH. It is a fallback for existing setups, not a requirement for
the browser connector.

## Data and backups

Compose bind-mounts `/opt/selfwishes/data` to `/app/data`. Data survives image
rebuilds and `docker compose down`.

Use SQLite's backup API for a consistent database backup while the app is running:

```bash
docker exec selfwishes python -c 'import sqlite3, os; src = sqlite3.connect("/app/data/wishes.db"); dst = sqlite3.connect("/app/data/wishes-backup.db"); src.backup(dst); dst.close(); src.close(); os.chmod("/app/data/wishes-backup.db", 0o600)'
docker cp selfwishes:/app/data/wishes-backup.db ./wishes-backup.db
```

This backs up wish history, not saved login cookies. A backup of the entire data
directory also includes `.hoyo-sessions.json`; treat it as a credential backup.
You can reconnect your browser instead of backing up credentials.

To restore history, stop the service, replace `wishes.db` with the backup, and
start the service again. Keep a copy of the current database before replacing it.

**Migrate from the old named volume (`selfwishes_data`):**

```bash
mkdir -p /opt/selfwishes/data
docker run --rm -v selfwishes_data:/src -v /opt/selfwishes/data:/dest alpine sh -c "cp -a /src/. /dest/"
docker compose up -d --build
# once verified, remove the old volume:
docker volume rm selfwishes_data
```

**Migrate from an old bind-mount `./data` folder:**

```bash
mkdir -p /opt/selfwishes/data
cp -a ./data/. /opt/selfwishes/data/
docker compose up -d --build
```

## Configuration

| Variable | Default outside Docker | Compose value | Description |
| --- | --- | --- | --- |
| `DATA_DIR` | `data/` at the project root | `/app/data` | Directory for the SQLite database and private HoYoverse session file. |

## Development and validation

Backend:

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

In another terminal, build the connector packages before running the frontend:

```bash
python3 browser-extension/build.py
cd frontend
npm ci
npm run dev
```

Checks:

```bash
node --test browser-extension/tests/*.test.cjs
cd backend
python3 -m unittest discover -s tests -v
```

The connector source is in `browser-extension/shared`; `browser-extension/build.py`
creates unpacked packages under `browser-extension/dist` and downloadable ZIPs
under `frontend/public/extensions`. Generated packages, runtime databases, and
session files are excluded from Git.

## Tech stack

- Backend: Python / FastAPI / SQLAlchemy / aiosqlite / httpx
- Frontend: Vue 3 / Vite / Pinia
- Connector: Manifest V3 WebExtension for Chromium and Firefox
- Deployment: Docker / Docker Compose
