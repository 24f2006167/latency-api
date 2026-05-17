# api/index.py
import statistics
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel
from typing import List

app = FastAPI()

@app.middleware("http")
async def add_cors(request: Request, call_next):
    if request.method == "OPTIONS":
        return Response(status_code=200, headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        })
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response

RAW_DATA = [
  {"region":"apac","latency_ms":152.05,"uptime_pct":97.586},
  {"region":"apac","latency_ms":211.94,"uptime_pct":99.088},
  {"region":"apac","latency_ms":159.64,"uptime_pct":98.842},
  {"region":"apac","latency_ms":219.4,"uptime_pct":98.138},
  {"region":"apac","latency_ms":159.75,"uptime_pct":97.785},
  {"region":"apac","latency_ms":107.02,"uptime_pct":98.116},
  {"region":"apac","latency_ms":115.96,"uptime_pct":99.373},
  {"region":"apac","latency_ms":168.33,"uptime_pct":99.26},
  {"region":"apac","latency_ms":101.03,"uptime_pct":99.063},
  {"region":"apac","latency_ms":141.11,"uptime_pct":97.329},
  {"region":"apac","latency_ms":110.23,"uptime_pct":99.426},
  {"region":"apac","latency_ms":197.51,"uptime_pct":97.766},
  {"region":"emea","latency_ms":198.45,"uptime_pct":99.05},
  {"region":"emea","latency_ms":199.21,"uptime_pct":98.694},
  {"region":"emea","latency_ms":218.19,"uptime_pct":99.194},
  {"region":"emea","latency_ms":226.08,"uptime_pct":97.19},
  {"region":"emea","latency_ms":202.1,"uptime_pct":98.877},
  {"region":"emea","latency_ms":141.17,"uptime_pct":98.407},
  {"region":"emea","latency_ms":158.04,"uptime_pct":99.038},
  {"region":"emea","latency_ms":213.45,"uptime_pct":98.242},
  {"region":"emea","latency_ms":208.01,"uptime_pct":97.471},
  {"region":"emea","latency_ms":202.99,"uptime_pct":98.946},
  {"region":"emea","latency_ms":202.49,"uptime_pct":99.012},
  {"region":"emea","latency_ms":128.47,"uptime_pct":98.396},
  {"region":"amer","latency_ms":147.11,"uptime_pct":98.474},
  {"region":"amer","latency_ms":191.03,"uptime_pct":97.652},
  {"region":"amer","latency_ms":155.4,"uptime_pct":99.452},
  {"region":"amer","latency_ms":190.6,"uptime_pct":97.994},
  {"region":"amer","latency_ms":155.39,"uptime_pct":98.065},
  {"region":"amer","latency_ms":148.54,"uptime_pct":98.141},
  {"region":"amer","latency_ms":152.9,"uptime_pct":99.186},
  {"region":"amer","latency_ms":197.35,"uptime_pct":98.281},
  {"region":"amer","latency_ms":114.9,"uptime_pct":97.354},
  {"region":"amer","latency_ms":185.64,"uptime_pct":98.112},
  {"region":"amer","latency_ms":206.08,"uptime_pct":97.62},
  {"region":"amer","latency_ms":188.12,"uptime_pct":97.344},
]

class AnalyticsRequest(BaseModel):
    regions: List[str]
    threshold_ms: float

def p95(values: list) -> float:
    if not values:
        return 0.0
    sorted_vals = sorted(values)
    index = min(int(len(sorted_vals) * 0.95), len(sorted_vals) - 1)
    return round(sorted_vals[index], 3)

@app.post("/analytics")
async def analytics(req: AnalyticsRequest):
    result = {}
    for region in req.regions:
        records = [r for r in RAW_DATA if r["region"].lower() == region.lower()]
        if not records:
            result[region] = {"avg_latency": None, "p95_latency": None, "avg_uptime": None, "breaches": 0}
            continue
        latencies = [r["latency_ms"] for r in records]
        uptimes   = [r["uptime_pct"] / 100 for r in records]
        result[region] = {
            "avg_latency": round(statistics.mean(latencies), 3),
            "p95_latency": p95(latencies),
            "avg_uptime":  round(statistics.mean(uptimes), 5),
            "breaches":    sum(1 for l in latencies if l > req.threshold_ms),
        }
    return result