from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import httpx

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

ALPHA_VANTAGE_API_KEY = "UGLDAKBR7W6AO6UW"
TWELVE_DATA_API_KEY = "573f14c758bb40ec8916d6719c7a805b"

async def fetch_yahoo(symbol):
    url = f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={symbol}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code != 200:
            return None
        try:
            data = response.json()
            quote = data["quoteResponse"]["result"][0]
            return {
                "symbol": quote["symbol"],
                "price": quote["regularMarketPrice"],
                "currency": quote.get("currency", "USD"),
                "timestamp": quote.get("regularMarketTime"),
                "source": "Yahoo Finance"
            }
        except:
            return None

async def fetch_twelve(symbol):
    url = f"https://api.twelvedata.com/price?symbol={symbol}&apikey={TWELVE_DATA_API_KEY}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code != 200:
            return None
        try:
            data = response.json()
            return {
                "symbol": symbol,
                "price": float(data.get("price", 0)),
                "currency": "USD",
                "timestamp": None,
                "source": "Twelve Data"
            }
        except:
            return None

async def fetch_alpha(symbol):
