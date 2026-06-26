import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional


class FileOrganizer:
    def __init__(self):
        self.rules = {
            "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".ico", ".tiff"],
            "Documents": [".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".md"],
            "Spreadsheets": [".xls", ".xlsx", ".csv", ".ods"],
            "Presentations": [".ppt", ".pptx", ".odp"],
            "Audio": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a"],
            "Video": [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm"],
            "Archives": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"],
            "Code": [".py", ".js", ".ts", ".jsx", ".tsx", ".html", ".css", ".scss",
                     ".json", ".xml", ".yaml", ".yml", ".toml", ".ini", ".cfg",
                     ".java", ".cpp", ".c", ".h", ".hpp", ".go", ".rs", ".rb",
                     ".php", ".swift", ".kt", ".sh", ".bat", ".ps1"],
            "Executables": [".exe", ".msi", ".app", ".dmg", ".deb", ".rpm"],
        }

    def organize(self, folder_path: str, preview: bool = False) -> Dict[str, Any]:
        target = Path(folder_path)
        if not target.exists() or not target.is_dir():
            return {"success": False, "error": f"Folder not found: {folder_path}"}
        summary = {}
        for file in target.iterdir():
            if file.is_file():
                ext = file.suffix.lower()
                category = self._categorize(ext)
                summary[category] = summary.get(category, 0) + 1
                if not preview:
                    dest = target / category
                    dest.mkdir(exist_ok=True)
                    try:
                        shutil.move(str(file), str(dest / file.name))
                    except Exception:
                        pass
        return {"success": True, "folder": folder_path, "preview": preview, "summary": summary, "total_files": sum(summary.values())}

    def organize_by_date(self, folder_path: str) -> Dict[str, Any]:
        target = Path(folder_path)
        if not target.exists():
            return {"success": False, "error": "Folder not found"}
        summary = {}
        for file in target.iterdir():
            if file.is_file():
                mtime = datetime.fromtimestamp(file.stat().st_mtime)
                date_folder = mtime.strftime("%Y-%m")
                dest = target / date_folder
                dest.mkdir(exist_ok=True)
                try:
                    shutil.move(str(file), str(dest / file.name))
                    summary[date_folder] = summary.get(date_folder, 0) + 1
                except Exception:
                    pass
        return {"success": True, "folder": folder_path, "summary": summary}

    def organize_by_size(self, folder_path: str) -> Dict[str, Any]:
        target = Path(folder_path)
        if not target.exists():
            return {"success": False, "error": "Folder not found"}
        size_rules = {"Small_1KB": 1024, "Medium_1MB": 1024**2, "Large_100MB": 100*1024**2}
        summary = {}
        for file in target.iterdir():
            if file.is_file():
                size = file.stat().st_size
                if size < 1024:
                    cat = "Tiny_1KB"
                elif size < 1024**2:
                    cat = "Small_1MB"
                elif size < 100*1024**2:
                    cat = "Medium_100MB"
                else:
                    cat = "Large_100MB+"
                dest = target / cat
                dest.mkdir(exist_ok=True)
                try:
                    shutil.move(str(file), str(dest / file.name))
                    summary[cat] = summary.get(cat, 0) + 1
                except Exception:
                    pass
        return {"success": True, "folder": folder_path, "summary": summary}

    def clean_empty_folders(self, folder_path: str) -> Dict[str, Any]:
        target = Path(folder_path)
        if not target.exists():
            return {"success": False, "error": "Folder not found"}
        removed = 0
        for root, dirs, files in os.walk(target, topdown=False):
            for d in dirs:
                dirpath = Path(root) / d
                try:
                    if not any(dirpath.iterdir()):
                        dirpath.rmdir()
                        removed += 1
                except Exception:
                    pass
        return {"success": True, "folder": folder_path, "removed": removed}

    def _categorize(self, ext: str) -> str:
        for category, exts in self.rules.items():
            if ext in exts:
                return category
        return "Others"


file_organizer = FileOrganizer()
