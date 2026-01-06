from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
from typing import List, Optional
from datetime import datetime
import re

app = FastAPI(title="QuickFilings API")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SearchRequest(BaseModel):
    ticker: str
    file_types: List[str]
    quarters_back: int = 6
    annuals_back: int = 5
    exchange: str = "auto"

class FileInfo(BaseModel):
    name: str
    url: str
    type: str
    date: str
    size: str

class SearchResponse(BaseModel):
    company: dict
    files: List[FileInfo]

# SEC EDGAR headers (required by SEC)
SEC_HEADERS = {
    "User-Agent": "QuickFilings/1.0 (quickfilings@example.com)"
}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/")
async def root():
    return {"message": "QuickFilings API - Use /search endpoint to fetch SEC filings"}

async def get_cik_from_ticker(ticker: str) -> Optional[str]:
    """Get CIK number from ticker symbol using SEC's company tickers JSON"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://www.sec.gov/files/company_tickers.json",
                headers=SEC_HEADERS,
                timeout=10.0
            )

            if response.status_code == 200:
                data = response.json()
                # Search for the ticker
                for item in data.values():
                    if item.get("ticker", "").upper() == ticker.upper():
                        # CIK is returned as integer, need to pad with zeros to 10 digits
                        cik = str(item["cik_str"]).zfill(10)
                        return cik

    except Exception as e:
        print(f"Error fetching CIK: {e}")

    return None

async def get_company_filings(cik: str, ticker: str, file_types: List[str],
                              quarters_back: int, annuals_back: int) -> SearchResponse:
    """Fetch company filings from SEC EDGAR"""

    try:
        async with httpx.AsyncClient() as client:
            # Get company submissions
            response = await client.get(
                f"https://data.sec.gov/submissions/CIK{cik}.json",
                headers=SEC_HEADERS,
                timeout=15.0
            )

            if response.status_code != 200:
                raise HTTPException(status_code=404, detail="Company not found")

            data = response.json()
            company_name = data.get("name", ticker)

            # Get recent filings
            recent_filings = data.get("filings", {}).get("recent", {})

            files = []

            # Map frontend file types to SEC form types
            form_type_map = {
                "quarterlyAnnual": ["10-Q", "10-K"],
                "form8k": ["8-K"],
                "earnings": ["8-K"],  # Earnings are often in 8-K
                "presentations": ["UPLOAD", "425", "8-K"]  # Investor presentations
            }

            # Collect form types to search for
            forms_to_fetch = set()
            for file_type in file_types:
                if file_type in form_type_map:
                    forms_to_fetch.update(form_type_map[file_type])

            # Process filings
            accession_numbers = recent_filings.get("accessionNumber", [])
            filing_dates = recent_filings.get("filingDate", [])
            form_types = recent_filings.get("form", [])
            primary_documents = recent_filings.get("primaryDocument", [])

            quarterly_count = 0
            annual_count = 0

            for i in range(len(accession_numbers)):
                form_type = form_types[i]

                # Check if we want this form type
                if form_type not in forms_to_fetch:
                    continue

                # Limit by quarters and annuals
                if form_type == "10-Q":
                    if quarterly_count >= quarters_back:
                        continue
                    quarterly_count += 1
                elif form_type == "10-K":
                    if annual_count >= annuals_back:
                        continue
                    annual_count += 1

                accession = accession_numbers[i].replace("-", "")
                filing_date = filing_dates[i]
                primary_doc = primary_documents[i]

                # Build document URL
                doc_url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession}/{primary_doc}"

                # Determine file name
                if form_type == "10-K":
                    file_name = f"{ticker}_10K_{filing_date}.htm"
                    file_type_label = "10-K Annual Report"
                elif form_type == "10-Q":
                    file_name = f"{ticker}_10Q_{filing_date}.htm"
                    file_type_label = "10-Q Quarterly Report"
                elif form_type == "8-K":
                    file_name = f"{ticker}_8K_{filing_date}.htm"
                    file_type_label = "8-K Current Report"
                else:
                    file_name = f"{ticker}_{form_type}_{filing_date}.htm"
                    file_type_label = form_type

                files.append(FileInfo(
                    name=file_name,
                    url=doc_url,
                    type=file_type_label,
                    date=filing_date,
                    size="N/A"  # SEC doesn't provide size easily
                ))

                # Limit total files
                if len(files) >= 50:
                    break

            return SearchResponse(
                company={
                    "name": company_name,
                    "ticker": ticker,
                    "cik": cik
                },
                files=files
            )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching filings: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching filings: {str(e)}")

@app.post("/search")
async def search_company(request: SearchRequest) -> SearchResponse:
    """Search for company filings by ticker"""

    ticker = request.ticker.upper().strip()

    if not ticker:
        raise HTTPException(status_code=400, detail="Ticker symbol is required")

    if len(request.file_types) == 0:
        raise HTTPException(status_code=400, detail="At least one file type must be selected")

    # Get CIK from ticker
    cik = await get_cik_from_ticker(ticker)

    if not cik:
        raise HTTPException(
            status_code=404,
            detail=f"Company with ticker '{ticker}' not found. Please verify the ticker symbol."
        )

    # Fetch filings
    return await get_company_filings(
        cik=cik,
        ticker=ticker,
        file_types=request.file_types,
        quarters_back=request.quarters_back,
        annuals_back=request.annuals_back
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
