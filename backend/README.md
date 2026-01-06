# QuickFilings Backend

FastAPI backend for fetching SEC EDGAR filings.

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python main.py
```

Server will run on `http://localhost:8000`

## API Endpoints

### GET /health
Health check endpoint

### POST /search
Search for company filings

Request body:
```json
{
  "ticker": "AAPL",
  "file_types": ["quarterlyAnnual", "earnings"],
  "quarters_back": 6,
  "annuals_back": 5,
  "exchange": "auto"
}
```

## Deployment

### Render.com

1. Create a new Web Service
2. Connect your GitHub repository
3. Use these settings:
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Environment**: Python 3

### Environment Variables

No environment variables required - uses SEC's public API.

## Notes

- Uses SEC EDGAR public API
- Requires proper User-Agent header per SEC guidelines
- Rate limited by SEC (10 requests/second max)
