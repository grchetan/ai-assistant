"""
================================================================================
            JARVIS IN-HOUSE OFFLINE SYSTEM TROUBLESHOOTER & DIAGNOSTICS
================================================================================
Rule-based heuristic expert system diagnosing Windows BSOD error codes,
high CPU/RAM utilization bottlenecks, storage exhaustion, and Wi-Fi outages.
Zero external internet required.
================================================================================
"""

import re
from typing import Dict, List, Optional, Any
from jarvis.core.logger import get_logger

TROUBLESHOOTING_GUIDES: List[Dict[str, Any]] = [
    {
        "id": "bsod_irql",
        "keywords": ["irql_not_less_or_equal", "0x0000000a", "irql bsod", "blue screen driver"],
        "title": "BSOD: IRQL_NOT_LESS_OR_EQUAL (0x0000000A)",
        "cause": "Driver memory leak, corrupted system driver, ya faulty hardware RAM module.",
        "steps": [
            "1. Safe Mode me reboot karke Display Driver Uninstaller (DDU) se graphics driver clean reinstall karein.",
            "2. Command Prompt (Admin) me 'sfc /scannow' aur 'DISM /Online /Cleanup-Image /RestoreHealth' run karein.",
            "3. Windows Memory Diagnostic (mdsched.exe) chala kar RAM integrity verify karein."
        ]
    },
    {
        "id": "bsod_whea",
        "keywords": ["whea_uncorrectable_error", "0x00000124", "whea error", "hardware error bsod"],
        "title": "BSOD: WHEA_UNCORRECTABLE_ERROR (0x00000124)",
        "cause": "Critical hardware failure — mostly CPU overheating, unstable overclocking, ya failing SSD/motherboard.",
        "steps": [
            "1. BIOS me jakar CPU/RAM overclocking profile (XMP/DOCP) ko default/stock frequency par reset karein.",
            "2. CPU cooler check karein aur thermal paste re-apply karein (temperatures 85°C se niche rehne chahiye).",
            "3. CrystalDiskInfo se SSD/HDD ka S.M.A.R.T. health status inspect karein."
        ]
    },
    {
        "id": "perf_high_cpu",
        "keywords": ["100% cpu", "high cpu", "high cpu usage", "cpu full", "laptop garam ho raha", "processor fan loud"],
        "title": "High CPU Usage & Thermal Throttling",
        "cause": "Runaway background process, Windows Search Indexer loop, ya crypto-miner malware.",
        "steps": [
            "1. Task Manager (Ctrl+Shift+Esc) khol kar CPU column par sort karein aur top consumer process identify karein.",
            "2. Agar 'System' ya 'WmiPrvSE' high CPU le raha hai toh drivers update karein.",
            "3. JARVIS command bolein: 'kill process [process_name]' taaki rogue task force-close ho sake."
        ]
    },
    {
        "id": "perf_high_ram",
        "keywords": ["100% ram", "high memory usage", "ram full", "out of memory", "laptop hang"],
        "title": "Memory Exhaustion & Pagefile Spilling",
        "cause": "Chrome memory leaks, unclosed background Docker/Node containers, ya non-paged pool memory leak.",
        "steps": [
            "1. Unused browser tabs aur heavy background services (Docker, VirtualBox) terminate karein.",
            "2. Windows Virtual Memory (Pagefile) setting check karein ki C: drive me kam se kam 8-16 GB unallocated space ho.",
            "3. Killer Network Suite ya third-party antivirus uninstall karke Windows Defender use karein."
        ]
    },
    {
        "id": "net_wifi_drop",
        "keywords": ["wifi bar bar disconnect", "wifi dropping", "no internet secured", "dns server not responding"],
        "title": "Wi-Fi Disconnection & DNS Failure",
        "cause": "Wi-Fi adapter power-saving mode, stale DNS cache, ya IP lease expiry.",
        "steps": [
            "1. Command Prompt me run karein: 'ipconfig /flushdns' aur 'netsh winsock reset'.",
            "2. Device Manager me Wi-Fi Adapter properties me jakar 'Allow the computer to turn off this device to save power' uncheck karein.",
            "3. Network settings me DNS ko Google (8.8.8.8, 8.8.4.4) ya Cloudflare (1.1.1.1) par set karein."
        ]
    }
]


class SystemTroubleshooterEngine:
    """Expert system diagnosing Windows hardware and software anomalies."""

    def __init__(self) -> None:
        self.logger = get_logger()
        self.guides = TROUBLESHOOTING_GUIDES

    def diagnose(self, query: str) -> Optional[str]:
        """Diagnose system issue and return structured remediation steps."""
        q = query.lower().strip()

        for guide in self.guides:
            if any(k in q for k in guide["keywords"]):
                steps_txt = "\n".join(guide["steps"])
                response = (
                    f"Sir, {guide['title']} issue detect hui hai.\n"
                    f"Sambhavit Kaaran: {guide['cause']}\n\n"
                    f"Remediation Steps:\n{steps_txt}"
                )
                self.logger.info(f"Troubleshooter match: {guide['title']}", "EXPERT")
                return response

        return None


_troubleshooter_instance: Optional[SystemTroubleshooterEngine] = None

def get_troubleshooter() -> SystemTroubleshooterEngine:
    global _troubleshooter_instance
    if _troubleshooter_instance is None:
        _troubleshooter_instance = SystemTroubleshooterEngine()
    return _troubleshooter_instance
