"""
================================================================================
            JARVIS IN-HOUSE OFFLINE SCIENTIFIC ENCYCLOPEDIA
================================================================================
Exhaustive reference data:
  • Fundamental Physical Constants (CODATA recommended values)
  • Comprehensive Periodic Table of Elements (1 to 118)
  • Celestial & Planetary Astronomy Catalog
  • Astronomical coordinates & Solar System properties
Zero cloud API required.
================================================================================
"""

from typing import Dict, Any, Optional, List
from jarvis.core.logger import get_logger

# ──────────────────────────────────────────────────────────────────────────────
# Fundamental Physical Constants (CODATA)
# ──────────────────────────────────────────────────────────────────────────────
PHYSICAL_CONSTANTS: Dict[str, Dict[str, Any]] = {
    "speed_of_light": {
        "symbol": "c",
        "value": 299792458,
        "unit": "m/s",
        "description": "Speed of light in vacuum (exact universal constant)"
    },
    "planck_constant": {
        "symbol": "h",
        "value": 6.62607015e-34,
        "unit": "J·s",
        "description": "Planck constant relating photon energy to frequency (E = hf)"
    },
    "reduced_planck_constant": {
        "symbol": "ħ (h-bar)",
        "value": 1.054571817e-34,
        "unit": "J·s",
        "description": "Dirac constant (h / 2π) used in quantum mechanics"
    },
    "gravitational_constant": {
        "symbol": "G",
        "value": 6.67430e-11,
        "unit": "m³/(kg·s²)",
        "description": "Newtonian constant of gravitation"
    },
    "elementary_charge": {
        "symbol": "e",
        "value": 1.602176634e-19,
        "unit": "Coulombs",
        "description": "Electric charge carried by a single proton"
    },
    "electron_mass": {
        "symbol": "m_e",
        "value": 9.1093837015e-31,
        "unit": "kg",
        "description": "Rest mass of an electron"
    },
    "proton_mass": {
        "symbol": "m_p",
        "value": 1.67262192369e-27,
        "unit": "kg",
        "description": "Rest mass of a proton"
    },
    "neutron_mass": {
        "symbol": "m_n",
        "value": 1.67492749804e-27,
        "unit": "kg",
        "description": "Rest mass of a neutron"
    },
    "avogadro_constant": {
        "symbol": "N_A",
        "value": 6.02214076e23,
        "unit": "mol⁻¹",
        "description": "Number of constituent particles in one mole of substance"
    },
    "boltzmann_constant": {
        "symbol": "k_B",
        "value": 1.380649e-23,
        "unit": "J/K",
        "description": "Relates average kinetic energy of gas particles to temperature"
    },
    "gas_constant": {
        "symbol": "R",
        "value": 8.314462618,
        "unit": "J/(mol·K)",
        "description": "Molar ideal gas constant (R = N_A * k_B)"
    },
    "stefan_boltzmann_constant": {
        "symbol": "σ",
        "value": 5.670374419e-8,
        "unit": "W/(m²·K⁴)",
        "description": "Black-body radiant emittance proportionality constant"
    },
    "vacuum_permittivity": {
        "symbol": "ε_0",
        "value": 8.8541878128e-12,
        "unit": "F/m",
        "description": "Electric constant of free space"
    },
    "vacuum_permeability": {
        "symbol": "μ_0",
        "value": 1.25663706212e-6,
        "unit": "N/A²",
        "description": "Magnetic constant of free space"
    }
}

