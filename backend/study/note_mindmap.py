import json
import re
from datetime import datetime


class NoteMindmap:
    def __init__(self):
        self.mindmaps = {}
        self.next_id = 1

    def create_mindmap(self, title, notes_text, central_topic=None):
        if not title or not notes_text:
            raise ValueError("title and notes_text are required")
        mindmap_id = self.next_id
        self.next_id += 1
        structure = self._parse_notes_to_structure(notes_text, central_topic or title)
        self.mindmaps[mindmap_id] = {
            "id": mindmap_id,
            "title": title,
            "central_topic": central_topic or title,
            "notes_text": notes_text,
            "structure": structure,
            "created": datetime.now().isoformat(),
            "updated": datetime.now().isoformat(),
        }
        return mindmap_id

    def _parse_notes_to_structure(self, text, central_topic):
        lines = text.strip().split("\n")
        nodes = {}
        edges = []
        node_id_counter = [0]

        def add_node(label, parent_id=None, level=0):
            node_id_counter[0] += 1
            nid = f"n{node_id_counter[0]}"
            nodes[nid] = {
                "id": nid,
                "label": label.strip(),
                "level": level,
            }
            if parent_id:
                edges.append({"source": parent_id, "target": nid})
            return nid

        root_id = add_node(central_topic)
        stack = [(root_id, 0)]
        prev_level = 0
        prev_id = root_id

        for line in lines:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            indent = len(line) - len(line.lstrip())
            level = indent // 2 if indent > 0 else 1
            if level < 1:
                level = 1
            label = re.sub(r"^[-*•]\s*", "", stripped)
            label = re.sub(r"^\d+[.)]\s*", "", label)
            while stack and stack[-1][1] >= level:
                stack.pop()
            parent_id = stack[-1][0] if stack else root_id
            nid = add_node(label, parent_id, level)
            stack.append((nid, level))
            prev_id = nid
            prev_level = level

        return {"nodes": nodes, "edges": edges, "root": root_id}

    def get_mindmap(self, mindmap_id):
        if mindmap_id not in self.mindmaps:
            raise KeyError(f"Mindmap '{mindmap_id}' not found")
        return self.mindmaps[mindmap_id]

    def update_mindmap(self, mindmap_id, notes_text=None, title=None):
        if mindmap_id not in self.mindmaps:
            raise KeyError(f"Mindmap '{mindmap_id}' not found")
        mm = self.mindmaps[mindmap_id]
        if title:
            mm["title"] = title
        if notes_text:
            mm["notes_text"] = notes_text
            mm["structure"] = self._parse_notes_to_structure(notes_text, mm["central_topic"])
        mm["updated"] = datetime.now().isoformat()
        return mm

    def delete_mindmap(self, mindmap_id):
        if mindmap_id not in self.mindmaps:
            raise KeyError(f"Mindmap '{mindmap_id}' not found")
        del self.mindmaps[mindmap_id]

    def list_mindmaps(self):
        return [
            {"id": mm["id"], "title": mm["title"], "created": mm["created"]}
            for mm in self.mindmaps.values()
        ]

    def search_mindmaps(self, query):
        q = query.lower()
        return [
            mm for mm in self.mindmaps.values()
            if q in mm["title"].lower() or q in mm["notes_text"].lower()
        ]

    def to_dict(self, mindmap_id):
        if mindmap_id not in self.mindmaps:
            raise KeyError(f"Mindmap '{mindmap_id}' not found")
        return self.mindmaps[mindmap_id]

    def to_json(self, mindmap_id):
        return json.dumps(self.to_dict(mindmap_id), indent=2)

    def get_node_count(self, mindmap_id):
        if mindmap_id not in self.mindmaps:
            raise KeyError(f"Mindmap '{mindmap_id}' not found")
        return len(self.mindmaps[mindmap_id]["structure"]["nodes"])
