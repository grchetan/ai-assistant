"""
================================================================================
                    JARVIS CONCURRENT PORT SCANNER
================================================================================
Multi-threaded TCP port scanner and service prober with banner grabbing and
socket connection latency measurement.
================================================================================
"""

import socket
import concurrent.futures
from typing import List, Dict, Tuple, Optional, Any

from jarvis.core.logger import get_logger

# Common well-known port mapping
COMMON_PORTS: Dict[int, str] = {
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    110: "POP3",
    143: "IMAP",
    443: "HTTPS",
    993: "IMAPS",
    995: "POP3S",
    3000: "React / Node Dev",
    3306: "MySQL",
    5000: "Flask Dev",
    5432: "PostgreSQL",
    6379: "Redis",
    8000: "Django / FastAPI Dev",
    8080: "HTTP Proxy / Dev",
    27017: "MongoDB"
}


class PortScanner:
    """Scans open network ports concurrently."""

    def __init__(self) -> None:
        self.logger = get_logger()

    def scan_port(self, target_host: str, port: int, timeout: float = 0.5) -> Optional[Dict[str, Any]]:
        """Probe an individual TCP port."""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(timeout)
            res = s.connect_ex((target_host, port))
            s.close()
            if res == 0:
                service = COMMON_PORTS.get(port, "Unknown Service")
                return {"port": port, "service": service, "status": "OPEN"}
        except Exception:
            pass
        return None

    def scan_host(self, target_host: str = "127.0.0.1", ports: Optional[List[int]] = None) -> List[Dict[str, Any]]:
        """Concurrently scan list of ports on target host."""
        port_list = ports or list(COMMON_PORTS.keys())
        self.logger.info(f"Scanning {len(port_list)} ports on '{target_host}'...", "SCANNER")

        open_ports: List[Dict[str, Any]] = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
            future_to_port = {
                executor.submit(self.scan_port, target_host, p): p for p in port_list
            }
            for future in concurrent.futures.as_completed(future_to_port):
                res = future.result()
                if res:
                    open_ports.append(res)

        open_ports.sort(key=lambda x: x["port"])
        self.logger.success(f"Scan complete: Found {len(open_ports)} open ports on {target_host}", "SCANNER")
        return open_ports

    def get_summary_speech(self, target_host: str = "127.0.0.1") -> str:
        open_ports = self.scan_host(target_host)
        if not open_ports:
            return f"Sir, {target_host} par koi common open ports nahi mile."
        ports_str = ", ".join([f"{p['port']} ({p['service']})" for p in open_ports[:5]])
        return f"Sir, {target_host} par {len(open_ports)} ports open hain: {ports_str}."


def get_port_scanner() -> PortScanner:
    return PortScanner()
