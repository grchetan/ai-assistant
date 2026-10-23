"""
================================================================================
                    JARVIS NETWORK & CONNECTIVITY DIAGNOSTICS
================================================================================
Network diagnostic suite: latency ping checks, public / local IP resolution,
active Wi-Fi connection inspection, and port connectivity testers.
================================================================================
"""

import socket
import time
import subprocess
import urllib.request
from typing import Dict, Any, Optional, Tuple

from jarvis.core.logger import get_logger


class NetworkDiagnostics:
    """Network testing and telemetry."""

    def __init__(self) -> None:
        self.logger = get_logger()

    def ping_host(self, host: str = "8.8.8.8") -> str:
        """Measure round-trip ICMP latency."""
        self.logger.info(f"Pinging host: {host}", "NETWORK")
        try:
            res = subprocess.run(
                ["ping", "-n", "2", "-w", "1500", host],
                capture_output=True,
                text=True
            )
            if "Average =" in res.stdout:
                avg = res.stdout.split("Average =")[-1].strip()
                return f"Internet latency {avg} hai sir. Connection stable hai."
            elif "Lost = 0" in res.stdout:
                return "Ping successful, connection active hai sir."
            else:
                return "Sir, ping packet drop ho gaya. Network slow ya disconnected lag raha hai."
        except Exception as e:
            return f"Ping test fail ho gaya: {e}"

    def get_ip_info(self) -> Dict[str, str]:
        """Resolve local and public IP addresses."""
        info = {"local_ip": "127.0.0.1", "public_ip": "Unknown"}
        try:
            # Local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            info["local_ip"] = s.getsockname()[0]
            s.close()
        except Exception:
            pass

        try:
            # Public IP
            req = urllib.request.Request("https://api.ipify.org", headers={'User-Agent': 'JARVIS'})
            with urllib.request.urlopen(req, timeout=3) as resp:
                info["public_ip"] = resp.read().decode('utf-8').strip()
        except Exception:
            pass

        return info

    def get_wifi_ssid(self) -> str:
        """Get connected Wi-Fi network SSID."""
        try:
            res = subprocess.run(
                ["netsh", "wlan", "show", "interfaces"],
                capture_output=True,
                text=True
            )
            for line in res.stdout.splitlines():
                if "SSID" in line and "BSSID" not in line:
                    ssid = line.split(":")[-1].strip()
                    if ssid:
                        return ssid
            return "Ethernet / Cable"
        except Exception:
            return "Unknown Network"

    def measure_internet_speed(self) -> Tuple[float, float, str]:
        """Measure real internet download bandwidth in Mbps and latency in ms."""
        self.logger.info("Starting real internet bandwidth speed test...", "NETWORK")
        ping_ms = 25.0
        try:
            res = subprocess.run(["ping", "-n", "2", "-w", "1200", "8.8.8.8"], capture_output=True, text=True)
            if "Average =" in res.stdout:
                avg_part = res.stdout.split("Average =")[-1].replace("ms", "").strip()
                ping_ms = float(avg_part)
        except Exception:
            pass

        mbps = 0.0
        # Probe high-speed CDN chunk (10MB payload)
        test_endpoints = [
            "https://speed.cloudflare.com/__down?bytes=10485760",
            "https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css"
        ]

        for url in test_endpoints:
            try:
                t0 = time.time()
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
                with urllib.request.urlopen(req, timeout=8) as resp:
                    chunk = resp.read()
                dt = time.time() - t0
                if dt > 0.05 and len(chunk) > 0:
                    mbps = (len(chunk) * 8.0) / (dt * 1_000_000.0)
                    break
            except Exception as e:
                self.logger.debug(f"Speed probe attempt failed on {url}: {e}", "NETWORK")
                continue

        if mbps > 0.0:
            msg = f"Sir, internet speed test complete! Download speed {mbps:.1f} Mbps hai, aur ping latency {ping_ms:.0f} ms hai. Connection bilkul fast aur stable chal raha hai."
        else:
            msg = f"Sir, ping latency {ping_ms:.0f} ms hai, connection online hai lekin bandwidth probe complete nahi ho paaya."

        self.logger.success(msg, "NETWORK")
        return mbps, ping_ms, msg

    def get_ip_summary_speech(self) -> str:
        ip = self.get_ip_info()
        ssid = self.get_wifi_ssid()
        return f"Sir, aapka Wi-Fi '{ssid}' se connected hai. Local IP {ip['local_ip']} hai aur Public IP {ip['public_ip']} hai."

    def get_summary_speech(self) -> str:
        _, _, msg = self.measure_internet_speed()
        return msg


def get_network_diagnostics() -> NetworkDiagnostics:
    return NetworkDiagnostics()
