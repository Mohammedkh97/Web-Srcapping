# Web Scraper App

A FastAPI-based web scraping application with Scrape.do integration.

## Features

- Web scraping using Scrape.do API
- HTML parsing for legal consultancy content
- Data export (JSON, CSV)
- SQLite database storage
- Modern responsive UI
- REST API for integration

---

## 🐳 Docker Setup (Recommended)

### Quick Start

```bash
# Build and run
docker compose up -d

# View logs
docker compose logs -f

# Stop
docker compose down
```

### Development Mode (with hot-reload)

```bash
docker compose --profile dev up web-scraper-dev
```

### Environment Variables

Create a `.env` file or set these variables:

```bash
SCRAPEDO_TOKEN=your_scrape_do_token
```

---

## 🐍 Local Setup (Alternative)

### 1. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env with your Scrape.do API token
```

### 4. Run the application

```bash
uvicorn app.main:app --reload
```

---

## 🌐 Access the Application

| Mode                 | URL                   |
| -------------------- | --------------------- |
| Production (Docker)  | http://localhost:8000 |
| Development (Docker) | http://localhost:8001 |
| Local                | http://localhost:8000 |

---

## 📡 API Endpoints

| Method | Endpoint            | Description          |
| ------ | ------------------- | -------------------- |
| POST   | `/api/scrape`       | Scrape a URL         |
| GET    | `/api/history`      | Get scraping history |
| GET    | `/api/history/{id}` | Get specific record  |
| DELETE | `/api/history/{id}` | Delete record        |
| GET    | `/api/export/json`  | Export as JSON       |
| GET    | `/api/export/csv`   | Export as CSV        |

---

## 📁 Project Structure

```
web-scraper/
├── app/
│   ├── main.py           # FastAPI entry
│   ├── config.py         # Configuration
│   ├── api/routes.py     # API endpoints
│   ├── models/           # Pydantic schemas
│   ├── services/         # Business logic
│   └── database/         # SQLAlchemy models
├── static/               # CSS & JS
├── templates/            # HTML templates
├── data/                 # Database storage
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

---

## 🔧 Environment Variables

| Variable         | Description              | Default                       |
| ---------------- | ------------------------ | ----------------------------- |
| `SCRAPEDO_TOKEN` | Your Scrape.do API token | -                             |
| `DATABASE_URL`   | SQLite database path     | `sqlite:///./data/scraper.db` |
