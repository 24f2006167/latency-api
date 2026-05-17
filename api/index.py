from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import numpy as np

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request schema
class RequestData(BaseModel):
    regions: list
    threshold_ms: int

# Load JSON file
with open("q-vercel-latency.json", "r") as f:
    telemetry = json.load(f)

# ROOT TEST ROUTE
@app.get("/")
def home():
    return {"message": "API is working"}

# MAIN POST ENDPOINT
@app.post("/api")
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