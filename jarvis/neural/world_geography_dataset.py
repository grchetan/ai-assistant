"""
================================================================================
            JARVIS IN-HOUSE WORLD GEOGRAPHY & NATIONS REPOSITORY
================================================================================
Offline geospatial dataset covering major sovereign countries:
  • Capitals, Continents, Official Languages
  • National Currencies & Standard Timezones
  • Population, GDP rank, and Notable Landmarks
================================================================================
"""

from typing import Dict, List, Any, Optional
from jarvis.core.logger import get_logger

COUNTRIES_DATA: List[Dict[str, Any]] = [
    {"name": "India", "capital": "New Delhi", "continent": "Asia", "currency": "Indian Rupee (INR - ₹)", "languages": ["Hindi", "English"], "pop": "1.43 Billion", "landmark": "Taj Mahal, Himalayas, Red Fort", "desc": "World's largest democracy, fastest-growing major economy, and ancient civilization."},
    {"name": "United States", "capital": "Washington, D.C.", "continent": "North America", "currency": "US Dollar (USD - $)", "languages": ["English"], "pop": "335 Million", "landmark": "Grand Canyon, Statue of Liberty", "desc": "Global economic leader, technology innovation hub, and federal republic."},
    {"name": "United Kingdom", "capital": "London", "continent": "Europe", "currency": "British Pound (GBP - £)", "languages": ["English"], "pop": "67 Million", "landmark": "Big Ben, Stonehenge, Tower of London", "desc": "Island nation in northwestern Europe; birthplace of the Industrial Revolution."},
    {"name": "Japan", "capital": "Tokyo", "continent": "Asia", "currency": "Japanese Yen (JPY - ¥)", "languages": ["Japanese"], "pop": "124 Million", "landmark": "Mount Fuji, Kyoto Temples", "desc": "Island nation renowned for advanced robotics, bullet trains, and cultural heritage."},
    {"name": "Germany", "capital": "Berlin", "continent": "Europe", "currency": "Euro (EUR - €)", "languages": ["German"], "pop": "84 Million", "landmark": "Brandenburg Gate, Neuschwanstein Castle", "desc": "Europe's largest economy; world leader in precision engineering and automotive innovation."},
    {"name": "France", "capital": "Paris", "continent": "Europe", "currency": "Euro (EUR - €)", "languages": ["French"], "pop": "68 Million", "landmark": "Eiffel Tower, Louvre Museum", "desc": "Global hub for art, gastronomy, aerospace (Airbus), and diplomacy."},
    {"name": "China", "capital": "Beijing", "continent": "Asia", "currency": "Renminbi Yuan (CNY - ¥)", "languages": ["Standard Mandarin"], "pop": "1.41 Billion", "landmark": "Great Wall of China, Forbidden City", "desc": "East Asian economic powerhouse; global center of manufacturing and infrastructure."},
    {"name": "Russia", "capital": "Moscow", "continent": "Europe / Asia", "currency": "Russian Ruble (RUB - ₽)", "languages": ["Russian"], "pop": "144 Million", "landmark": "Red Square, Lake Baikal, Kremlin", "desc": "Largest country by land area in the world, spanning eleven time zones."},
    {"name": "Canada", "capital": "Ottawa", "continent": "North America", "currency": "Canadian Dollar (CAD - $)", "languages": ["English", "French"], "pop": "40 Million", "landmark": "Niagara Falls, Rocky Mountains", "desc": "Second largest country by land area, renowned for vast wilderness and natural resources."},
    {"name": "Australia", "capital": "Canberra", "continent": "Oceania", "currency": "Australian Dollar (AUD - $)", "languages": ["English"], "pop": "26 Million", "landmark": "Sydney Opera House, Great Barrier Reef", "desc": "Megadiverse continent-country famous for unique wildlife and mineral wealth."},
    {"name": "Brazil", "capital": "Brasília", "continent": "South America", "currency": "Brazilian Real (BRL - R$)", "languages": ["Portuguese"], "pop": "215 Million", "landmark": "Christ the Redeemer, Amazon Rainforest", "desc": "Largest country in South America, home to 60% of the Amazon rainforest."},
    {"name": "South Africa", "capital": "Pretoria / Cape Town / Bloemfontein", "continent": "Africa", "currency": "South African Rand (ZAR - R)", "languages": ["11 official (Zulu, Xhosa, Afrikaans, English)"], "pop": "60 Million", "landmark": "Table Mountain, Kruger National Park", "desc": "Southern tip of Africa with immense biodiversity and rich cultural tapestry."},
    {"name": "United Arab Emirates", "capital": "Abu Dhabi", "continent": "Asia", "currency": "UAE Dirham (AED)", "languages": ["Arabic", "English"], "pop": "10 Million", "landmark": "Burj Khalifa, Sheikh Zayed Grand Mosque", "desc": "Middle Eastern federation known for architectural marvels, finance, and tourism."},
    {"name": "Singapore", "capital": "Singapore", "continent": "Asia", "currency": "Singapore Dollar (SGD - $)", "languages": ["English", "Malay", "Mandarin", "Tamil"], "pop": "5.9 Million", "landmark": "Marina Bay Sands, Gardens by the Bay", "desc": "Global financial, maritime, and smart-city innovation metropolis in Southeast Asia."}
]


class WorldGeographyEngine:
    """Geographical query engine."""

    def __init__(self) -> None:
        self.logger = get_logger()
        self.countries = COUNTRIES_DATA

    def lookup_country(self, query: str) -> Optional[Dict[str, Any]]:
        q = query.lower()
        for c in self.countries:
            if c["name"].lower() in q or c["capital"].lower() in q:
                return c
        return None

    def format_country_speech(self, country: Dict[str, Any]) -> str:
        return (
            f"Sir, {country['name']}: Capital is {country['capital']} ({country['continent']}). "
            f"Official currency is {country['currency']}. Population: ~{country['pop']}. "
            f"Prominent landmarks include {country['landmark']}. {country['desc']}"
        )


_geo_instance: Optional[WorldGeographyEngine] = None

def get_world_geography() -> WorldGeographyEngine:
    global _geo_instance
    if _geo_instance is None:
        _geo_instance = WorldGeographyEngine()
    return _geo_instance
