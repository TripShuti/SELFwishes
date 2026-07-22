# SELFwishes

Self-hosted Genshin Impact wish history tracker. Alternative to paimon.moe.

<img width="1145" height="2704" alt="image" src="https://github.com/user-attachments/assets/9f9ce910-7513-4497-8eb4-04f81661c3ca" />


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

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `DATA_DIR` | `./data/` | Directory for the SQLite database |

## Tech Stack

- **Backend:** Python / FastAPI / SQLAlchemy / aiosqlite
- **Frontend:** Vue 3 / Vite / Pinia
- **Deploy:** Docker / docker-compose
