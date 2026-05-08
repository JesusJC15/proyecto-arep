from __future__ import annotations

from collections import Counter, defaultdict
from threading import Lock


class MetricsCollector:
    def __init__(self) -> None:
        self._lock = Lock()
        self.request_total = Counter()
        self.request_duration_ms = defaultdict(float)

    def record_request(self, method: str, path: str, status_code: int, duration_ms: float) -> None:
        key = (method, path, status_code)
        with self._lock:
            self.request_total[key] += 1
            self.request_duration_ms[(method, path)] += duration_ms

    def render_prometheus(self) -> str:
        lines = [
            "# HELP arep_http_requests_total Total HTTP requests by method, path and status",
            "# TYPE arep_http_requests_total counter",
        ]
        for (method, path, status_code), count in sorted(self.request_total.items()):
            lines.append(
                'arep_http_requests_total{method="%s",path="%s",status="%s"} %s'
                % (method, path, status_code, count)
            )
        lines.extend(
            [
                "# HELP arep_http_request_duration_ms_sum Aggregate request duration in milliseconds",
                "# TYPE arep_http_request_duration_ms_sum counter",
            ]
        )
        for (method, path), total_duration in sorted(self.request_duration_ms.items()):
            lines.append(
                'arep_http_request_duration_ms_sum{method="%s",path="%s"} %.3f'
                % (method, path, total_duration)
            )
        return "\n".join(lines) + "\n"
