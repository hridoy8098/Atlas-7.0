import json
from datetime import datetime


class CitationGenerator:
    def __init__(self):
        self.sources = {}
        self.styles = {"apa", "mla", "chicago", "ieee"}

    def add_source(self, source_id, title, author, year, publisher=None, url=None, volume=None, issue=None, pages=None, edition=None, doi=None):
        if not source_id or not title or not author or not year:
            raise ValueError("source_id, title, author, and year are required")
        self.sources[source_id] = {
            "title": title,
            "author": author,
            "year": year,
            "publisher": publisher,
            "url": url,
            "volume": volume,
            "issue": issue,
            "pages": pages,
            "edition": edition,
            "doi": doi,
        }
        return True

    def get_source(self, source_id):
        if source_id not in self.sources:
            raise KeyError(f"Source '{source_id}' not found")
        return self.sources[source_id]

    def remove_source(self, source_id):
        if source_id not in self.sources:
            raise KeyError(f"Source '{source_id}' not found")
        del self.sources[source_id]

    def list_sources(self):
        return list(self.sources.keys())

    def _format_authors(self, authors):
        parts = [a.strip() for a in authors.split(",")]
        if len(parts) == 1:
            return parts[0]
        elif len(parts) == 2:
            return f"{parts[0]} and {parts[1]}"
        else:
            return ", ".join(parts[:-1]) + f", and {parts[-1]}"

    def _format_apa(self, source):
        a = self.sources[source]
        author = self._format_authors(a["author"])
        year = a["year"]
        title = a["title"]
        pub = a["publisher"]
        doi = a["doi"]
        if doi:
            return f'{author} ({year}). {title}. {pub}. https://doi.org/{doi}'
        return f'{author} ({year}). {title}. {pub}.'

    def _format_mla(self, source):
        a = self.sources[source]
        author = a["author"]
        title = a["title"]
        pub = a["publisher"]
        year = a["year"]
        url = a["url"]
        parts = [f'{author}. "{title}." {pub}, {year}.']
        if url:
            parts.append(url)
        return " ".join(parts)

    def _format_chicago(self, source):
        a = self.sources[source]
        author = a["author"]
        title = a["title"]
        pub = a["publisher"]
        year = a["year"]
        url = a["url"]
        parts = [f'{author}. {title}. {pub}, {year}.']
        if url:
            parts.append(url)
        return " ".join(parts)

    def _format_ieee(self, source):
        a = self.sources[source]
        author_initials = "".join([p.split()[-1][0] + ". " + " ".join(p.split()[:-1]) for p in a["author"].split(",")])
        title = a["title"]
        pub = a["publisher"]
        year = a["year"]
        return f'{author_initials}, "{title}" {pub}, {year}.'

    def generate(self, source_id, style="apa"):
        if style not in self.styles:
            raise ValueError(f"Unsupported style '{style}'. Choose from {self.styles}")
        if source_id not in self.sources:
            raise KeyError(f"Source '{source_id}' not found")
        formatters = {
            "apa": self._format_apa,
            "mla": self._format_mla,
            "chicago": self._format_chicago,
            "ieee": self._format_ieee,
        }
        return formatters[style](source_id)

    def generate_bibliography(self, style="apa", source_ids=None):
        if style not in self.styles:
            raise ValueError(f"Unsupported style '{style}'")
        ids = source_ids if source_ids else list(self.sources.keys())
        return [self.generate(sid, style) for sid in ids]

    def export_json(self, filepath):
        with open(filepath, "w") as f:
            json.dump(self.sources, f, indent=2)

    def import_json(self, filepath):
        with open(filepath, "r") as f:
            data = json.load(f)
        self.sources.update(data)
