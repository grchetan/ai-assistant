"""
================================================================================
            JARVIS IN-HOUSE OFFLINE KNOWLEDGE & FACT ENGINE
================================================================================
Comprehensive zero-dependency knowledge repository spanning Physics, Chemistry,
Biology, Computer Science, Astronomy, History, Geography, and Technology.
Provides fast local multi-hop entity matching, fact retrieval, and rich answers.
================================================================================
"""

import re
from typing import Dict, List, Optional, Tuple, Any
from jarvis.core.logger import get_logger

# ──────────────────────────────────────────────────────────────────────────────
# Comprehensive In-House Fact & Entity Graph Database
# ──────────────────────────────────────────────────────────────────────────────
KNOWLEDGE_CORPUS: List[Dict[str, Any]] = [
    # ─── PHYSICS & ASTRONOMY ───
    {
        "id": "phys_newton_laws",
        "keywords": ["newton law", "newtons laws", "motion laws", "newton ke niyam", "gati ke niyam"],
        "category": "Physics",
        "title": "Newton's Three Laws of Motion",
        "content": (
            "Newton ke teen gati ke niyam (Laws of Motion) hain, Sir:\n"
            "1. First Law (Inertia): Koi bhi object rest ya uniform motion me tab tak rehta hai jab tak koi external unbalanced force na lage.\n"
            "2. Second Law (Force): Force = mass × acceleration (F = ma). Yani momentum change ka rate applied force ke proportional hota hai.\n"
            "3. Third Law (Action-Reaction): Har action ka equal aur opposite reaction hota hai (Fa = -Fb)."
        )
    },
    {
        "id": "phys_relativity",
        "keywords": ["theory of relativity", "einstein relativity", "e=mc2", "general relativity", "special relativity", "kaal aur sthan"],
        "category": "Physics",
        "title": "Albert Einstein's Theory of Relativity",
        "content": (
            "Albert Einstein ne do relativity theories di thin, Sir:\n"
            "1. Special Relativity (1905): Speed of light (c ≈ 3×10^8 m/s) universe me constant hai aur universal speed limit hai. Isme mass-energy equivalence formula E = mc² diya gaya.\n"
            "2. General Relativity (1915): Gravity koi simple force nahi, balki mass dwara Spacetime curvature ka parinam hai. Heavy objects spacetime fabric ko curve karte hain."
        )
    },
    {
        "id": "phys_quantum_mechanics",
        "keywords": ["quantum mechanics", "quantum physics", "schrodinger", "heisenberg uncertainty", "quantum superposition"],
        "category": "Physics",
        "title": "Quantum Mechanics & Principles",
        "content": (
            "Quantum mechanics subatomic particles (electrons, photons, quarks) ke behavior ko describe karta hai:\n"
            "• Wave-Particle Duality: Light aur matter dono particle aur wave ki tarah behave karte hain (de Broglie hypothesis).\n"
            "• Heisenberg Uncertainty Principle: Kisi subatomic particle ki exact position aur exact momentum simultaneously measure karna mathematically impossible hai (Δx × Δp ≥ ħ/2).\n"
            "• Superposition: Particle ek saath multiple states me reh sakta hai jab tak use observe na kiya jaye (Schrödinger's Cat experiment).\n"
            "• Quantum Entanglement: Do particles itne closely linked hote hain ki ek ka state badalte hi dusre ka instant badal jata hai, chahe light-years door kyu na ho."
        )
    },
    {
        "id": "phys_black_holes",
        "keywords": ["black hole", "event horizon", "singularity", "hawking radiation", "black holes kya hote hain"],
        "category": "Astrophysics",
        "title": "Black Holes & Event Horizons",
        "content": (
            "Black Hole space me ek aisa region hai jahan gravitational force itna extreme hota hai ki light bhi escape nahi kar sakti:\n"
            "• Formation: Supermassive stars ke supernova collapse se bante hain.\n"
            "• Event Horizon: Wo boundary jiske andar jaane ke baad wapas aana impossible hai (point of no return).\n"
            "• Singularity: Center point jahan infinite density aur zero volume hota hai, jahan physics ke known laws break ho jate hain.\n"
            "• Hawking Radiation: Stephen Hawking ne prove kiya ki quantum fluctuations ki wajah se black holes gradually evaporate hote hain."
        )
    },
    {
        "id": "phys_thermodynamics",
        "keywords": ["thermodynamics", "laws of thermodynamics", "entropy", "absolute zero", "heat engine"],
        "category": "Physics",
        "title": "Laws of Thermodynamics",
        "content": (
            "Thermodynamics ke 4 mukhya niyam hain, Sir:\n"
            "• Zeroth Law: Agar A aur B thermal equilibrium me hain aur B aur C bhi hain, toh A aur C bhi equilibrium me honge (Temperature definition).\n"
            "• 1st Law (Energy Conservation): Energy create ya destroy nahi ki ja sakti, sirf ek form se dusre me convert hoti hai (ΔU = Q - W).\n"
            "• 2nd Law (Entropy): Isolated system ki total entropy hamesha badhti hai; heat spontaneously cold se hot body me flow nahi ho sakti.\n"
            "• 3rd Law (Absolute Zero): Jaise temperature absolute zero (0 Kelvin / -273.15°C) ke pass pahunchta hai, system ki entropy constant ho jati hai."
        )
    },
    {
        "id": "astro_solar_system",
        "keywords": ["solar system", "planets", "surya mandal", "grah", "mars", "jupiter", "sun"],
        "category": "Astronomy",
        "title": "Solar System Architecture",
        "content": (
            "Humara Solar System lagbhag 4.6 billion saal purana hai:\n"
            "• Sun: 99.86% solar system ka mass Sun me hai, powered by nuclear fusion (Hydrogen -> Helium).\n"
            "• 8 Planets: Mercury (sabse pass), Venus (sabse garam), Earth (life host), Mars (Red Planet), Jupiter (sabse bada gas giant), Saturn (spectacular rings), Uranus (ice giant), Neptune (sabse door gas giant).\n"
            "• Asteroid Belt: Mars aur Jupiter ke beech sthit hai.\n"
            "• Kuiper Belt & Oort Cloud: Solar system ke outer edge par jahan comets aur dwarf planets (Pluto) rehte hain."
        )
    },

    # ─── COMPUTER SCIENCE & ARCHITECTURE ───
    {
        "id": "cs_cpu_architecture",
        "keywords": ["cpu architecture", "how cpu works", "processor", "alu", "cache memory", "fetch decode execute"],
        "category": "Computer Science",
        "title": "CPU Architecture & Execution Cycle",
        "content": (
            "CPU (Central Processing Unit) computer ka brain hota hai, Sir:\n"
            "• Fetch-Decode-Execute Cycle: Program Counter se instruction fetch hoti hai, instruction decoder use decode karta hai, aur execution unit run karta hai.\n"
            "• Core Components:\n"
            "  1. ALU (Arithmetic Logic Unit): Math calculations aur logical comparisons karta hai.\n"
            "  2. Control Unit (CU): Components ke beech signals aur timing synchronize karta hai.\n"
            "  3. Registers: Ultra-fast onboard temporary storage (AX, BX, PC, SP).\n"
            "  4. Cache Levels: L1 (fastest, small), L2 (medium), L3 (shared, larger) jo RAM latency ko bypass karte hain."
        )
    },
    {
        "id": "cs_operating_systems",
        "keywords": ["operating system", "os concepts", "kernel", "virtual memory", "deadlock", "paging", "process scheduling"],
        "category": "Computer Science",
        "title": "Operating Systems & Kernel Concepts",
        "content": (
            "Operating System hardware aur software applications ke beech bridge hota hai:\n"
            "• Kernel: OS ka core component jo memory, CPU scheduling, aur devices ko control karta hai (Monolithic vs Microkernel).\n"
            "• Virtual Memory & Paging: RAM se bada virtual memory space simulate karta hai page tables aur disk swapping ke through.\n"
            "• Process vs Thread: Process ek independent executing program hai apni memory space ke saath; Thread usi process ke andar lightweight execution unit hai.\n"
            "• Deadlock: Situation jahan do processes ek dusre ke resources hold karke ek dusre ka wait karte hain (Mutual Exclusion, Hold & Wait, No Preemption, Circular Wait)."
        )
    },
    {
        "id": "cs_data_structures",
        "keywords": ["data structures", "array", "linked list", "binary tree", "graph", "hash table", "stack queue"],
        "category": "Computer Science",
        "title": "Core Data Structures & Complexity",
        "content": (
            "Important Data Structures aur unki average search complexities:\n"
            "• Array: Contiguous memory, direct index lookup O(1), search O(n).\n"
            "• Linked List: Dynamic memory nodes linked by pointers, insertion O(1), search O(n).\n"
            "• Stack & Queue: LIFO (Stack) aur FIFO (Queue) access patterns, push/pop O(1).\n"
            "• Hash Map / Hash Table: Key-value hashing, O(1) average lookup/insertion.\n"
            "• Binary Search Tree (BST) & AVL/Red-Black: Balanced tree lookup O(log n).\n"
            "• Graph: Vertices aur edges, represented via Adjacency Matrix ya Adjacency List."
        )
    },
    {
        "id": "cs_algorithms_big_o",
        "keywords": ["big o notation", "sorting algorithms", "quicksort", "mergesort", "binary search", "dijkstra"],
        "category": "Computer Science",
        "title": "Algorithms & Asymptotic Complexity",
        "content": (
            "Algorithms ki efficiency measure karne ke liye Big-O notation use hota hai:\n"
            "• O(1) Constant: Hash map lookup, array index read.\n"
            "• O(log n) Logarithmic: Binary search on sorted arrays.\n"
            "• O(n) Linear: Linear search, array traversal.\n"
            "• O(n log n) Linearithmic: MergeSort, QuickSort (average), HeapSort.\n"
            "• O(n²) Quadratic: Bubble Sort, Selection Sort, Insertion Sort.\n"
            "• O(2^n) Exponential: Recursive Fibonacci, subsets generation.\n"
            "• Dijkstra Algorithm: Shortest path in weighted graph using min-heap priority queue (O((V+E) log V))."
        )
    },
    {
        "id": "cs_cryptography",
        "keywords": ["cryptography", "encryption", "aes", "rsa", "hashing", "sha256", "public key"],
        "category": "Cybersecurity",
        "title": "Modern Cryptography & Security",
        "content": (
            "Data security aur privacy ke do mukhya encryption standards hain:\n"
            "• Symmetric Encryption (AES-256): Single shared secret key se encrypt aur decrypt dono hota hai. Fast aur efficient bulk data storage ke liye.\n"
            "• Asymmetric Encryption (RSA, ECC): Public key encrypt karne ke liye aur Private key decrypt karne ke liye use hoti hai. Digital signatures aur SSL/TLS handshake me use hoti hai.\n"
            "• Cryptographic Hashing (SHA-256): One-way mathematical function jo kisi bhi data ka fixed 256-bit hash banata hai. Irreversible aur collision-resistant."
        )
    },
    {
        "id": "cs_networking",
        "keywords": ["osi model", "tcp ip", "dns", "http https", "ip address", "networking protocols"],
        "category": "Computer Networks",
        "title": "Computer Networking & OSI 7-Layer Model",
        "content": (
            "OSI (Open Systems Interconnection) 7-Layer Model:\n"
            "1. Physical: Bits, cables, radio signals, NIC.\n"
            "2. Data Link: Frames, MAC address, Ethernet switches.\n"
            "3. Network: Packets, IP addressing, Routers.\n"
            "4. Transport: Segments, TCP (reliable connection-oriented) & UDP (fast connectionless).\n"
            "5. Session: Communication session management.\n"
            "6. Presentation: Encryption (TLS), Compression, Serialization.\n"
            "7. Application: HTTP/HTTPS, DNS, SSH, FTP, SMTP."
        )
    },

    # ─── CHEMISTRY & BIOLOGY ───
    {
        "id": "chem_periodic_table",
        "keywords": ["periodic table", "elements", "atomic number", "hydrogen", "carbon", "avogadro", "chemical bonds"],
        "category": "Chemistry",
        "title": "Periodic Table & Atomic Structure",
        "content": (
            "Periodic table me 118 elements atomic number (proton count) ke anusaar arrange hain:\n"
            "• Groups & Periods: 18 vertical columns (groups) aur 7 horizontal rows (periods).\n"
            "• Key Elements: Hydrogen (H, atomic #1, lightest), Carbon (C, #6, organic chemistry backbone), Oxygen (O, #8, respiration).\n"
            "• Chemical Bonding: Ionic bonding (electron transfer), Covalent bonding (electron sharing), Hydrogen bonding (dipole interaction).\n"
            "• Avogadro's Number: 1 mole = 6.022 × 10^23 atoms/molecules."
        )
    },
    {
        "id": "bio_dna_genetics",
        "keywords": ["dna", "rna", "genetics", "chromosomes", "mitochondria", "crispr", "cells"],
        "category": "Biology",
        "title": "DNA, RNA & Cellular Genetics",
        "content": (
            "Genetics aur cellular life ka core structure:\n"
            "• DNA (Deoxyribonucleic Acid): Double helix structure discovered by Watson & Crick. Base pairs: Adenine (A) - Thymine (T) aur Guanine (G) - Cytosine (C).\n"
            "• RNA (Ribonucleic Acid): Single-stranded molecule jo protein synthesis me genetic code translate karta hai (mRNA, tRNA, rRNA).\n"
            "• Human Genome: Manushya ke andar 23 pairs (total 46) chromosomes hote hain.\n"
            "• Mitochondria: 'Powerhouse of the cell', jo ATP (Adenosine Triphosphate) ke roop me cellular energy generate karta hai."
        )
    },

    # ─── WORLD HISTORY & CIVILIZATIONS ───
    {
        "id": "hist_world_wars",
        "keywords": ["world war 1", "world war 2", "hitler", "ww1", "ww2", "atomic bomb", "cold war"],
        "category": "History",
        "title": "The World Wars Overview",
        "content": (
            "20th Century ke do vishva yuddh:\n"
            "• World War I (1914 - 1918): Archduke Franz Ferdinand ke assassination se shuru hua. Allies vs Central Powers. 1919 me Treaty of Versailles ke sath end hua.\n"
            "• World War II (1939 - 1945): Germany ke Poland invasion se shuru hua. Axis Powers (Germany, Italy, Japan) vs Allied Powers (USA, USSR, UK, China). August 1945 me Hiroshima aur Nagasaki par atomic bombs giraye jaane ke baad end hua.\n"
            "• Consequence: United Nations (UN) ki sthapna aur USA-USSR Cold War ki shuruat hui."
        )
    },
    {
        "id": "hist_industrial_revolution",
        "keywords": ["industrial revolution", "steam engine", "james watt", "aadhunik kranti", "assembly line"],
        "category": "History",
        "title": "The Industrial Revolution",
        "content": (
            "Industrial Revolution 18th century ke mid me Britain se shuru hui:\n"
            "• 1st Industrial Revolution (1760-1840): Steam engine (James Watt), mechanized textile manufacturing, aur coal-powered railways.\n"
            "• 2nd Industrial Revolution (late 19th c.): Electricity, steel manufacturing, telegraph, aur assembly line mass production (Henry Ford).\n"
            "• 3rd & 4th Revolutions: Computing, automation, internet, aur ab AI/Quantum systems."
        )
    },
    {
        "id": "hist_india_independence",
        "keywords": ["india independence", "1947", "mahatma gandhi", "bhagat singh", "subhash chandra bose", "azadi"],
        "category": "History",
        "title": "Indian Independence Movement",
        "content": (
            "Bharat ki Azadi ka sangharsh:\n"
            "• 1857: First War of Independence (Mangal Pandey, Rani Lakshmibai).\n"
            "• Leaders: Mahatma Gandhi (Non-Violence, Salt Satyagraha, Quit India Movement), Netaji Subhash Chandra Bose (Azad Hind Fauj), Bhagat Singh, Sardar Vallabhbhai Patel, Dr. B.R. Ambedkar (Constitution Maker).\n"
            "• 15 August 1947: Bharat ne 200 saal ke British colonial rule se aazadi prapt ki.\n"
            "• 26 January 1950: Bharat ka Samvidhan lagu hua aur desh Republic bana."
        )
    },

    # ─── GEOGRAPHY & EARTH ───
    {
        "id": "geo_earth_facts",
        "keywords": ["earth facts", "mount everest", "pacific ocean", "continents", "prithvi", "atmosphere"],
        "category": "Geography",
        "title": "Earth Geography & Planetary Statistics",
        "content": (
            "Prithvi (Earth) ke pramukh geographical facts:\n"
            "• 7 Continents: Asia (sabse bada), Africa, North America, South America, Antarctica, Europe, Australia (sabse chhota).\n"
            "• 5 Oceans: Pacific Ocean (sabse bada aur gehra - Mariana Trench 11,034m), Atlantic, Indian, Southern, Arctic.\n"
            "• Highest Peak: Mount Everest (8,848.86 meters, Himalayas).\n"
            "• Atmosphere Layers: Troposphere (weather), Stratosphere (ozone layer), Mesosphere (meteors burn), Thermosphere (auroras, ISS), Exosphere."
        )
    },

    # ─── IRON MAN & J.A.R.V.I.S. LORE ───
    {
        "id": "lore_jarvis_origins",
        "keywords": ["who created jarvis", "tony stark", "arc reactor", "marvel jarvis", "what is jarvis", "jarvis full form"],
        "category": "JARVIS Lore",
        "title": "J.A.R.V.I.S. Architecture & Origins",
        "content": (
            "J.A.R.V.I.S. (Just A Rather Very Intelligent System):\n"
            "• Origin: Tony Stark dwara create kiya gaya ultra-advanced AI operating system, jo Edwin Jarvis (Howard Stark ke loyal butler) ke samman me naamit hai.\n"
            "• Core Functions: Stark Industries ke networks, Malibu mansion ki automation, Iron Man armor suits ki weapons/flight telemetry, aur tactical battlefield simulations ko real-time coordinate karta hai.\n"
            "• Voice: Original cinematic universe me Paul Bettany dwara voice kiya gaya.\n"
            "• Evolution: Baad me JARVIS ke neural core ko Mind Stone ke sath integrate karke 'Vision' me synthesize kiya gaya, aur unki jagah F.R.I.D.A.Y. ne li."
        )
    },
    {
        "id": "lore_arc_reactor",
        "keywords": ["arc reactor", "clean energy", "palladium", "vibranium", "tony stark chest"],
        "category": "JARVIS Lore",
        "title": "Arc Reactor Technology",
        "content": (
            "Arc Reactor Tony aur Howard Stark dwara viksit kiya gaya fusion energy source hai:\n"
            "• Function: Cold fusion reactor jo clean, limitless electrical energy produce karta hai.\n"
            "• Miniaturization: Tony Stark ne Afghanistan cave me palladium-based miniature Arc Reactor banaya, jo 3 gigajoules per second generate karta tha.\n"
            "• New Element: Baad me palladium poisoning se bachne ke liye Tony ne particle accelerator se ek naya synthetic element synthesize kiya jo unlimited output deta hai."
        )
    }
]


