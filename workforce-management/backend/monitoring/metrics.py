"""
AI-Powered Workforce Management Automation System
Application Performance & Reliability Metrics
--------------------------------------------------
Provides thread-safe metrics collection for:
- Request counts by category & status
- Latency percentiles & averages
- Authentication success vs. failures
- Attendance & Leave business events
- AI inference durations (attrition, absenteeism, forecasting)
- Chatbot query latencies
- Database & Integration error counts
Emits both structured JSON and standard Prometheus exposition formats.
"""

import time
from typing import Dict, Any
from threading import Lock
from collections import defaultdict
import psutil

class MetricsCollector:
    def __init__(self):
        self._lock = Lock()
        self._start_time = time.time()
        
        # Counters
        self._http_requests_total: Dict[str, int] = defaultdict(int)
        self._http_errors_total: Dict[str, int] = defaultdict(int)
        self._auth_success_total: int = 0
        self._auth_failure_total: int = 0
        self._attendance_punches_total: int = 0
        self._leave_applications_total: int = 0
        self._ai_inferences_total: int = 0
        self._chatbot_queries_total: int = 0
        self._workflow_executions_total: int = 0
        self._workflow_failures_total: int = 0
        self._database_errors_total: int = 0
        self._integration_errors_total: int = 0

        # Duration samples (last 100 for calculating rolling averages)
        self._request_durations_ms: list[float] = []
        self._ai_durations_ms: list[float] = []
        self._chatbot_durations_ms: list[float] = []

    def record_request(self, method: str, path: str, status_code: int, duration_ms: float):
        with self._lock:
            # Group paths to prevent high cardinality (e.g. /employees/EMP001 -> /employees/{id})
            normalized_path = self._normalize_path(path)
            key = f"{method}_{normalized_path}_{status_code}"
            self._http_requests_total[key] += 1
            if status_code >= 400:
                self._http_errors_total[f"{status_code}"] += 1

            self._request_durations_ms.append(duration_ms)
            if len(self._request_durations_ms) > 200:
                self._request_durations_ms.pop(0)

    def record_auth_success(self):
        with self._lock:
            self._auth_success_total += 1

    def record_auth_failure(self):
        with self._lock:
            self._auth_failure_total += 1

    def record_attendance_punch(self):
        with self._lock:
            self._attendance_punches_total += 1

    def record_leave_application(self):
        with self._lock:
            self._leave_applications_total += 1

    def record_ai_inference(self, duration_ms: float):
        with self._lock:
            self._ai_inferences_total += 1
            self._ai_durations_ms.append(duration_ms)
            if len(self._ai_durations_ms) > 100:
                self._ai_durations_ms.pop(0)

    def record_chatbot_query(self, duration_ms: float):
        with self._lock:
            self._chatbot_queries_total += 1
            self._chatbot_durations_ms.append(duration_ms)
            if len(self._chatbot_durations_ms) > 100:
                self._chatbot_durations_ms.pop(0)

    def record_workflow_execution(self, success: bool = True):
        with self._lock:
            self._workflow_executions_total += 1
            if not success:
                self._workflow_failures_total += 1

    def record_database_error(self):
        with self._lock:
            self._database_errors_total += 1

    def record_integration_error(self):
        with self._lock:
            self._integration_errors_total += 1

    def _normalize_path(self, path: str) -> str:
        parts = path.strip("/").split("/")
        normalized = []
        for p in parts:
            if p.startswith("EMP") or p.startswith("PRJ") or (len(p) > 10 and any(c.isdigit() for c in p)):
                normalized.append("{id}")
            else:
                normalized.append(p)
        return "/" + "/".join(normalized)

    def get_summary(self) -> Dict[str, Any]:
        """Returns JSON-formatted metrics snapshot."""
        with self._lock:
            uptime_seconds = int(time.time() - self._start_time)
            avg_latency = round(sum(self._request_durations_ms) / max(1, len(self._request_durations_ms)), 2)
            avg_ai_latency = round(sum(self._ai_durations_ms) / max(1, len(self._ai_durations_ms)), 2)
            avg_chatbot_latency = round(sum(self._chatbot_durations_ms) / max(1, len(self._chatbot_durations_ms)), 2)
            
            # System resource metrics
            try:
                process = psutil.Process()
                mem_info = process.memory_info()
                cpu_percent = process.cpu_percent(interval=None)
                memory_rss_mb = round(mem_info.rss / (1024 * 1024), 2)
            except Exception:
                memory_rss_mb = 0.0
                cpu_percent = 0.0

            total_requests = sum(self._http_requests_total.values())
            total_errors = sum(self._http_errors_total.values())
            error_rate = round((total_errors / max(1, total_requests)) * 100, 2)

            return {
                "uptime_seconds": uptime_seconds,
                "process": {
                    "cpu_percent": cpu_percent,
                    "memory_rss_mb": memory_rss_mb
                },
                "http": {
                    "total_requests": total_requests,
                    "total_errors": total_errors,
                    "error_rate_percent": error_rate,
                    "avg_latency_ms": avg_latency
                },
                "auth": {
                    "success": self._auth_success_total,
                    "failures": self._auth_failure_total
                },
                "business_events": {
                    "attendance_punches": self._attendance_punches_total,
                    "leave_applications": self._leave_applications_total
                },
                "ai_workforce": {
                    "total_inferences": self._ai_inferences_total,
                    "avg_inference_latency_ms": avg_ai_latency,
                    "chatbot_queries": self._chatbot_queries_total,
                    "avg_chatbot_latency_ms": avg_chatbot_latency
                },
                "workflows": {
                    "total_executions": self._workflow_executions_total,
                    "failures": self._workflow_failures_total
                },
                "errors": {
                    "database_errors": self._database_errors_total,
                    "integration_errors": self._integration_errors_total
                }
            }

    def to_prometheus(self) -> str:
        """Renders metrics in Prometheus standard exposition text format."""
        summary = self.get_summary()
        lines = [
            "# HELP hr_app_uptime_seconds Application uptime in seconds",
            "# TYPE hr_app_uptime_seconds gauge",
            f"hr_app_uptime_seconds {summary['uptime_seconds']}",
            "# HELP hr_app_memory_rss_mb Process resident memory in MB",
            "# TYPE hr_app_memory_rss_mb gauge",
            f"hr_app_memory_rss_mb {summary['process']['memory_rss_mb']}",
            "# HELP hr_http_requests_total Total HTTP requests",
            "# TYPE hr_http_requests_total counter",
            f"hr_http_requests_total {summary['http']['total_requests']}",
            "# HELP hr_http_errors_total Total HTTP error responses",
            "# TYPE hr_http_errors_total counter",
            f"hr_http_errors_total {summary['http']['total_errors']}",
            "# HELP hr_http_latency_ms Average HTTP latency in milliseconds",
            "# TYPE hr_http_latency_ms gauge",
            f"hr_http_latency_ms {summary['http']['avg_latency_ms']}",
            "# HELP hr_auth_failures_total Total failed authentication attempts",
            "# TYPE hr_auth_failures_total counter",
            f"hr_auth_failures_total {summary['auth']['failures']}",
            "# HELP hr_ai_inferences_total Total AI inferences completed",
            "# TYPE hr_ai_inferences_total counter",
            f"hr_ai_inferences_total {summary['ai_workforce']['total_inferences']}",
            "# HELP hr_database_errors_total Total database errors encountered",
            "# TYPE hr_database_errors_total counter",
            f"hr_database_errors_total {summary['errors']['database_errors']}"
        ]
        return "\n".join(lines) + "\n"

# Global singleton
metrics = MetricsCollector()
