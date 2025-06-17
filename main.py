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

@app.get("/realtime")
async def get_live_price(symbol: str = Query(...), source: str = Query("yahoo")):
    symbol = symbol.upper()

    if source == "alpha":
        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={ALPHA_VANTAGE_API_KEY}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            if response.status_code != 200:
                return {"error": f"Alpha Vantage falló con status {response.status_code}"}
            try:
                data = response.json()
                quote = data.get("Global Quote", {})
                return {
                    "symbol": symbol,
                    "price": float(quote.get("05. price", 0)),
                    "currency": "USD",
                    "timestamp": quote.get("07. latest trading day"),
                    "source": "Alpha Vantage"
                }
            except Exception as e:
                return {"error": f"Error al leer JSON de Alpha Vantage: {str(e)}"}

    if source == "twelve":
        url = f"https://api.twelvedata.com/price?symbol={symbol}&apikey={TWELVE_DATA_API_KEY}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            if response.status_code != 200:
                return {"error": f"Twelve Data falló con status {response.status_code}"}
            try:
                data = response.json()
                return {
                    "symbol": symbol,
                    "price": float(data.get("price", 0)),
                    "currency": "USD",
                    "timestamp": None,
                    "source": "Twelve Data"
                }
            except Exception as e:
                return {"error": f"Error al leer JSON de Twelve Data: {str(e)}"}

    # Default to Yahoo Finance
    url = f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={symbol}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code != 200:
            return {"error": f"Yahoo Finance falló con status {response.status_code}"}
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
        except Exception as e:
            return {"error": f"Error al leer JSON de Yahoo Finance: {str(e)}"}