class KnowledgeEngine:
    """In-House multi-domain knowledge retrieval and fact extraction engine."""

    def __init__(self) -> None:
        self.logger = get_logger()
        self.corpus = KNOWLEDGE_CORPUS

    def search_knowledge(self, query: str) -> Optional[Dict[str, Any]]:
        """Find best matching knowledge item with multi-keyword scoring."""
        q = query.lower().strip()
        best_match = None
        highest_score = 0

        for item in self.corpus:
            score = 0
            # Direct keyword matches
            for kw in item["keywords"]:
                if kw in q:
                    score += 15 + len(kw)

            # Title word matches
            title_words = item["title"].lower().split()
            for tw in title_words:
                if len(tw) > 3 and tw in q:
                    score += 5

            if score > highest_score and score >= 12:
                highest_score = score
                best_match = item

        if best_match:
            self.logger.info(f"Knowledge match found: [{best_match['title']}] (score={highest_score})", "KNOWLEDGE")
        return best_match

    def answer_query(self, query: str) -> Optional[str]:
        """Produce rich formatted answer if knowledge exists."""
        match = self.search_knowledge(query)
        if match:
            return match["content"]
        return None


_engine_instance: Optional[KnowledgeEngine] = None

def get_knowledge_engine() -> KnowledgeEngine:
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = KnowledgeEngine()
    return _engine_instance
