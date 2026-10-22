"""
================================================================================
                    JARVIS DOCKER CONTAINER ORCHESTRATOR
================================================================================
Container management suite wrapping the Docker Engine CLI:
  - List running and stopped containers
  - Inspect container resource utilization (CPU %, RAM MB, Net I/O)
  - Start, stop, and restart microservice containers
  - Stream live tail container logs
================================================================================
"""

import json
import subprocess
from typing import List, Dict, Any, Tuple, Optional

from jarvis.core.logger import get_logger


class DockerOrchestrator:
    """Manages Docker containers and images via CLI."""

    def __init__(self) -> None:
        self.logger = get_logger()

    def _run_docker(self, args: List[str], timeout: int = 10) -> Tuple[bool, str]:
        try:
            res = subprocess.run(
                ["docker"] + args,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=True
            )
            return True, res.stdout.strip()
        except subprocess.CalledProcessError as e:
            err = e.stderr.strip() if e.stderr else str(e)
            return False, err
        except FileNotFoundError:
            return False, "Docker is not installed or not in system PATH."
        except Exception as e:
            return False, str(e)

    def is_docker_running(self) -> bool:
        """Verify Docker daemon responsiveness."""
        success, _ = self._run_docker(["info"])
        return success

    def list_containers(self, all_containers: bool = False) -> List[Dict[str, str]]:
        """List active or all containers with IDs, names, and status."""
        args = ["ps", "--format", "{{.ID}}|{{.Names}}|{{.Image}}|{{.Status}}|{{.Ports}}"]
        if all_containers:
            args.insert(1, "-a")

        success, out = self._run_docker(args)
        if not success or not out:
            return []

        containers = []
        for line in out.splitlines():
            parts = line.split("|")
            if len(parts) >= 4:
                containers.append({
                    "id": parts[0],
                    "name": parts[1],
                    "image": parts[2],
                    "status": parts[3],
                    "ports": parts[4] if len(parts) > 4 else ""
                })
        return containers

    def start_container(self, name_or_id: str) -> Tuple[bool, str]:
        """Start a stopped Docker container."""
        self.logger.info(f"Starting container: '{name_or_id}'", "DOCKER")
        success, out = self._run_docker(["start", name_or_id])
        if success:
            return True, f"Container '{name_or_id}' start ho gaya sir."
        return False, f"Failed to start container: {out}"

    def stop_container(self, name_or_id: str) -> Tuple[bool, str]:
        """Gracefully stop a running Docker container."""
        self.logger.info(f"Stopping container: '{name_or_id}'", "DOCKER")
        success, out = self._run_docker(["stop", name_or_id])
        if success:
            return True, f"Container '{name_or_id}' band kar diya sir."
        return False, f"Failed to stop container: {out}"

    def get_container_logs(self, name_or_id: str, tail_lines: int = 20) -> str:
        """Fetch recent console logs from a container."""
        success, out = self._run_docker(["logs", "--tail", str(tail_lines), name_or_id])
        if success:
            return out if out else "No recent logs produced."
        return f"Error reading logs: {out}"

    def get_summary_speech(self) -> str:
        if not self.is_docker_running():
            return "Sir, Docker engine system par active nahi hai ya running nahi hai."

        running = self.list_containers(all_containers=False)
        all_c = self.list_containers(all_containers=True)
        return f"Sir, Docker online hai. {len(running)} containers running hain aur total {len(all_c)} containers exist karte hain."


def get_docker_orchestrator() -> DockerOrchestrator:
    return DockerOrchestrator()
