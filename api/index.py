from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from statistics import mean
import math

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["*"],
)

# Replace this with your real telemetry loading logic if the assignment gives you a file.
DATA = {
    "emea": [
        {"latency_ms": 120, "uptime": 0.99},
        {"latency_ms": 160, "uptime": 0.98},
        {"latency_ms": 150, "uptime": 1.00},
    ],
    "amer": [
        {"latency_ms": 140, "uptime": 0.97},
        {"latency_ms": 170, "uptime": 0.96},
        {"latency_ms": 180, "uptime": 0.98},
    ],
}

@app.post("/")
async def analytics(request: Request):
    body = await request.json()
    regions = body.get("regions", [])
    threshold_ms = body.get("threshold_ms", 0)

    result = {}
    for region in regions:
        records = DATA.get(region, [])
        if not records:
            result[region] = {
                "avg_latency": None,
                "p95_latency": None,
                "avg_uptime": None,
                "breaches": 0,
            }
            continue

        latencies = [r["latency_ms"] for r in records]
        uptimes = [r["uptime"] for r in records]
        sorted_lat = sorted(latencies)

        p95_index = math.ceil(0.95 * len(sorted_lat)) - 1
        p95_index = max(0, min(p95_index, len(sorted_lat) - 1))

        result[region] = {
            "avg_latency": mean(latencies),
            "p95_latency": sorted_lat[p95_index],
            "avg_uptime": mean(uptimes),
            "breaches": sum(1 for x in latencies if x > threshold_ms),
        }

    return result