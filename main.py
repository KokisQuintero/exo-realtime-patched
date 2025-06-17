from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import httpx

app = FastAPI(title="EXO-FIN GPT RealTime API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

ALPHA_VANTAGE_API_KEY = "UGLDAKBR7W6AO6UW"
TWELVE_DATA_API_KEY = "573f14c758bb40ec8916d6719c7a805b"

async def fetch_yahoo(symbol: str):
    try:
        url = f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={symbol}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=5)
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

async def fetch_twelve(symbol: str):
    try:
        url = f"https://api.twelvedata.com/price?symbol={symbol}&apikey={TWELVE_DATA_API_KEY}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=5)
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

async def fetch_alpha(symbol: str):
    try:
        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={ALPHA_VANTAGE_API_KEY}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=5)
            data = response.json()
            quote = data.get("Global Quote", {})
            return {
                "symbol": symbol,
                "price": float(quote.get("05. price", 0)),
                "currency": "USD",
                "timestamp": quote.get("07. latest trading day"),
                "source": "Alpha Vantage"
            }
    except:
        return None

@app.get("/")
async def root():
    return {
        "message": "EXO-FIN GPT RealTime API Activa",
        "status": "OK",
        "version": app.version
    }

@app.get("/realtime")
async def get_live_price(symbol: str = Query(..., description="Símbolo bursátil, ej: AAPL, RIOT, TSLA")):
    symbol = symbol.upper()
    for source in [fetch_yahoo, fetch_twelve, fetch_alpha]:
        result = await source(symbol)
        if result and result["price"] > 0:
            return result
    return {"error": "No se pudo obtener el precio desde ninguna fuente"}

@app.get("/.well-known/openapi.json")
async def get_openapi_spec():
    return {
        "openapi": "3.1.0",
        "info": {
            "title": "EXO-FIN RealTime API",
            "version": "1.0.0",
            "description": "API de precios en tiempo real con fallback automático Yahoo → Twelve Data → Alpha Vantage."
        },
        "servers": [
            {"url": "https://web-production-48404.up.railway.app"}
        ],
        "paths": {
            "/realtime": {
                "get": {
                    "summary": "Obtener precio en tiempo real de una acción",
                    "operationId": "getLivePrice",
                    "parameters": [
                        {
                            "name": "symbol",
                            "in": "query",
                            "required": True,
                            "description": "Símbolo bursátil (ej: AAPL, TSLA, RIOT)",
                            "schema": {"type": "string"}
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Precio actual obtenido",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "symbol": {"type": "string"},
                                            "price": {"type": "number"},
                                            "currency": {"type": "string"},
                                            "timestamp": {"type": "string"},
                                            "source": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
