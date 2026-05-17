from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import numpy as np

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

# Request body structure
class RequestData(BaseModel):
    regions: list
    threshold_ms: int

# Load telemetry data
with open("q-vercel-latency.json", "r") as f:
    telemetry = json.load(f)

@app.post("/")
def analyze_latency(data: RequestData):

    results = []

    for region in data.regions:

        region_records = [
            x for x in telemetry
            if x["region"] == region
        ]

        if not region_records:
            continue

        latencies = [x["latency_ms"] for x in region_records]
        uptimes = [x["uptime"] for x in region_records]

        avg_latency = sum(latencies) / len(latencies)

        p95_latency = float(np.percentile(latencies, 95))

        avg_uptime = sum(uptimes) / len(uptimes)

        breaches = len([
            x for x in latencies
            if x > data.threshold_ms
        ])

        results.append({
            "region": region,
            "avg_latency": round(avg_latency, 2),
            "p95_latency": round(p95_latency, 2),
            "avg_uptime": round(avg_uptime, 4),
            "breaches": breaches
        })

    return results