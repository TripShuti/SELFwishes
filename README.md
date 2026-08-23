# SELFwishes

Self-hosted Genshin Impact wish history tracker. Alternative to paimon.moe.


<img width="1145" height="1684" alt="2d3dddce-1798-4c18-98cb-62f6baf14ef7" src="https://github.com/user-attachments/assets/524ddf10-5876-4911-9c99-0ee585b0947c" />



## Features

- Import wish history via authkey URL from the game
- Per-banner-type statistics (Character, Weapon, Standard, Beginner, Chronicled)
- Pity tracking with 50/50 detection
- Multi-account support with comparison
- Sortable wish table with pagination


## Quick Start

```bash
git clone https://github.com/TripShuti/SELFwishes
cd SELFwishes/
docker compose up -d --build
```

Open http://localhost:6767

### Getting the authkey URL

1. Open PowerShell 
2. Run the [Paimon.moe getlink script](https://paimon.moe/wish/import):
   ```powershell
   Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex "&{$((New-Object System.Net.WebClient).DownloadString('https://gist.github.com/MadeBaruna/1d75c1d37d19eca71591ec8a31178235/raw/getlink.ps1'))} global"
   ```
3. Copy the output URL and paste it in SELFwishes → Import

## Development

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Data & Backups

The SQLite database lives on the host machine at `/opt/selfwishes/data/wishes.db` (bind-mounted to `/app/data` inside the container). It survives container rebuilds, `docker compose down`, and deleting the project folder.

**Backup:**

```bash
cp /opt/selfwishes/data/wishes.db wishes-backup.db
```

**Restore / drop in your own DB:**

```bash
docker compose down
cp wishes-backup.db /opt/selfwishes/data/wishes.db
docker compose up -d
```

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

| Variable | Default | Description |
|----------|---------|-------------|
| `DATA_DIR` | `./data/` | Directory for the SQLite database |

## Tech Stack

- **Backend:** Python / FastAPI / SQLAlchemy / aiosqlite
- **Frontend:** Vue 3 / Vite / Pinia
- **Deploy:** Docker / docker-compose
