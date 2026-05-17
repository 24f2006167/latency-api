# api/index.py
import json
import os
import statistics
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

app = FastAPI()

# ✅ Enable CORS for POST requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # any website can call this
    allow_methods=["*"],       # allow GET, POST, etc.
    allow_headers=["*"],
)

# 📦 Load the telemetry data once when the function starts
# DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "q-vercel-latency.json")
DATA_FILE = os.path.join(os.path.dirname(__file__), "q-vercel-latency.json")

with open(DATA_FILE) as f:
    RAW_DATA = json.load(f)

# 📋 Define what the incoming request must look like
class AnalyticsRequest(BaseModel):
    regions: List[str]
    threshold_ms: float

# 🔢 Helper: calculate p95 (95th percentile)
def p95(values: list) -> float:
    if not values:
        return 0.0
    sorted_vals = sorted(values)
    # Find the index 95% of the way through the list
    index = int(len(sorted_vals) * 0.95)
    # Clamp so we don't go out of bounds
    index = min(index, len(sorted_vals) - 1)
    return round(sorted_vals[index], 3)

# 🚀 The POST endpoint
@app.post("/analytics")
def analytics(req: AnalyticsRequest):
    result = {}

    for region in req.regions:
        # Filter records that belong to this region
        region_records = [
            r for r in RAW_DATA
            if r.get("region", "").lower() == region.lower()
        ]

        if not region_records:
            result[region] = {
                "avg_latency": None,
                "p95_latency": None,
                "avg_uptime": None,
                "breaches": 0
            }
            continue

        latencies = [r["latency_ms"] for r in region_records]
        uptimes   = [r["uptime"] for r in region_records]

        result[region] = {
            "avg_latency": round(statistics.mean(latencies), 3),
            "p95_latency": p95(latencies),
            "avg_uptime":  round(statistics.mean(uptimes), 5),
            "breaches":    sum(1 for l in latencies if l > req.threshold_ms)
        }

    return result