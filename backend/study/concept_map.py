import json


class ConceptMap:
    def __init__(self):
        self.nodes = {}
        self.edges = []
        self.metadata = {"title": "", "description": "", "created": None}

    def add_concept(self, concept_id, label, description="", color=None, shape=None):
        if not concept_id or not label:
            raise ValueError("concept_id and label are required")
        if concept_id in self.nodes:
            raise ValueError(f"Concept '{concept_id}' already exists")
        self.nodes[concept_id] = {
            "id": concept_id,
            "label": label,
            "description": description,
            "color": color or "#4A90D9",
            "shape": shape or "box",
        }
        return True

    def remove_concept(self, concept_id):
        if concept_id not in self.nodes:
            raise KeyError(f"Concept '{concept_id}' not found")
        del self.nodes[concept_id]
        self.edges = [
            e for e in self.edges
            if e["source"] != concept_id and e["target"] != concept_id
        ]

    def add_relationship(self, source_id, target_id, relationship_type="related"):
        if source_id not in self.nodes:
            raise KeyError(f"Source concept '{source_id}' not found")
        if target_id not in self.nodes:
            raise KeyError(f"Target concept '{target_id}' not found")
        self.edges.append({
            "source": source_id,
            "target": target_id,
            "type": relationship_type,
            "id": f"{source_id}--{target_id}",
        })
        return True

    def remove_relationship(self, source_id, target_id):
        before = len(self.edges)
        self.edges = [
            e for e in self.edges
            if not (e["source"] == source_id and e["target"] == target_id)
        ]
        if len(self.edges) == before:
            raise ValueError(f"No relationship found between '{source_id}' and '{target_id}'")

    def get_concept(self, concept_id):
        if concept_id not in self.nodes:
            raise KeyError(f"Concept '{concept_id}' not found")
        relationships = [
            e for e in self.edges
            if e["source"] == concept_id or e["target"] == concept_id
        ]
        return {"node": self.nodes[concept_id], "relationships": relationships}

    def search_concepts(self, query):
        q = query.lower()
        return [
            n for n in self.nodes.values()
            if q in n["label"].lower() or q in n["description"].lower()
        ]

    def to_dict(self):
        return {
            "metadata": self.metadata,
            "nodes": list(self.nodes.values()),
            "edges": self.edges,
        }

    def to_json(self):
        return json.dumps(self.to_dict(), indent=2)

    def from_dict(self, data):
        self.metadata = data.get("metadata", self.metadata)
        self.nodes = {n["id"]: n for n in data.get("nodes", [])}
        self.edges = data.get("edges", [])

    def from_json(self, json_str):
        self.from_dict(json.loads(json_str))

    def get_connected_concepts(self, concept_id):
        if concept_id not in self.nodes:
            raise KeyError(f"Concept '{concept_id}' not found")
        connected = set()
        for e in self.edges:
            if e["source"] == concept_id:
                connected.add(e["target"])
            if e["target"] == concept_id:
                connected.add(e["source"])
        return [self.nodes[cid] for cid in connected if cid in self.nodes]
