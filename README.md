# QuickFilings

Download SEC financials and presentations for any public company instantly.

🔗 **Live Demo**: [https://cnpayton.github.io/quickfilings-frontend](https://cnpayton.github.io/quickfilings-frontend)

## Features

- 📊 Search any public company by ticker symbol
- 📄 Download quarterly (10-Q) and annual (10-K) reports
- 📈 Access 8-K current reports and earnings presentations
- 🔍 Configurable date ranges (1-5 years of data)
- 💾 Bulk download all files at once
- 🔗 Copy direct links to SEC filings
- 👀 Preview files before downloading

## Project Structure

```
quickfilings-frontend/
├── index.html          # Frontend single-page application
├── backend/           # FastAPI backend
│   ├── main.py       # Backend API server
│   ├── requirements.txt
│   ├── render.yaml   # Render deployment config
│   └── README.md     # Backend documentation
└── README.md         # This file
```

## Quick Start

### Frontend Only (GitHub Pages)

The frontend is automatically deployed via GitHub Pages. Just visit the live demo link above.

### Local Development

#### 1. Run the Backend

```bash
cd backend
pip install -r requirements.txt
python main.py
```

Backend will run on `http://localhost:8000`

#### 2. Open the Frontend

Simply open `index.html` in your browser. The frontend automatically detects localhost and connects to your local backend.

```bash
# Option 1: Direct file open
open index.html  # macOS
start index.html # Windows
xdg-open index.html # Linux

# Option 2: Simple HTTP server
python -m http.server 8080
# Then visit http://localhost:8080
```

## Deployment

### Frontend (GitHub Pages)

1. Push to GitHub
2. Go to repository Settings → Pages
3. Set source to "Deploy from branch"
4. Select branch: `claude/resume-previous-work-3z4r9` (or your main branch)
5. Save - your site will be live at `https://<username>.github.io/<repo-name>`

### Backend (Render.com)

1. Create account on [Render.com](https://render.com)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: `quickfilings-backend`
   - **Root Directory**: `backend`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Click "Create Web Service"
6. Copy your Render URL (e.g., `https://quickfilings-backend-xyz.onrender.com`)
7. Update `index.html` line 458 with your backend URL

## How It Works

1. **Frontend** (`index.html`): Single-page application with vanilla JavaScript
2. **Backend** (`backend/main.py`): FastAPI server that:
   - Fetches company CIK from SEC's ticker mapping
   - Retrieves filings from SEC EDGAR API
   - Returns formatted filing data to frontend
3. **Data Source**: All data comes from SEC's public EDGAR API (free, no API key needed)

## API Endpoints

### `GET /health`
Health check endpoint

### `POST /search`
Search for company filings

**Request:**
```json
{
  "ticker": "AAPL",
  "file_types": ["quarterlyAnnual", "earnings"],
  "quarters_back": 6,
  "annuals_back": 5,
  "exchange": "auto"
}
```

**Response:**
```json
{
  "company": {
    "name": "Apple Inc.",
    "ticker": "AAPL",
    "cik": "0000320193"
  },
  "files": [
    {
      "name": "AAPL_10K_2024-09-28.htm",
      "url": "https://www.sec.gov/Archives/edgar/data/...",
      "type": "10-K Annual Report",
      "date": "2024-09-28",
      "size": "N/A"
    }
  ]
}
```

## Technologies

- **Frontend**: HTML, CSS, JavaScript (vanilla)
- **Backend**: Python, FastAPI, httpx
- **Data**: SEC EDGAR API
- **Hosting**: GitHub Pages (frontend), Render.com (backend)

## Limitations

- SEC rate limits API to 10 requests/second
- File sizes not available from SEC API
- Render free tier: backend may sleep after inactivity (first request takes ~30s to wake)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - feel free to use for any purpose

## Support

Issues? Please open a GitHub issue or contact the maintainer.

---

Built with ❤️ using SEC's public EDGAR database
