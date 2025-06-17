# 📈 Realtime Stock Price API – EXO-FIN GPT

API de precios en tiempo real para integración con el sistema EXO-FIN GPT. Diseñada para obtener cotizaciones bursátiles actualizadas desde múltiples fuentes y asegurar decisiones de inversión basadas en datos actuales.

---

## 🚀 Endpoint principal

```
GET /realtime?symbol=APLD
```

### 📥 Parámetros

- `symbol` → Ticker bursátil (ej. AAPL, TSLA, APLD)
- `source` (opcional) → Fuente: `yahoo` (default), `alpha`, `twelve`

### 📤 Respuesta JSON

```json
{
  "symbol": "APLD",
  "price": 11.55,
  "currency": "USD",
  "timestamp": "2025-06-17",
  "source": "Twelve Data"
}
```

---

## 🔌 Fuentes compatibles

| Fuente          | Acceso                                | API Key                  | Estado     |
|------------------|----------------------------------------|---------------------------|-------------|
| Yahoo Finance   | Automático (source=yahoo o default)    | ❌ No necesita            | ✅ Listo    |
| Alpha Vantage   | Manual (source=alpha)                  | ✅ UGLDAKBR7W6AO6UW       | ✅ Listo    |
| Twelve Data     | Manual (source=twelve)                 | ✅ 573f14c758bb40ec8916d6719c7a805b | ✅ Listo    |

---

## 📁 Estructura del proyecto

```
main.py             # Código principal FastAPI
requirements.txt    # Dependencias (FastAPI, httpx, uvicorn)
Procfile            # Instrucción de despliegue para Railway
README.md           # Documentación del proyecto
```

---

## 🧠 Extensión futura sugerida

- Fallback automático entre fuentes en caso de error
- Cache de cotizaciones por 30s para eficiencia
- Selección inteligente de fuente según símbolo/región

---

## ⚙️ Deploy recomendado

✔️ Railway + GitHub (auto-deploy)  
✔️ Compatible con Vercel / Fly.io / Render  
