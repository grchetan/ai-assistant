"""
================================================================================
                    JARVIS REST & HTTP API TEST RUNNER
================================================================================
Developer utility to dispatch HTTP requests (GET, POST, PUT, DELETE), measure
endpoint latency, validate JSON responses, and inspect response headers.
================================================================================
"""

import time
import json
import urllib.request
import urllib.error
from typing import Dict, Any, Tuple, Optional

from jarvis.core.logger import get_logger


class APITester:
    """Dispatches HTTP probes and records latency metrics."""

    def __init__(self) -> None:
        self.logger = get_logger()

    def send_request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        timeout: int = 10
    ) -> Tuple[bool, int, float, str]:
        """
        Execute an HTTP request.
        Returns: (success, status_code, elapsed_ms, response_body)
        """
        req_headers = headers or {}
        if "User-Agent" not in req_headers:
            req_headers["User-Agent"] = "JARVIS-APITester/4.0"

        data_bytes = None
        if json_data:
            data_bytes = json.dumps(json_data).encode("utf-8")
            req_headers["Content-Type"] = "application/json"

        self.logger.info(f"Dispatching HTTP {method.upper()} -> {url}", "API")
        t0 = time.perf_counter()

        try:
            req = urllib.request.Request(url, data=data_bytes, headers=req_headers, method=method.upper())
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                elapsed_ms = (time.perf_counter() - t0) * 1000.0
                status_code = resp.status
                body = resp.read().decode("utf-8", errors="replace")

                self.logger.success(f"HTTP {status_code} [{elapsed_ms:.1f}ms]", "API")
                return True, status_code, round(elapsed_ms, 1), body

        except urllib.error.HTTPError as e:
            elapsed_ms = (time.perf_counter() - t0) * 1000.0
            body = e.read().decode("utf-8", errors="replace") if e.fp else str(e)
            self.logger.warning(f"HTTP Error {e.code} [{elapsed_ms:.1f}ms]", "API")
            return False, e.code, round(elapsed_ms, 1), body

        except Exception as e:
            elapsed_ms = (time.perf_counter() - t0) * 1000.0
            self.logger.error(f"HTTP Request failed: {e}", "API")
            return False, 0, round(elapsed_ms, 1), str(e)


def get_api_tester() -> APITester:
    return APITester()
