"""
AI-Powered Workforce Management Automation System
Production Load Testing & Performance Benchmark Script
--------------------------------------------------
Executes concurrent simulated workloads against FastAPI ASGI backend
without requiring external network servers. Measures throughput (RPS),
latency percentiles (P50, P95, P99), error rates, and system resources.
Saves empirical report to reports/load_test_report.json.
"""

import os
import sys
import time
import json
import statistics
import concurrent.futures
from datetime import datetime, timezone

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)

from fastapi.testclient import TestClient
from backend.main import app

def run_benchmark(concurrency: int = 10, total_requests: int = 200) -> dict:
    """
    Executes a multi-threaded synthetic load test against critical production endpoints.
    """
    client = TestClient(app)
    
    # 1. Authenticate to acquire Bearer tokens
    login_res = client.post("/api/v1/auth/login", json={"email": "admin@demo.com", "password": "Demo@2026"})
    admin_token = login_res.json().get("access_token") if login_res.status_code == 200 else ""
    headers = {"Authorization": f"Bearer {admin_token}", "X-Test-Rate-Limit": "bypass"} if admin_token else {}

    test_endpoints = [
        ("GET", "/api/v1/health/live", None, {}),
        ("GET", "/api/v1/health/ready", None, {}),
        ("GET", "/api/v1/employees?limit=10", None, headers),
        ("GET", "/api/v1/notifications?limit=5", None, headers),
        ("GET", "/api/v1/ai/attrition/EMP001", None, headers),
        ("GET", "/api/v1/metrics?format=json", None, {})
    ]


    print(f"[*] Starting Load Test Benchmark: {total_requests} requests across {concurrency} worker threads...")
    
    latencies = []
    status_counts = {}
    errors = 0

    def send_request(idx: int):
        method, url, payload, hdrs = test_endpoints[idx % len(test_endpoints)]
        req_start = time.perf_counter()
        try:
            if method == "GET":
                resp = client.get(url, headers=hdrs)
            else:
                resp = client.post(url, json=payload, headers=hdrs)
            duration_ms = (time.perf_counter() - req_start) * 1000
            return resp.status_code, duration_ms, None
        except Exception as e:
            duration_ms = (time.perf_counter() - req_start) * 1000
            return 500, duration_ms, str(e)

    bench_start = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [executor.submit(send_request, i) for i in range(total_requests)]
        for f in concurrent.futures.as_completed(futures):
            code, dur, err = f.result()
            latencies.append(dur)
            status_counts[code] = status_counts.get(code, 0) + 1
            if code >= 400 or err:
                errors += 1

    total_time_seconds = time.perf_counter() - bench_start
    rps = round(total_requests / max(0.001, total_time_seconds), 2)
    latencies.sort()

    p50 = round(statistics.median(latencies), 2)
    p95 = round(latencies[int(len(latencies) * 0.95)], 2)
    p99 = round(latencies[int(len(latencies) * 0.99)], 2)
    avg_latency = round(statistics.mean(latencies), 2)

    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "concurrency": concurrency,
        "total_requests": total_requests,
        "total_duration_seconds": round(total_time_seconds, 2),
        "requests_per_second": rps,
        "successful_requests": total_requests - errors,
        "failed_requests": errors,
        "error_rate_percent": round((errors / total_requests) * 100, 2),
        "latency_ms": {
            "avg": avg_latency,
            "min": round(min(latencies), 2),
            "max": round(max(latencies), 2),
            "p50": p50,
            "p95": p95,
            "p99": p99
        },
        "status_distribution": status_counts
    }

    os.makedirs(os.path.join(ROOT_DIR, "reports"), exist_ok=True)
    report_file = os.path.join(ROOT_DIR, "reports", "load_test_report.json")
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print("\n============================================================")
    print("LOAD TEST BENCHMARK RESULTS")
    print("============================================================")
    print(f"Total Requests:       {total_requests}")
    print(f"Concurrency:          {concurrency} workers")
    print(f"Total Time:           {report['total_duration_seconds']}s")
    print(f"Throughput:           {rps} requests/second")
    print(f"Success Rate:         {100 - report['error_rate_percent']}%")
    print(f"Average Latency:      {avg_latency}ms")
    print(f"P50 Latency:          {p50}ms")
    print(f"P95 Latency:          {p95}ms")
    print(f"P99 Latency:          {p99}ms")
    print(f"Report exported to:   {report_file}")
    print("============================================================\n")

    return report

if __name__ == "__main__":
    run_benchmark(concurrency=8, total_requests=150)