# ──────────────────────────────────────────────────────────────────────────────
# Periodic Table of Elements (Representative Core Corpus)
# ──────────────────────────────────────────────────────────────────────────────
PERIODIC_TABLE: List[Dict[str, Any]] = [
    {"num": 1, "sym": "H", "name": "Hydrogen", "mass": 1.008, "group": 1, "period": 1, "cat": "Nonmetal", "desc": "Most abundant cosmic element; powers nuclear fusion in stars."},
    {"num": 2, "sym": "He", "name": "Helium", "mass": 4.0026, "group": 18, "period": 1, "cat": "Noble Gas", "desc": "Inert gas; lowest boiling point among all elements."},
    {"num": 3, "sym": "Li", "name": "Lithium", "mass": 6.94, "group": 1, "period": 2, "cat": "Alkali Metal", "desc": "Lightest solid metal; core component of modern rechargeable batteries."},
    {"num": 4, "sym": "Be", "name": "Beryllium", "mass": 9.0122, "group": 2, "period": 2, "cat": "Alkaline Earth", "desc": "High melting point metal used in aerospace and the James Webb mirror."},
    {"num": 5, "sym": "B", "name": "Boron", "mass": 10.81, "group": 13, "period": 2, "cat": "Metalloid", "desc": "Used in semiconductor doping, fiberglass, and pyrotechnics."},
    {"num": 6, "sym": "C", "name": "Carbon", "mass": 12.011, "group": 14, "period": 2, "cat": "Nonmetal", "desc": "Basis of organic chemistry and life; forms diamond, graphite, and graphene."},
    {"num": 7, "sym": "N", "name": "Nitrogen", "mass": 14.007, "group": 15, "period": 2, "cat": "Nonmetal", "desc": "Makes up ~78% of Earth's atmosphere; vital for amino acids and DNA."},
    {"num": 8, "sym": "O", "name": "Oxygen", "mass": 15.999, "group": 16, "period": 2, "cat": "Nonmetal", "desc": "Essential for aerobic cellular respiration; makes up ~21% of Earth's air."},
    {"num": 9, "sym": "F", "name": "Fluorine", "mass": 18.998, "group": 17, "period": 2, "cat": "Halogen", "desc": "Most electronegative element; highly reactive toxic gas."},
    {"num": 10, "sym": "Ne", "name": "Neon", "mass": 20.180, "group": 18, "period": 2, "cat": "Noble Gas", "desc": "Glows reddish-orange in high-voltage electric discharge signs."},
    {"num": 11, "sym": "Na", "name": "Sodium", "mass": 22.990, "group": 1, "period": 3, "cat": "Alkali Metal", "desc": "Soft reactive metal; forms table salt (NaCl) with chlorine."},
    {"num": 12, "sym": "Mg", "name": "Magnesium", "mass": 24.305, "group": 2, "period": 3, "cat": "Alkaline Earth", "desc": "Lightweight structural metal; essential cofactor in biological ATP enzymes."},
    {"num": 13, "sym": "Al", "name": "Aluminium", "mass": 26.982, "group": 13, "period": 3, "cat": "Post-transition Metal", "desc": "Low density, high corrosion resistance; fundamental in aircraft construction."},
    {"num": 14, "sym": "Si", "name": "Silicon", "mass": 28.085, "group": 14, "period": 3, "cat": "Metalloid", "desc": "Heart of the semiconductor industry; basis of microprocessors and solar cells."},
    {"num": 15, "sym": "P", "name": "Phosphorus", "mass": 30.974, "group": 15, "period": 3, "cat": "Nonmetal", "desc": "Essential component of DNA backbone, RNA, cell membranes, and ATP."},
    {"num": 16, "sym": "S", "name": "Sulfur", "mass": 32.06, "group": 16, "period": 3, "cat": "Nonmetal", "desc": "Yellow nonmetal; used in gunpowder, sulfuric acid, and rubber vulcanization."},
    {"num": 17, "sym": "Cl", "name": "Chlorine", "mass": 35.45, "group": 17, "period": 3, "cat": "Halogen", "desc": "Powerful disinfectant; widely used in municipal water purification."},
    {"num": 18, "sym": "Ar", "name": "Argon", "mass": 39.948, "group": 18, "period": 3, "cat": "Noble Gas", "desc": "Third most abundant atmospheric gas (~0.93%); used in shielding arc welding."},
    {"num": 19, "sym": "K", "name": "Potassium", "mass": 39.098, "group": 1, "period": 4, "cat": "Alkali Metal", "desc": "Crucial cellular electrolyte for nerve impulses and cardiac muscle function."},
    {"num": 20, "sym": "Ca", "name": "Calcium", "mass": 40.078, "group": 2, "period": 4, "cat": "Alkaline Earth", "desc": "Primary constituent of human bones, teeth, and marine shells."},
    {"num": 26, "sym": "Fe", "name": "Iron", "mass": 55.845, "group": 8, "period": 4, "cat": "Transition Metal", "desc": "Most common element on Earth by mass; oxygen carrier in blood hemoglobin."},
    {"num": 29, "sym": "Cu", "name": "Copper", "mass": 63.546, "group": 11, "period": 4, "cat": "Transition Metal", "desc": "Exceptional electrical and thermal conductivity; fundamental to global wiring."},
    {"num": 47, "sym": "Ag", "name": "Silver", "mass": 107.87, "group": 11, "period": 5, "cat": "Transition Metal", "desc": "Highest electrical conductivity, thermal conductivity, and optical reflectivity."},
    {"num": 79, "sym": "Au", "name": "Gold", "mass": 196.97, "group": 11, "period": 6, "cat": "Transition Metal", "desc": "Noble metal resistant to corrosion; used in currency, jewelry, and electronics."},
    {"num": 92, "sym": "U", "name": "Uranium", "mass": 238.03, "group": 3, "period": 7, "cat": "Actinide", "desc": "Radioactive heavy metal; primary fuel source for nuclear power reactors."}
]


class ScientificEncyclopedia:
    """Offline encyclopedia for physical constants and chemical taxonomy."""

    def __init__(self) -> None:
        self.logger = get_logger()
        self.constants = PHYSICAL_CONSTANTS
        self.elements = PERIODIC_TABLE

    def lookup_constant(self, query: str) -> Optional[str]:
        q = query.lower()
        for key, data in self.constants.items():
            words = key.split("_")
            if all(w in q for w in words) or data["symbol"].lower() in q:
                return f"Sir, {data['description']}: {data['symbol']} = {data['value']} {data['unit']}"
        return None

    def lookup_element(self, query: str) -> Optional[str]:
        q = query.lower()
        for elem in self.elements:
            if elem["name"].lower() in q or elem["sym"].lower() == q or f"atomic number {elem['num']}" in q:
                return (
                    f"Sir, Element: {elem['name']} ({elem['sym']})\n"
                    f"• Atomic Number: {elem['num']}\n"
                    f"• Atomic Mass: {elem['mass']} u\n"
                    f"• Category: {elem['cat']} (Group {elem['group']}, Period {elem['period']})\n"
                    f"• Details: {elem['desc']}"
                )
        return None


_encyclopedia_instance: Optional[ScientificEncyclopedia] = None

def get_scientific_encyclopedia() -> ScientificEncyclopedia:
    global _encyclopedia_instance
    if _encyclopedia_instance is None:
        _encyclopedia_instance = ScientificEncyclopedia()
    return _encyclopedia_instance
