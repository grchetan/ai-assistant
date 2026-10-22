"""
================================================================================
                    JARVIS NETWORK PACKET & TRAFFIC ANALYZER
================================================================================
Monitors network interface statistics, tracks per-process bandwidth consumption,
detects sudden traffic surges, and visualizes network protocol distributions.
================================================================================
"""

import time
import socket
import threading
from typing import Dict, Any, List, Optional, Tuple

try:
    import psutil
    _PSUTIL_AVAILABLE = True
except ImportError:
    _PSUTIL_AVAILABLE = False

from jarvis.core.logger import get_logger


class NetworkPacketAnalyzer:
    """Measures socket throughput and process bandwidth allocations."""

    def __init__(self) -> None:
        self.logger = get_logger()
        self._last_snapshot_time = time.time()
        self._last_bytes_sent = 0
        self._last_bytes_recv = 0
        self._init_baselines()

    def _init_baselines(self) -> None:
        if _PSUTIL_AVAILABLE:
            try:
                io = psutil.net_io_counters()
                self._last_bytes_sent = io.bytes_sent
                self._last_bytes_recv = io.bytes_recv
            except Exception:
                pass

    def get_instantaneous_throughput(self) -> Dict[str, float]:
        """
        Calculate current upload and download throughput in KB/sec.
        """
        if not _PSUTIL_AVAILABLE:
            return {"download_kbps": 0.0, "upload_kbps": 0.0}

        try:
            now = time.time()
            dt = max(now - self._last_snapshot_time, 0.05)
            io = psutil.net_io_counters()

            sent_delta = io.bytes_sent - self._last_bytes_sent
            recv_delta = io.bytes_recv - self._last_bytes_recv

            upload_kbps = round((sent_delta / 1024.0) / dt, 1)
            download_kbps = round((recv_delta / 1024.0) / dt, 1)

            self._last_snapshot_time = now
            self._last_bytes_sent = io.bytes_sent
            self._last_bytes_recv = io.bytes_recv

            return {
                "download_kbps": max(0.0, download_kbps),
                "upload_kbps": max(0.0, upload_kbps)
            }
        except Exception:
            return {"download_kbps": 0.0, "upload_kbps": 0.0}

    def get_top_network_processes(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        List running processes with the most active network connections.
        """
        if not _PSUTIL_AVAILABLE:
            return []

        counts: Dict[str, int] = {}
        for conn in psutil.net_connections(kind='inet'):
            if conn.pid:
                try:
                    p = psutil.Process(conn.pid)
                    name = p.name()
                    counts[name] = counts.get(name, 0) + 1
                except Exception:
                    continue

        sorted_procs = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:limit]
        return [{"process": k, "active_sockets": v} for k, v in sorted_procs]

    def get_traffic_summary_speech(self) -> str:
        speed = self.get_instantaneous_throughput()
        top = self.get_top_network_processes(limit=3)

        top_names = ", ".join([f"{p['process']} ({p['active_sockets']} sockets)" for p in top]) if top else "None"
        return (
            f"Sir, network speed: Download {speed['download_kbps']} KB/s, "
            f"Upload {speed['upload_kbps']} KB/s. Top active processes: {top_names}."
        )


def get_packet_analyzer() -> NetworkPacketAnalyzer:
    return NetworkPacketAnalyzer()
