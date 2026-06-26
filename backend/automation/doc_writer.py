import json
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

import config
from backend.core.ai_engine import ai_engine


class DocWriter:
    def __init__(self):
        self.docs_dir = config.DOWNLOADS_DIR / "documents"
        self.docs_dir.mkdir(parents=True, exist_ok=True)

    def generate(self, topic: str, doc_type: str = "general", tone: str = "professional",
                 word_count: int = 500) -> Dict[str, Any]:
        prompt = f"""Write a {tone} {doc_type} document about '{topic}'.
Target length: around {word_count} words.
Format it with clear sections, headings, and paragraphs.
Use proper {doc_type} structure and professional language."""
        try:
            content = ai_engine.chat(prompt)
            if not content:
                content = f"# {topic}\n\nThis is a {tone} {doc_type} document about {topic}."
        except Exception:
            content = f"# {topic}\n\nGenerated document could not be created."
        filename = f"{doc_type}_{topic[:30]}_{datetime.now():%Y%m%d_%H%M%S}.md"
        safe_name = "".join(c if c.isalnum() or c in "._- " else "_" for c in filename)
        filepath = self.docs_dir / safe_name
        filepath.write_text(content.strip(), encoding="utf-8")
        meta = {
            "topic": topic,
            "type": doc_type,
            "tone": tone,
            "word_count": len(content.split()),
            "filename": safe_name,
            "created_at": datetime.now().isoformat(),
        }
        meta_path = filepath.with_suffix(".meta.json")
        meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
        return {"success": True, "filename": safe_name, "path": str(filepath), "word_count": meta["word_count"], "content": content.strip()}

    def summarize(self, content: str, max_length: int = 200) -> Dict[str, Any]:
        try:
            prompt = f"Summarize the following text in {max_length} words or less:\n\n{content[:3000]}"
            summary = ai_engine.chat(prompt)
        except Exception:
            summary = content[:max_length] + "..." if len(content) > max_length else content
        return {"success": True, "summary": summary, "original_length": len(content), "summary_length": len(summary)}

    def list_documents(self) -> Dict[str, Any]:
        files = []
        for f in sorted(self.docs_dir.glob("*.md"), key=lambda x: x.stat().st_mtime, reverse=True):
            meta_file = f.with_suffix(".meta.json")
            meta = {}
            if meta_file.exists():
                try:
                    meta = json.loads(meta_file.read_text(encoding="utf-8"))
                except Exception:
                    pass
            files.append({
                "name": f.name,
                "size": f.stat().st_size,
                "modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat(),
                "meta": meta,
            })
        return {"success": True, "files": files, "count": len(files)}


doc_writer = DocWriter()
