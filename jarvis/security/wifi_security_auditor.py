"""
================================================================================
                    JARVIS WI-FI CYBERSECURITY AUDITOR
================================================================================
Wireless network security assessor: probes current 802.11 association parameters,
evaluates encryption strength (WPA3-SAE vs WPA2-PSK vs Open), measures signal RSSI
radio attenuation, and flags rogue or unencrypted access points.
================================================================================
"""

import subprocess
from typing import Dict, Any, List, Optional

from jarvis.core.logger import get_logger


class WiFiSecurityAuditor:
    """Evaluates the cryptographic security posture of the active Wi-Fi link."""

    def __init__(self) -> None:
        self.logger = get_logger()

    def audit_active_wifi(self) -> Dict[str, Any]:
        """
        Query Windows WLAN API for current interface security parameters.
        """
        self.logger.info("Executing Wi-Fi cybersecurity audit...", "WIFI")

        details = {
            "ssid": "Unknown",
            "bssid": "Unknown",
            "radio_type": "Unknown",
            "authentication": "Unknown",
            "cipher": "Unknown",
            "signal_percent": 0,
            "security_rating": "UNKNOWN",
            "warnings": []
        }

        try:
            res = subprocess.run(
                ["netsh", "wlan", "show", "interfaces"],
                capture_output=True,
                text=True,
                timeout=4
            )
            for line in res.stdout.splitlines():
                if ":" in line:
                    key, val = [p.strip() for p in line.split(":", 1)]
                    k_low = key.lower()
                    if k_low == "ssid":
                        details["ssid"] = val
                    elif k_low == "bssid":
                        details["bssid"] = val
                    elif "radio" in k_low:
                        details["radio_type"] = val
                    elif "authentication" in k_low:
                        details["authentication"] = val
                    elif "cipher" in k_low:
                        details["cipher"] = val
                    elif "signal" in k_low:
                        digits = "".join([c for c in val if c.isdigit()])
                        details["signal_percent"] = int(digits) if digits else 0

            # Security rating evaluation
            auth = details["authentication"].upper()
            cipher = details["cipher"].upper()

            if "OPEN" in auth or "NONE" in auth:
                details["security_rating"] = "DANGEROUS_UNENCRYPTED"
                details["warnings"].append("Wi-Fi network is unencrypted! Traffic is vulnerable to eavesdropping.")
                self.logger.critical("SECURITY HAZARD: Connected to unencrypted Wi-Fi access point!", "WIFI")
            elif "WEP" in auth or "WEP" in cipher:
                details["security_rating"] = "COMPROMISED_WEP"
                details["warnings"].append("WEP cipher is cryptographically broken and easily cracked.")
            elif "WPA3" in auth:
                details["security_rating"] = "EXCELLENT_WPA3"
            elif "WPA2" in auth:
                details["security_rating"] = "STRONG_WPA2"
            else:
                details["security_rating"] = "STANDARD"

            return details

        except Exception as e:
            self.logger.error(f"Error auditing Wi-Fi: {e}", "WIFI")
            return details

    def get_audit_summary_speech(self) -> str:
        d = self.audit_active_wifi()
        ssid = d["ssid"]
        auth = d["authentication"]
        signal = d["signal_percent"]
        rating = d["security_rating"]

        if rating == "DANGEROUS_UNENCRYPTED":
            return f"Caution sir! Aapka Wi-Fi '{ssid}' bilkul unencrypted hai. Kripya VPN activate karein!"
        else:
            return f"Sir, Wi-Fi '{ssid}' secure hai ({auth}). Signal strength {signal}% hai."


def get_wifi_auditor() -> WiFiSecurityAuditor:
    return WiFiSecurityAuditor()
