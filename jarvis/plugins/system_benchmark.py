"""
================================================================================
                    JARVIS HARDWARE BENCHMARK & PERFORMANCE SUITE
================================================================================
Evaluates real-time hardware compute capability: CPU floating point throughput,
RAM sequential access bandwidth, and local disk I/O performance.
================================================================================
"""

import time
import tempfile
import numpy as np
from pathlib import Path
from typing import Dict, Any, Tuple

from jarvis.plugins.plugin_base import JarvisPlugin
from jarvis.core.logger import get_logger


class SystemBenchmarkPlugin(JarvisPlugin):
    """Executes CPU, RAM, and Disk performance stress benchmarks."""

    @property
    def name(self) -> str:
        return "benchmark"

    @property
    def description(self) -> str:
        return "Measures system compute performance and hardware benchmark score."

    def can_handle(self, text: str) -> bool:
        t = text.lower()
        return any(k in t for k in ["benchmark", "speed test pc", "performance test", "hardware score"])

    def execute(self, text: str, payload: Dict[str, Any]) -> Tuple[bool, str]:
        logger = get_logger()
        logger.info("Executing JARVIS Hardware Benchmark...", "BENCH")

        # 1. CPU Floating Point Benchmark
        t0 = time.perf_counter()
        a = np.random.rand(1500, 1500).astype(np.float32)
        b = np.random.rand(1500, 1500).astype(np.float32)
        _ = np.dot(a, b)
        cpu_time = max(time.perf_counter() - t0, 0.001)
        gflops = (2 * (1500 ** 3)) / (cpu_time * 1e9)

        # 2. RAM Throughput Benchmark
        t0 = time.perf_counter()
        arr = np.ones((8000, 8000), dtype=np.float32)
        _ = arr * 2.5
        ram_time = max(time.perf_counter() - t0, 0.001)
        ram_mb = (8000 * 8000 * 4) / (1024 * 1024)
        ram_speed_mbps = ram_mb / ram_time

        # 3. Disk I/O Benchmark
        temp_file = Path(tempfile.gettempdir()) / "jarvis_bench_io.dat"
        data_block = b"J" * (50 * 1024 * 1024) # 50 MB
        t0 = time.perf_counter()
        with open(temp_file, "wb") as f:
            f.write(data_block)
        disk_time = max(time.perf_counter() - t0, 0.001)
        disk_speed_mbps = 50.0 / disk_time
        temp_file.unlink(missing_ok=True)

        # Composite score
        total_score = int(gflops * 100 + (ram_speed_mbps / 20) + (disk_speed_mbps / 10))

        speech = (
            f"Sir, benchmark complete! CPU Compute: {gflops:.1f} GFLOPS, "
            f"RAM bandwidth: {ram_speed_mbps:.0f} MB/s, Disk write speed: {disk_speed_mbps:.0f} MB/s. "
            f"JARVIS Performance Score: {total_score} points!"
        )
        logger.success(speech, "BENCH")
        return True, speech
