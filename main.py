from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import httpx

app = FastAPI(title="EXO-FIN GPT API v2.2", version="2.2.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

ALPHA_VANTAGE_API_KEY = "UGLDAKBR7W6AO6UW"
TWELVE_DATA_API_KEY = "573f14c758bb40ec8916d6719c7a805b"

def list_symbol_variants(symbol):
    s = symbol.upper()
    variants = [s]
    if not s.endswith(".AX"):
        variants.append(s + ".AX")
        variants.append("ASX:" + s)
    return variants

async def fetch_source(func, symbol):
    try:
        return await func(symbol)
    except:
        return None

async def fetch_yahoo(symbol):
    async with httpx.AsyncClient(timeout=5) as client:
        r = await client.get(f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={symbol}")
    j = r.json().get("quoteResponse", {}).get("result", [])
    if j and "regularMarketPrice" in j[0]:
        q = j[0]
        curr = q.get("currency", "USD")
        return {"symbol": q["symbol"], "price": q["regularMarketPrice"], "currency": curr, "source": "Yahoo Finance"}
    return None

async def fetch_twelve(symbol):
    async with httpx.AsyncClient(timeout=5) as client:
        r = await client.get(f"https://api.twelvedata.com/price?symbol={symbol}&apikey={TWELVE_DATA_API_KEY}")
    d = r.json()
    if "price" in d:
        return {"symbol": symbol, "price": float(d["price"]), "currency": "USD", "source": "Twelve Data"}
    return None

async def fetch_alpha(symbol):
    async with httpx.AsyncClient(timeout=5) as client:
        r = await client.get(f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={ALPHA_VANTAGE_API_KEY}")
    d = r.json().get("Global Quote", {})
    if "05. price" in d:
        return {"symbol": symbol, "price": float(d["05. price"]), "currency": "USD", "source": "Alpha Vantage"}
    return None

async def get_price(symbol):
    for variant in list_symbol_variants(symbol):
        for src in (fetch_yahoo, fetch_twelve, fetch_alpha):
            res = await fetch_source(src, variant)
            if res and res["price"] and res["price"] > 0:
                return res
    return {"error": f"No se pudo obtener precio para {symbol} (revisá símbolo ASX o fuente)"}

@app.get("/")
async def root():
    return {"message": "EXO-FIN GPT API ASX + variaciones activada"}

@app.get("/realtime")
async def realtime(symbol: str = Query(..., description="Ticker, e.g. ZIP")):
    return await get_price(symbol)

@app.post("/dailycheck")
async def daily_check(data: dict):
    res = []
    for pos in data.get("positions", []):
        s = pos.get("symbol", "")
        info = await get_price(s)
        if "error" in info:
            res.append({"symbol": s.upper(), "error": info["error"]})
            continue
        cp = info["price"]
        bp = pos.get("price", 0)
        pl = round((cp - bp)/bp*100, 2) if bp else None
        res.append({
            "symbol": s.upper(), "quantity": pos.get("quantity"),
            "buy_price": bp, "current_price": cp,
            "currency": info["currency"], "source": info["source"],
            "TP": round(bp*1.5,2), "SL": round(bp*0.8,2),
            "PL_percent": pl,
            "decision": "VENDER" if pl and pl>=50 else ("REFORZAR" if pl and pl<=-20 else "MANTENER")
        })
    return res
