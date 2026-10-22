"""
================================================================================
                    JARVIS KNOWLEDGE GRAPH & ONTOLOGY ENGINE
================================================================================
Directed relational graph capturing semantic connections between entities:
  - Users, Projects, Hardware, Preferences, Tools, and Events
  - Relation traversal, neighbor queries, and graph reasoning
================================================================================
"""

import json
from typing import Dict, List, Set, Any, Optional, Tuple
from collections import deque
from pathlib import Path

from jarvis.core.logger import get_logger

GRAPH_FILE = Path(__file__).resolve().parent.parent / "data" / "knowledge_graph.json"


class EntityNode:
    """Represents a discrete node entity in the knowledge graph."""

    def __init__(self, name: str, entity_type: str, properties: Optional[Dict[str, Any]] = None) -> None:
        self.name = name.strip()
        self.type = entity_type.upper().strip()
        self.properties = properties or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "type": self.type,
            "properties": self.properties
        }


class RelationEdge:
    """Represents a directed relationship from source entity to target entity."""

    def __init__(self, source: str, relation: str, target: str, weight: float = 1.0) -> None:
        self.source = source.strip()
        self.relation = relation.upper().strip()
        self.target = target.strip()
        self.weight = weight

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "relation": self.relation,
            "target": self.target,
            "weight": self.weight
        }


class KnowledgeGraph:
    """Directed multi-relational semantic graph store."""

    def __init__(self) -> None:
        self.logger = get_logger()
        self.nodes: Dict[str, EntityNode] = {}
        self.edges: List[RelationEdge] = []
        self._load()

    def add_entity(self, name: str, entity_type: str = "CONCEPT", properties: Optional[Dict[str, Any]] = None) -> EntityNode:
        key = name.lower().strip()
        if key not in self.nodes:
            node = EntityNode(name, entity_type, properties)
            self.nodes[key] = node
            return node
        return self.nodes[key]

    def add_relation(self, source_name: str, relation_type: str, target_name: str, weight: float = 1.0) -> None:
        s_key = source_name.lower().strip()
        t_key = target_name.lower().strip()

        # Ensure endpoints exist
        self.add_entity(source_name)
        self.add_entity(target_name)

        edge = RelationEdge(s_key, relation_type, t_key, weight)
        self.edges.append(edge)
        self._save()

    def get_related_entities(self, entity_name: str, relation_filter: Optional[str] = None) -> List[Tuple[str, str]]:
        """
        Find all outgoing connected entities.
        Returns: [(relation, target_name), ...]
        """
        key = entity_name.lower().strip()
        results = []
        for e in self.edges:
            if e.source == key:
                if relation_filter is None or e.relation == relation_filter.upper():
                    target_node = self.nodes.get(e.target)
                    t_name = target_node.name if target_node else e.target
                    results.append((e.relation, t_name))
        return results

    def find_path(self, start_entity: str, end_entity: str) -> Optional[List[str]]:
        """Breadth-first search for shortest relational path."""
        start_key = start_entity.lower().strip()
        end_key = end_entity.lower().strip()

        if start_key not in self.nodes or end_key not in self.nodes:
            return None

        queue = deque([[start_key]])
        visited = {start_key}

        while queue:
            path = queue.popleft()
            curr = path[-1]

            if curr == end_key:
                return [self.nodes[k].name for k in path]

            for e in self.edges:
                if e.source == curr and e.target not in visited:
                    visited.add(e.target)
                    new_path = list(path)
                    new_path.append(e.target)
                    queue.append(new_path)

        return None

    def _save(self) -> None:
        try:
            data = {
                "nodes": [n.to_dict() for n in self.nodes.values()],
                "edges": [e.to_dict() for e in self.edges]
            }
            with open(GRAPH_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass

    def _load(self) -> None:
        if GRAPH_FILE.exists():
            try:
                with open(GRAPH_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for n in data.get("nodes", []):
                    self.add_entity(n["name"], n["type"], n.get("properties"))
                for e in data.get("edges", []):
                    self.add_relation(e["source"], e["relation"], e["target"], e.get("weight", 1.0))
            except Exception:
                pass


def get_knowledge_graph() -> KnowledgeGraph:
    return KnowledgeGraph()
