"""
================================================================================
                    JARVIS CODE PROFILER & MEMORY TRACER
================================================================================
Developer diagnostic tool using cProfile and tracemalloc to analyze execution
bottlenecks, function call latencies, and memory allocation hotspots.
================================================================================
"""

import cProfile
import pstats
import io
import tracemalloc
from typing import Callable, Any, Tuple, List, Dict

from jarvis.core.logger import get_logger


class SystemProfiler:
    """Profiles execution time and tracks memory allocations."""

    def __init__(self) -> None:
        self.logger = get_logger()

    def profile_callable(self, func: Callable, *args, **kwargs) -> Tuple[Any, str]:
        """Profile a python callable using cProfile and return formatted stats."""
        self.logger.info(f"Profiling execution of '{func.__name__}'...", "PROFILE")
        pr = cProfile.Profile()
        pr.enable()

        result = func(*args, **kwargs)

        pr.disable()
        s = io.StringIO()
        ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
        ps.print_stats(15)

        profile_output = s.getvalue()
        return result, profile_output

    def trace_memory_usage(self, func: Callable, *args, **kwargs) -> Tuple[Any, Dict[str, Any]]:
        """Measure peak memory allocations during callable execution."""
        tracemalloc.start()

        result = func(*args, **kwargs)

        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        stats = {
            "current_memory_kb": round(current / 1024, 2),
            "peak_memory_kb": round(peak / 1024, 2),
            "peak_memory_mb": round(peak / (1024 * 1024), 2)
        }
        self.logger.info(f"Memory profile for '{func.__name__}': Peak = {stats['peak_memory_mb']} MB", "PROFILE")
        return result, stats


def get_system_profiler() -> SystemProfiler:
    return SystemProfiler()
