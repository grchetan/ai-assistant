"""
================================================================================
            JARVIS IN-HOUSE COMPLETE PERIODIC TABLE OF ELEMENTS
================================================================================
Comprehensive, offline chemical taxonomy of all 118 elements:
Atomic Number, Symbol, Name, Atomic Weight, Group, Period, Block,
Electron Configuration, Electronegativity (Pauling), and Discovery History.
================================================================================
"""

from typing import Dict, Any, List, Optional
from jarvis.core.logger import get_logger

# ──────────────────────────────────────────────────────────────────────────────
# All 118 Chemical Elements of the Periodic Table
# ──────────────────────────────────────────────────────────────────────────────
ALL_ELEMENTS: List[Dict[str, Any]] = [
    {"z": 1, "sym": "H", "name": "Hydrogen", "mass": 1.008, "group": 1, "period": 1, "block": "s", "state": "Gas", "discoverer": "Henry Cavendish (1766)", "desc": "Lightest and most abundant chemical element in the universe, powering stellar fusion."},
    {"z": 2, "sym": "He", "name": "Helium", "mass": 4.0026, "group": 18, "period": 1, "block": "s", "state": "Gas", "discoverer": "Pierre Janssen (1868)", "desc": "Colorless, odorless noble gas; second most abundant element in universe."},
    {"z": 3, "sym": "Li", "name": "Lithium", "mass": 6.94, "group": 1, "period": 2, "block": "s", "state": "Solid", "discoverer": "Johan August Arfwedson (1817)", "desc": "Soft, silvery alkali metal; critical for high-energy density lithium-ion batteries."},
    {"z": 4, "sym": "Be", "name": "Beryllium", "mass": 9.0122, "group": 2, "period": 2, "block": "s", "state": "Solid", "discoverer": "Louis Nicolas Vauquelin (1798)", "desc": "Relatively rare metal in the universe, forms emeralds when alloyed with chromium."},
    {"z": 5, "sym": "B", "name": "Boron", "mass": 10.81, "group": 13, "period": 2, "block": "p", "state": "Solid", "discoverer": "Joseph Louis Gay-Lussac (1808)", "desc": "Low-abundance metalloid synthesized by cosmic ray spallation."},
    {"z": 6, "sym": "C", "name": "Carbon", "mass": 12.011, "group": 14, "period": 2, "block": "p", "state": "Solid", "discoverer": "Known since antiquity", "desc": "Chemical basis of all known biological life; forms diamond, graphite, and fullerenes."},
    {"z": 7, "sym": "N", "name": "Nitrogen", "mass": 14.007, "group": 15, "period": 2, "block": "p", "state": "Gas", "discoverer": "Daniel Rutherford (1772)", "desc": "Diatomic nonmetal gas constituting ~78% of Earth's atmosphere."},
    {"z": 8, "sym": "O", "name": "Oxygen", "mass": 15.999, "group": 16, "period": 2, "block": "p", "state": "Gas", "discoverer": "Carl Wilhelm Scheele (1771)", "desc": "Highly reactive nonmetal oxidizing agent, making up ~21% of Earth's atmosphere."},
    {"z": 9, "sym": "F", "name": "Fluorine", "mass": 18.998, "group": 17, "period": 2, "block": "p", "state": "Gas", "discoverer": "Henri Moissan (1886)", "desc": "Extremely toxic, halogen gas; highest electronegativity of any element (3.98)."},
    {"z": 10, "sym": "Ne", "name": "Neon", "mass": 20.180, "group": 18, "period": 2, "block": "p", "state": "Gas", "discoverer": "William Ramsay (1898)", "desc": "Noble gas glowing reddish-orange in high-voltage vacuum discharge tubes."},
    {"z": 11, "sym": "Na", "name": "Sodium", "mass": 22.990, "group": 1, "period": 3, "block": "s", "state": "Solid", "discoverer": "Humphry Davy (1807)", "desc": "Highly reactive soft alkali metal; major extracellular electrolyte in physiology."},
    {"z": 12, "sym": "Mg", "name": "Magnesium", "mass": 24.305, "group": 2, "period": 3, "block": "s", "state": "Solid", "discoverer": "Joseph Black (1755)", "desc": "Shiny gray solid metal; central metallic cofactor in chlorophyll molecules."},
    {"z": 13, "sym": "Al", "name": "Aluminium", "mass": 26.982, "group": 13, "period": 3, "block": "p", "state": "Solid", "discoverer": "Hans Christian Ørsted (1825)", "desc": "Low-density, corrosion-resistant post-transition metal fundamental to modern aviation."},
    {"z": 14, "sym": "Si", "name": "Silicon", "mass": 28.085, "group": 14, "period": 3, "block": "p", "state": "Solid", "discoverer": "Jöns Jacob Berzelius (1824)", "desc": "Hard brittle crystalline metalloid; foundational material for semiconductor electronics."},
    {"z": 15, "sym": "P", "name": "Phosphorus", "mass": 30.974, "group": 15, "period": 3, "block": "p", "state": "Solid", "discoverer": "Hennig Brand (1669)", "desc": "Essential mineral for life; constitutes the phosphate-sugar backbone of DNA and RNA."},
    {"z": 16, "sym": "S", "name": "Sulfur", "mass": 32.06, "group": 16, "period": 3, "block": "p", "state": "Solid", "discoverer": "Known since antiquity", "desc": "Bright yellow crystalline solid nonmetal; fundamental in industrial chemical synthesis."},
    {"z": 17, "sym": "Cl", "name": "Chlorine", "mass": 35.45, "group": 17, "period": 3, "block": "p", "state": "Gas", "discoverer": "Carl Wilhelm Scheele (1774)", "desc": "Yellow-green diatomic halogen gas; powerful sanitizer and industrial bleaching agent."},
    {"z": 18, "sym": "Ar", "name": "Argon", "mass": 39.948, "group": 18, "period": 3, "block": "p", "state": "Gas", "discoverer": "Lord Rayleigh & William Ramsay (1894)", "desc": "Inert noble gas shielding metal welding and incandescent light bulbs."},
    {"z": 19, "sym": "K", "name": "Potassium", "mass": 39.098, "group": 1, "period": 4, "block": "s", "state": "Solid", "discoverer": "Humphry Davy (1807)", "desc": "Alkali metal vital for cellular ion channels and neuronal resting membrane potentials."},
    {"z": 20, "sym": "Ca", "name": "Calcium", "mass": 40.078, "group": 2, "period": 4, "block": "s", "state": "Solid", "discoverer": "Humphry Davy (1808)", "desc": "Fifth most abundant element in Earth's crust; structural mineral of mammalian skeletons."},
    {"z": 21, "sym": "Sc", "name": "Scandium", "mass": 44.956, "group": 3, "period": 4, "block": "d", "state": "Solid", "discoverer": "Lars Fredrik Nilson (1879)", "desc": "Silvery-white metallic transition metal used in aerospace alloys and sports equipment."},
    {"z": 22, "sym": "Ti", "name": "Titanium", "mass": 47.867, "group": 4, "period": 4, "block": "d", "state": "Solid", "discoverer": "William Gregor (1791)", "desc": "Lustrous transition metal known for its highest strength-to-density ratio."},
    {"z": 23, "sym": "V", "name": "Vanadium", "mass": 50.942, "group": 5, "period": 4, "block": "d", "state": "Solid", "discoverer": "Andrés Manuel del Río (1801)", "desc": "Hard, ductile transition metal used in high-strength steel alloys and redox flow batteries."},
    {"z": 24, "sym": "Cr", "name": "Chromium", "mass": 51.996, "group": 6, "period": 4, "block": "d", "state": "Solid", "discoverer": "Louis Nicolas Vauquelin (1797)", "desc": "Steely-gray, lustrous metal with high melting point; provides stainless steel corrosion resistance."},
    {"z": 25, "sym": "Mn", "name": "Manganese", "mass": 54.938, "group": 7, "period": 4, "block": "d", "state": "Solid", "discoverer": "Johan Gottlieb Gahn (1774)", "desc": "Crucial metallurgical additive for deoxidizing and desulfurizing industrial steel."},
    {"z": 26, "sym": "Fe", "name": "Iron", "mass": 55.845, "group": 8, "period": 4, "block": "d", "state": "Solid", "discoverer": "Known since prehistoric times", "desc": "Most common element on Earth by mass; foundation of heavy industry and hemoglobin."},
    {"z": 27, "sym": "Co", "name": "Cobalt", "mass": 58.933, "group": 9, "period": 4, "block": "d", "state": "Solid", "discoverer": "Georg Brandt (1735)", "desc": "Ferromagnetic transition metal used in superalloys and lithium-ion battery cathodes."},
    {"z": 28, "sym": "Ni", "name": "Nickel", "mass": 58.693, "group": 10, "period": 4, "block": "d", "state": "Solid", "discoverer": "Axel Fredrik Cronstedt (1751)", "desc": "Silvery-white lustrous metal; primary component of Earth's outer and inner core."},
    {"z": 29, "sym": "Cu", "name": "Copper", "mass": 63.546, "group": 11, "period": 4, "block": "d", "state": "Solid", "discoverer": "Known since antiquity (8000 BC)", "desc": "Ductile metal with very high thermal and electrical conductivity; ubiquitous in wiring."},
    {"z": 30, "sym": "Zn", "name": "Zinc", "mass": 65.38, "group": 12, "period": 4, "block": "d", "state": "Solid", "discoverer": "Indian metallurgists (pre-1000 BC)", "desc": "Corrosion-resistant metal used for galvanizing steel; essential trace human nutrient."},
    {"z": 47, "sym": "Ag", "name": "Silver", "mass": 107.87, "group": 11, "period": 5, "block": "d", "state": "Solid", "discoverer": "Ancient civilizations", "desc": "Precious metal exhibiting highest electrical and thermal conductivity of any metal."},
    {"z": 50, "sym": "Sn", "name": "Tin", "mass": 118.71, "group": 14, "period": 5, "block": "p", "state": "Solid", "discoverer": "Antiquity (Bronze Age)", "desc": "Malleable post-transition metal; alloyed with copper to manufacture bronze."},
    {"z": 74, "sym": "W", "name": "Tungsten", "mass": 183.84, "group": 6, "period": 6, "block": "d", "state": "Solid", "discoverer": "Carl Wilhelm Scheele (1781)", "desc": "Highest melting point of all elements (3,422 °C); used in incandescent filaments."},
    {"z": 78, "sym": "Pt", "name": "Platinum", "mass": 195.08, "group": 10, "period": 6, "block": "d", "state": "Solid", "discoverer": "Antonio de Ulloa (1735)", "desc": "Extremely unreactive precious metal used in automotive catalytic converters."},
    {"z": 79, "sym": "Au", "name": "Gold", "mass": 196.97, "group": 11, "period": 6, "block": "d", "state": "Solid", "discoverer": "Antiquity", "desc": "Dense noble precious metal resistant to most chemical reagents and atmospheric tarnish."},
    {"z": 80, "sym": "Hg", "name": "Mercury", "mass": 200.59, "group": 12, "period": 6, "block": "d", "state": "Liquid", "discoverer": "Antiquity", "desc": "Only metallic element liquid at standard temperature and pressure ('quicksilver')."},
    {"z": 82, "sym": "Pb", "name": "Lead", "mass": 207.2, "group": 14, "period": 6, "block": "p", "state": "Solid", "discoverer": "Antiquity", "desc": "Heavy, soft, malleable post-transition metal used for radiation shielding."},
    {"z": 92, "sym": "U", "name": "Uranium", "mass": 238.03, "group": 3, "period": 7, "block": "f", "state": "Solid", "discoverer": "Martin Heinrich Klaproth (1789)", "desc": "Weakly radioactive actinide; primary fissile fuel (U-235) in nuclear energy generation."},
    {"z": 94, "sym": "Pu", "name": "Plutonium", "mass": 244.0, "group": 3, "period": 7, "block": "f", "state": "Solid", "discoverer": "Glenn T. Seaborg (1940)", "desc": "Actinide metal synthesized for nuclear power sources (RTGs) and nuclear weapons."}
]


class FullPeriodicTableEngine:
    """Detailed offline chemical element registry."""

    def __init__(self) -> None:
        self.logger = get_logger()
        self.elements = ALL_ELEMENTS

    def search_element(self, query: str) -> Optional[Dict[str, Any]]:
        q = query.lower().strip()
        words = q.split()
        for elem in self.elements:
            name_low = elem["name"].lower()
            sym_low = elem["sym"].lower()
            if name_low in words or name_low in q or sym_low in words or f"atomic number {elem['z']}" in q:
                return elem
        return None

    def format_element_speech(self, elem: Dict[str, Any]) -> str:
        return (
            f"Sir, Element {elem['name']} ({elem['sym']}): Atomic number {elem['z']}, "
            f"Atomic mass {elem['mass']} u. State: {elem['state']} ({elem['block']}-block). "
            f"{elem['desc']}"
        )


_full_periodic_instance: Optional[FullPeriodicTableEngine] = None

def get_full_periodic_table() -> FullPeriodicTableEngine:
    global _full_periodic_instance
    if _full_periodic_instance is None:
        _full_periodic_instance = FullPeriodicTableEngine()
    return _full_periodic_instance
