import os
import re

try:
    import PyPDF2
    HAS_PYPDF2 = True
except ImportError:
    HAS_PYPDF2 = False

try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False

try:
    import pdfminer
    HAS_PDFMINER = True
except ImportError:
    HAS_PDFMINER = False


class PDFReader:
    def __init__(self):
        self._backend = None
        self._detect_backend()

    def _detect_backend(self):
        if HAS_PDFPLUMBER:
            self._backend = "pdfplumber"
        elif HAS_PYPDF2:
            self._backend = "PyPDF2"
        elif HAS_PDFMINER:
            self._backend = "pdfminer"
        else:
            self._backend = None

    def read_text(self, filepath):
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")
        if self._backend == "pdfplumber":
            return self._read_pdfplumber(filepath)
        elif self._backend == "PyPDF2":
            return self._read_pypdf2(filepath)
        elif self._backend == "pdfminer":
            return self._read_pdfminer(filepath)
        else:
            raise NotImplementedError(
                "No PDF backend available. Install one: pip install pdfplumber or PyPDF2"
            )

    def _read_pdfplumber(self, filepath):
        import pdfplumber
        text = ""
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                text += page_text + "\n"
        return text.strip()

    def _read_pypdf2(self, filepath):
        with open(filepath, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            text = ""
            for page in reader.pages:
                page_text = page.extract_text() or ""
                text += page_text + "\n"
        return text.strip()

    def _read_pdfminer(self, filepath):
        from pdfminer.high_level import extract_text
        return extract_text(filepath).strip()

    def get_metadata(self, filepath):
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")
        if self._backend == "pdfplumber":
            import pdfplumber
            with pdfplumber.open(filepath) as pdf:
                meta = pdf.metadata or {}
                return {k: str(v) for k, v in meta.items()}
        elif self._backend == "PyPDF2":
            with open(filepath, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                meta = reader.metadata or {}
                return {k: str(v) for k, v in meta.items()}
        elif self._backend == "pdfminer":
            from pdfminer.pdfparser import PDFParser
            from pdfminer.pdfdocument import PDFDocument
            with open(filepath, "rb") as f:
                parser = PDFParser(f)
                doc = PDFDocument(parser)
                info = doc.info[0] if doc.info else {}
                return {k.decode() if isinstance(k, bytes) else k: str(v) for k, v in info.items()}
        else:
            raise NotImplementedError("No PDF backend available")

    def get_page_count(self, filepath):
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")
        if self._backend == "pdfplumber":
            import pdfplumber
            with pdfplumber.open(filepath) as pdf:
                return len(pdf.pages)
        elif self._backend == "PyPDF2":
            with open(filepath, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                return len(reader.pages)
        elif self._backend == "pdfminer":
            from pdfminer.pdfparser import PDFParser
            from pdfminer.pdfdocument import PDFDocument
            with open(filepath, "rb") as f:
                parser = PDFParser(f)
                doc = PDFDocument(parser)
                return len(list(doc.get_pages()))
        else:
            raise NotImplementedError("No PDF backend available")

    def search_text(self, filepath, query):
        text = self.read_text(filepath)
        matches = []
        for i, line in enumerate(text.split("\n"), 1):
            if query.lower() in line.lower():
                matches.append({"line": i, "text": line.strip()})
        return matches

    def extract_tables(self, filepath):
        if self._backend != "pdfplumber":
            raise NotImplementedError("Table extraction requires pdfplumber: pip install pdfplumber")
        import pdfplumber
        tables = []
        with pdfplumber.open(filepath) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                page_tables = page.extract_tables()
                for table in page_tables:
                    tables.append({"page": page_num, "data": table})
        return tables
