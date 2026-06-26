"""Read and interpret diagrams/flowcharts (basic structure)."""

import re


class DiagramReader:
    """Parse and interpret diagrams and flowcharts from text/graph descriptions."""

    def __init__(self):
        self.nodes = []
        self.edges = []
        self.recognized_shapes = {"rect", "diamond", "circle", "arrow", "parallelogram"}

    def load_text(self, text: str) -> None:
        if not isinstance(text, str):
            raise TypeError("text must be a string")
        self._parse_text(text)

    def _parse_text(self, text: str) -> None:
        lines = text.strip().splitlines()
        for line in lines:
            if "-->" in line or "->" in line:
                parts = re.split(r"-+>", line)
                src = parts[0].strip()
                dst = parts[1].strip() if len(parts) > 1 else ""
                if src and dst:
                    self.edges.append({"from": src, "to": dst})
            elif line.strip():
                label = line.strip()
                shape = self._infer_shape(label)
                self.nodes.append({"id": label, "shape": shape, "text": label})

    def _infer_shape(self, text: str) -> str:
        lower = text.lower()
        if any(w in lower for w in ("decision", "if", "?", "choose", "check")):
            return "diamond"
        if any(w in lower for w in ("start", "begin", "end", "stop")):
            return "circle"
        if any(w in lower for w in ("input", "output", "read", "print", "display")):
            return "parallelogram"
        return "rect"

    def get_flow(self) -> list:
        return [
            {"step": n["id"], "shape": n["shape"], "text": n["text"]}
            for n in self.nodes
        ]

    def find_loops(self) -> list:
        loops = []
        for i, edge in enumerate(self.edges):
            for other in self.edges[i + 1:]:
                if edge["to"] == other["from"] and other["to"] == edge["from"]:
                    loops.append({"nodes": [edge["from"], edge["to"]], "type": "cycle"})
        return loops

    def summarize(self) -> dict:
        return {
            "node_count": len(self.nodes),
            "edge_count": len(self.edges),
            "flow": self.get_flow(),
            "loops": self.find_loops(),
        }

    def to_mermaid(self) -> str:
        lines = ["flowchart TD"]
        for node in self.nodes:
            sid = node["id"].replace(" ", "_")
            shape = node["shape"]
            if shape == "diamond":
                lines.append(f"    {sid}{{{{{node['id']}}}}}")
            elif shape == "circle":
                lines.append(f"    {sid}(({node['id']}))")
            elif shape == "parallelogram":
                lines.append(f"    {sid}[/{node['id']}/]")
            else:
                lines.append(f"    {sid}[{node['id']}]")
        for edge in self.edges:
            src = edge["from"].replace(" ", "_")
            dst = edge["to"].replace(" ", "_")
            lines.append(f"    {src} --> {dst}")
        return "\n".join(lines)
