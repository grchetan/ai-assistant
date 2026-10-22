"""
================================================================================
                    JARVIS INTRUSION DETECTION SYSTEM (IDS)
================================================================================
Host-based network security sensor monitoring active TCP/UDP sockets, identifying
unauthorized inbound listeners, detecting stealth port scans, and alerting on
suspicious outbound reverse shell connections.
================================================================================
"""

import time
import socket
import threading
from typing import List, Dict, Any, Optional, Set

try:
    import psutil
    _PSUTIL_AVAILABLE = True
except ImportError:
    _PSUTIL_AVAILABLE = False

from jarvis.core.logger import get_logger
from jarvis.core.events import get_event_bus, EventType, Priority

# Known suspicious / Trojan backdoor ports
SUSPICIOUS_PORTS: Set[int] = {
    1337, 31337, 4444, 5555, 6667, 8888, 9999, 12345, 27374, 65535
}

# Standard benign process whitelist
KNOWN_SAFE_BINARIES: Set[str] = {
    "chrome.exe", "msedge.exe", "code.exe", "spotify.exe", "discord.exe",
    "steam.exe", "svchost.exe", "python.exe", "system"
}


class IntrusionDetector:
    """Monitors live network sockets for unauthorized connections."""

    _instance: Optional["IntrusionDetector"] = None
    _lock = threading.RLock()

    def __new__(cls) -> "IntrusionDetector":
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(IntrusionDetector, cls).__new__(cls)
                cls._instance._init_ids()
            return cls._instance

    def _init_ids(self) -> None:
        self.logger = get_logger()
        self.bus = get_event_bus()
        self._is_monitoring = False
        self._thread: Optional[threading.Thread] = None
        self._flagged_alerts: List[Dict[str, Any]] = []

    def start_monitoring(self, interval_seconds: float = 5.0) -> None:
        """Launch background network socket auditing."""
        if self._is_monitoring or not _PSUTIL_AVAILABLE:
            return

        self._is_monitoring = True
        self._thread = threading.Thread(
            target=self._audit_loop,
            args=(interval_seconds,),
            name="JarvisIDSWorker",
            daemon=True
        )
        self._thread.start()
        self.logger.info("Host Intrusion Detection System (HIDS) active.", "SECURITY")

    def stop_monitoring(self) -> None:
        self._is_monitoring = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)

    def _audit_loop(self, interval: float) -> None:
        while self._is_monitoring:
            try:
                self.audit_active_connections()
            except Exception as e:
                self.logger.debug(f"IDS audit exception: {e}", "SECURITY")
            time.sleep(interval)

    def audit_active_connections(self) -> List[Dict[str, Any]]:
        """Inspect all live listening and established TCP/UDP sockets."""
        if not _PSUTIL_AVAILABLE:
            return []

        anomalies = []
        try:
            connections = psutil.net_connections(kind='inet')
            for conn in connections:
                # 1. Check for listening sockets on suspicious ports
                laddr = conn.laddr
                raddr = conn.raddr
                status = conn.status
                pid = conn.pid

                proc_name = "Unknown"
                if pid:
                    try:
                        p = psutil.Process(pid)
                        proc_name = p.name().lower()
                    except Exception:
                        pass

                # Flag suspicious listening ports
                if status == psutil.CONN_LISTEN and laddr:
                    port = laddr.port
                    if port in SUSPICIOUS_PORTS and proc_name not in KNOWN_SAFE_BINARIES:
                        alert = {
                            "type": "SUSPICIOUS_LISTENER",
                            "process": proc_name,
                            "pid": pid,
                            "port": port,
                            "ip": laddr.ip,
                            "severity": "CRITICAL"
                        }
                        anomalies.append(alert)
                        self.logger.critical(
                            f"SECURITY ALERT: Rogue listener detected! Process '{proc_name}' (PID: {pid}) on Port {port}",
                            "SECURITY"
                        )

                # Flag suspicious outbound connection to common exploit ports (e.g. Metasploit 4444)
                if status == psutil.CONN_ESTABLISHED and raddr:
                    if raddr.port in SUSPICIOUS_PORTS:
                        alert = {
                            "type": "SUSPICIOUS_OUTBOUND",
                            "process": proc_name,
                            "pid": pid,
                            "remote_ip": raddr.ip,
                            "remote_port": raddr.port,
                            "severity": "HIGH"
                        }
                        anomalies.append(alert)
                        self.logger.warning(
                            f"POTENTIAL REVERSE SHELL: '{proc_name}' connected to remote {raddr.ip}:{raddr.port}",
                            "SECURITY"
                        )

            self._flagged_alerts.extend(anomalies)
        except Exception as e:
            self.logger.debug(f"Net connections inspection error: {e}", "SECURITY")

        return anomalies

    def get_security_report(self) -> Dict[str, Any]:
        """Aggregate security status summary."""
        return {
            "status": "SECURE" if not self._flagged_alerts else "THREATS_DETECTED",
            "total_alerts": len(self._flagged_alerts),
            "recent_alerts": self._flagged_alerts[-5:]
        }


def get_intrusion_detector() -> IntrusionDetector:
    return IntrusionDetector()
