"""
================================================================================
                    JARVIS WEATHER & METEOROLOGY PLUGIN
================================================================================
Fetches real-time weather observations, temperature, and wind conditions
using lightweight wttr.in JSON formatting.
================================================================================
"""

import json
import urllib.request
import urllib.parse
from typing import Dict, Any, Tuple

from jarvis.plugins.plugin_base import JarvisPlugin
from jarvis.core.logger import get_logger


class WeatherPlugin(JarvisPlugin):
    """Provides current weather summaries."""

    @property
    def name(self) -> str:
        return "weather"

    @property
    def description(self) -> str:
        return "Retrieves real-time weather and temperature for any city."

    def can_handle(self, text: str) -> bool:
        t = text.lower()
        return any(k in t for k in ["weather", "mausam", "temperature", "tapman"])

    def execute(self, text: str, payload: Dict[str, Any]) -> Tuple[bool, str]:
        city = payload.get("city", "Delhi")
        if not city or city.strip() == "":
            city = "Delhi"

        encoded_city = urllib.parse.quote(city.strip())
        url = f"https://wttr.in/{encoded_city}?format=j1"

        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'JARVIS/4.0'})
            with urllib.request.urlopen(req, timeout=4) as resp:
                data = json.loads(resp.read().decode('utf-8'))

            current = data['current_condition'][0]
            temp_c = current['temp_C']
            desc = current['weatherDesc'][0]['value']
            humidity = current['humidity']
            wind = current['windspeedKmph']

            speech = (
                f"Sir, {city.capitalize()} me abhi temperature {temp_c}°C hai. "
                f"Conditions '{desc}' hain, humidity {humidity}% hai, aur wind speed {wind} km/h hai."
            )
            return True, speech
        except Exception as e:
            return False, f"Sir, {city} ka weather data abhi fetch nahi ho paya."
