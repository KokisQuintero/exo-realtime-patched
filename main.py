from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import httpx

app = FastAPI(title="EXO-FIN GPT API v2", version="2.1.0")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

ALPHA_VANTAGE_API_KEY = "UGLDAKBR7W6AO6UW"
TWELVE_DATA_API_KEY = "573f14c758bb40ec8916d6719c7a805b"

def format_symbol(symbol):
    if symbol.endswith(".AX") or symbol.startswith("ASX:"):
        return symbol
    if symbol.isupper() and len(symbol) <= 4:
        return symbol + ".AX"
    return symbol

async def fetch_yahoo(symbol):
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            r = await client.get(f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={symbol}")
        j = r.json().get("quoteResponse", {}).get("result", [])
        if j:
            q = j[0]
            return {"symbol": q["symbol"], "price": q.get("regularMarketPrice", 0), "currency": q.get("currency", "AUD"), "source": "Yahoo Finance"}
    except:
        pass
    return None

async def fetch_twelve(symbol):
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            r = await client.get(f"https://api.twelvedata.com/price?symbol={symbol}&apikey={TWELVE_DATA_API_KEY}")
        d = r.json()
        if "price" in d:
            return {"symbol": symbol, "price": float(d["price"]), "currency": "AUD", "source": "Twelve Data"}
    except:
        pass
    return None

async def fetch_alpha(symbol):
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            r = await client.get(f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={ALPHA_VANTAGE_API_KEY}")
        d = r.json().get("Global Quote", {})
        if "05. price" in d:
            return {"symbol": symbol, "price": float(d["05. price"]), "currency": "AUD", "source": "Alpha Vantage"}
    except:
        pass
    return None

async def get_price(symbol):
    formatted_symbol = format_symbol(symbol)
    for fn in (fetch_yahoo, fetch_twelve, fetch_alpha):
        res = await fn(formatted_symbol)
        if res and res["price"] > 0:
            return res
    return {"error": f"No se pudo obtener precio para {symbol} (verificá símbolo ASX o fuente)."}

@app.get("/")
async def root():
    return {"message": "EXO-FIN GPT API ASX Mejorada Activa"}

@app.get("/realtime")
async def realtime(symbol: str = Query(..., description="Ticker (ej: APLD, ZIP, CMM)")):
    return await get_price(symbol.upper())

@app.post("/dailycheck")
async def daily_check(data: dict):
    out = []
    for pos in data.get("positions", []):
        s = pos.get("symbol", "").upper()
        info = await get_price(s)
        if "error" in info:
            out.append({"symbol": s, "error": info["error"]})
            continue
        cp = info["price"]
        bp = pos.get("price", 0)
        pl = round((cp - bp) / bp * 100, 2) if bp else None
        out.append({
            "symbol": s,
            "quantity": pos.get("quantity"),
            "buy_price": bp,
            "current_price": cp,
            "currency": info["currency"],
            "source": info["source"],
            "TP": round(bp * 1.5, 2),
            "SL": round(bp * 0.8, 2),
            "PL_percent": pl,
            "decision": "VENDER" if pl and pl >= 50 else ("REFORZAR" if pl and pl <= -20 else "MANTENER")
        })
    return out
