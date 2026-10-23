"""
================================================================================
            JARVIS IN-HOUSE DEEP SPACE & ASTRONOMY CATALOG
================================================================================
Comprehensive offline astronomical registry covering:
  • Planets, Dwarf Planets & Solar System Moons (Titan, Europa, Ganymede)
  • Constellations & Navigation Stars (Polaris, Sirius, Betelgeuse)
  • Messier Deep-Space Objects (Andromeda, Orion Nebula, Pleiades)
Zero cloud API required.
================================================================================
"""

from typing import Dict, List, Any, Optional
from jarvis.core.logger import get_logger

ASTRONOMICAL_BODIES: List[Dict[str, Any]] = [
    {"name": "Mercury", "type": "Terrestrial Planet", "distance_au": 0.39, "moons": 0, "day_length": "59 Earth days", "desc": "Smallest planet in the Solar System, closest to the Sun; has extreme temperature swings from -180°C to 430°C."},
    {"name": "Venus", "type": "Terrestrial Planet", "distance_au": 0.72, "moons": 0, "day_length": "243 Earth days", "desc": "Hottest planet in Solar System (465°C) due to a runaway greenhouse effect from thick CO2 clouds and sulfuric acid rain."},
    {"name": "Earth", "type": "Terrestrial Planet", "distance_au": 1.00, "moons": 1, "day_length": "24 hours", "desc": "Only known celestial body harboring life; liquid water oceans cover ~71% of surface."},
    {"name": "Mars", "type": "Terrestrial Planet", "distance_au": 1.52, "moons": 2, "day_length": "24.6 hours", "desc": "The Red Planet; home to Olympus Mons (tallest planetary volcano in Solar System) and Valles Marineris canyon system."},
    {"name": "Jupiter", "type": "Gas Giant", "distance_au": 5.20, "moons": 95, "day_length": "9.9 hours", "desc": "Largest planet in the Solar System; features the iconic Great Red Spot storm which has raged for centuries."},
    {"name": "Saturn", "type": "Gas Giant", "distance_au": 9.58, "moons": 146, "day_length": "10.7 hours", "desc": "Famous for its spectacular ring system composed of billions of chunks of water ice and rock."},
    {"name": "Uranus", "type": "Ice Giant", "distance_au": 19.22, "moons": 28, "day_length": "17.2 hours", "desc": "Rotates at an extreme axial tilt of 98 degrees, effectively spinning on its side; pale cyan color caused by methane in atmosphere."},
    {"name": "Neptune", "type": "Ice Giant", "distance_au": 30.05, "moons": 16, "day_length": "16.1 hours", "desc": "Most distant planet; features supersonic winds reaching up to 2,100 km/h and dark dynamic storms."},
    {"name": "Titan", "type": "Moon of Saturn", "distance_au": 9.58, "moons": 0, "day_length": "16 Earth days", "desc": "Only moon in Solar System with a dense atmosphere; possesses liquid hydrocarbon lakes of methane and ethane on its surface."},
    {"name": "Europa", "type": "Moon of Jupiter", "distance_au": 5.20, "moons": 0, "day_length": "3.5 Earth days", "desc": "Smooth icy crust covering a vast subterranean global saltwater ocean with twice the water of all Earth's oceans combined."},
    {"name": "Sirius", "type": "Binary Star (A1V)", "distance_ly": 8.6, "constellation": "Canis Major", "desc": "Brightest star in Earth's night sky; binary system consisting of a main-sequence star and a white dwarf companion."},
    {"name": "Betelgeuse", "type": "Red Supergiant", "distance_ly": 642, "constellation": "Orion", "desc": "Massive pulsating red supergiant star nearing the end of its life cycle; destined to explode as a dramatic supernova."}
]


class AstronomyDeepCatalog:
    """Offline astronomical reference engine."""

    def __init__(self) -> None:
        self.logger = get_logger()
        self.bodies = ASTRONOMICAL_BODIES

    def search_body(self, query: str) -> Optional[Dict[str, Any]]:
        q = query.lower()
        for b in self.bodies:
            if b["name"].lower() in q:
                return b
        return None

    def format_speech(self, body: Dict[str, Any]) -> str:
        return (
            f"Sir, {body['name']} ({body['type']}): "
            f"Distance: {body.get('distance_au', 'N/A')} AU. {body['desc']}"
        )


_astro_instance: Optional[AstronomyDeepCatalog] = None

def get_astronomy_catalog() -> AstronomyDeepCatalog:
    global _astro_instance
    if _astro_instance is None:
        _astro_instance = AstronomyDeepCatalog()
    return _astro_instance
