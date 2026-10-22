"""
================================================================================
                    JARVIS HARDWARE & TELEMETRY MONITOR
================================================================================
Real-time hardware diagnostics engine utilizing psutil to monitor CPU load,
RAM utilization, disk partition health, battery levels, network throughput,
and top resource-consuming processes.
================================================================================
"""

import time
import threading
from typing import Dict, Any, List, Optional

try:
    import psutil
    _PSUTIL_AVAILABLE = True
except ImportError:
    _PSUTIL_AVAILABLE = False

from jarvis.core.events import get_event_bus, EventType, Priority
from jarvis.core.state import get_state_manager
from jarvis.core.logger import get_logger


class HardwareMonitor:
    """Threaded background hardware telemetry collector."""

    _instance: Optional["HardwareMonitor"] = None
    _lock = threading.RLock()

    def __new__(cls) -> "HardwareMonitor":
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(HardwareMonitor, cls).__new__(cls)
                cls._instance._init_monitor()
            return cls._instance

    def _init_monitor(self) -> None:
        self.bus = get_event_bus()
        self.state = get_state_manager()
        self.logger = get_logger()

        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._last_net_io = None
        self._last_net_time = time.time()
        self._polling_interval = 2.0

    def start(self, interval: float = 2.0) -> None:
        """Launch background telemetry worker."""
        if self._running or not _PSUTIL_AVAILABLE:
            return
        self._polling_interval = interval
        self._running = True
        self._thread = threading.Thread(
            target=self._telemetry_worker,
            name="JarvisHardwareMonitor",
            daemon=True
        )
        self._thread.start()
        self.logger.info("Hardware telemetry monitor activated.", "SYSTEM")

    def stop(self) -> None:
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)

    def _telemetry_worker(self) -> None:
        while self._running:
            try:
                metrics = self.collect_snapshot()
                self.state.update_hardware_metrics(
                    cpu=metrics["cpu_percent"],
                    ram=metrics["ram_percent"],
                    battery=metrics["battery_percent"],
                    plugged=metrics["battery_plugged"],
                    net_status="Online"
                )
                self.bus.publish(
                    EventType.HARDWARE_METRICS,
                    data=metrics,
                    priority=Priority.LOW
                )
            except Exception as e:
                self.logger.debug(f"Telemetry collection error: {e}", "SYSTEM")
            time.sleep(self._polling_interval)

    def collect_snapshot(self) -> Dict[str, Any]:
        """Synchronously collect complete system metrics."""
        if not _PSUTIL_AVAILABLE:
            return {
                "cpu_percent": 0.0,
                "ram_percent": 0.0,
                "ram_used_gb": 0.0,
                "ram_total_gb": 0.0,
                "battery_percent": None,
                "battery_plugged": True,
                "disk_percent": 0.0,
                "net_sent_kbps": 0.0,
                "net_recv_kbps": 0.0
            }

        # CPU
        cpu_overall = psutil.cpu_percent(interval=None)
        cpu_cores = psutil.cpu_percent(percpu=True, interval=None)

        # Virtual Memory
        mem = psutil.virtual_memory()
        ram_percent = mem.percent
        ram_used_gb = round(mem.used / (1024 ** 3), 2)
        ram_total_gb = round(mem.total / (1024 ** 3), 2)

        # Battery
        battery_percent = None
        battery_plugged = True
        battery = psutil.sensors_battery()
        if battery:
            battery_percent = round(battery.percent, 1)
            battery_plugged = battery.power_plugged

        # Disk
        try:
            disk = psutil.disk_usage("C:\\")
            disk_percent = disk.percent
        except Exception:
            disk_percent = 0.0

        # Network speed
        net_sent_kbps = 0.0
        net_recv_kbps = 0.0
        try:
            current_net = psutil.net_io_counters()
            now = time.time()
            if self._last_net_io is not None:
                dt = max(now - self._last_net_time, 0.1)
                net_sent_kbps = round(((current_net.bytes_sent - self._last_net_io.bytes_sent) / 1024) / dt, 1)
                net_recv_kbps = round(((current_net.bytes_recv - self._last_net_io.bytes_recv) / 1024) / dt, 1)
            self._last_net_io = current_net
            self._last_net_time = now
        except Exception:
            pass

        return {
            "cpu_percent": cpu_overall,
            "cpu_cores": cpu_cores,
            "ram_percent": ram_percent,
            "ram_used_gb": ram_used_gb,
            "ram_total_gb": ram_total_gb,
            "battery_percent": battery_percent,
            "battery_plugged": battery_plugged,
            "disk_percent": disk_percent,
            "net_sent_kbps": net_sent_kbps,
            "net_recv_kbps": net_recv_kbps
        }

    def get_top_processes(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Return top memory/CPU consuming processes."""
        if not _PSUTIL_AVAILABLE:
            return []
        procs = []
        for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                info = p.info
                procs.append(info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        # Sort by memory percent descending
        procs.sort(key=lambda x: x.get('memory_percent') or 0, reverse=True)
        return procs[:limit]

    def get_summary_speech(self) -> str:
        """Generate a natural spoken summary of system hardware health."""
        snap = self.collect_snapshot()
        cpu = snap['cpu_percent']
        ram = snap['ram_percent']
        bat = snap['battery_percent']

        bat_text = f"Battery {bat}% par hai" if bat is not None else "Direct AC power connected hai"
        if snap.get('battery_plugged') and bat is not None:
            bat_text += " aur charging par hai"

        return f"Sir, CPU usage {cpu}% hai, RAM utilization {ram}% hai, aur {bat_text}. Sabhi components safely operate kar rahe hain."


def get_hardware_monitor() -> HardwareMonitor:
    return HardwareMonitor()
