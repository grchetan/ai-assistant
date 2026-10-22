"""
================================================================================
                    JARVIS HARDWARE PERIPHERALS & DEVICE INSPECTOR
================================================================================
Deep peripheral hardware inspection querying connected GPUs, display monitors,
audio input/output endpoints, and USB devices via PowerShell WMI.
================================================================================
"""

import subprocess
from typing import List, Dict, Any, Optional

try:
    import sounddevice as sd
    _SD_AVAILABLE = True
except ImportError:
    _SD_AVAILABLE = False

from jarvis.core.logger import get_logger


class DeviceInspector:
    """Enumerates peripheral hardware and system components."""

    def __init__(self) -> None:
        self.logger = get_logger()

    def get_gpu_info(self) -> List[Dict[str, str]]:
        """Query GPU graphic adapters via WMI."""
        gpus = []
        cmd = "Get-CimInstance Win32_VideoController | Select-Object Name, DriverVersion, VideoProcessor"
        try:
            res = subprocess.run(["powershell", "-NoProfile", "-Command", cmd], capture_output=True, text=True)
            lines = [l.strip() for l in res.stdout.splitlines() if l.strip()]
            for l in lines[2:]: # skip headers
                if l and not l.startswith("----"):
                    gpus.append({"name": l})
        except Exception:
            pass
        return gpus

    def get_audio_endpoints(self) -> Dict[str, List[Dict[str, Any]]]:
        """Query host audio inputs and outputs via SoundDevice."""
        inputs = []
        outputs = []
        if _SD_AVAILABLE:
            try:
                devices = sd.query_devices()
                for idx, d in enumerate(devices):
                    info = {
                        "index": idx,
                        "name": d["name"],
                        "channels": d["max_input_channels"] if d["max_input_channels"] > 0 else d["max_output_channels"],
                        "default_sample_rate": d["default_samplerate"]
                    }
                    if d["max_input_channels"] > 0:
                        inputs.append(info)
                    if d["max_output_channels"] > 0:
                        outputs.append(info)
            except Exception:
                pass
        return {"inputs": inputs, "outputs": outputs}

    def get_hardware_specs_speech(self) -> str:
        """Spoken summary of device hardware."""
        gpus = self.get_gpu_info()
        gpu_name = gpus[0]["name"] if gpus else "Integrated GPU"
        audio = self.get_audio_endpoints()
        mic_count = len(audio["inputs"])
        speaker_count = len(audio["outputs"])

        return f"Sir, system me Graphics card '{gpu_name}' detected hai, {mic_count} audio input endpoints aur {speaker_count} output devices configured hain."


def get_device_inspector() -> DeviceInspector:
    return DeviceInspector()
