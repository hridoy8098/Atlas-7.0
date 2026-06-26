# backend/agent/file_agent.py — Atlas 6.0 File Operations

import os
import shutil
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict

from .base_agent import BaseAgent


class FileAgent(BaseAgent):
    """File and folder operations"""
    
    def __init__(self):
        super().__init__(name="File Agent", description="File and folder operations")
        self.home = Path.home()
        self.downloads = self.home / "Downloads"
        self.documents = self.home / "Documents"
        self.desktop = self.home / "Desktop"
    
    # ===== FILE OPERATIONS =====
    
    def create_file(self, path: str, content: str = "") -> bool:
        """Create new file"""
        try:
            filepath = Path(path)
            filepath.parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"📄 Created: {filepath}")
            return True
        except Exception as e:
            print(f"❌ Create error: {e}")
            return False
    
    def read_file(self, path: str) -> Optional[str]:
        """Read file content"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except:
            return None
    
    def delete_file(self, path: str) -> bool:
        """Delete file"""
        try:
            os.remove(path)
            print(f"🗑️ Deleted: {path}")
            return True
        except:
            return False
    
    def move_file(self, src: str, dst: str) -> bool:
        """Move file"""
        try:
            shutil.move(src, dst)
            print(f"📦 Moved: {src} → {dst}")
            return True
        except:
            return False
    
    def copy_file(self, src: str, dst: str) -> bool:
        """Copy file"""
        try:
            shutil.copy2(src, dst)
            print(f"📋 Copied: {src} → {dst}")
            return True
        except:
            return False
    
    def rename_file(self, path: str, new_name: str) -> bool:
        """Rename file"""
        try:
            filepath = Path(path)
            new_path = filepath.parent / new_name
            filepath.rename(new_path)
            print(f"✏️ Renamed: {filepath.name} → {new_name}")
            return True
        except:
            return False
    
    # ===== FOLDER OPERATIONS =====
    
    def create_folder(self, path: str) -> bool:
        """Create folder"""
        try:
            os.makedirs(path, exist_ok=True)
            print(f"📁 Created folder: {path}")
            return True
        except:
            return False
    
    def delete_folder(self, path: str) -> bool:
        """Delete folder"""
        try:
            shutil.rmtree(path)
            print(f"🗑️ Deleted folder: {path}")
            return True
        except:
            return False
    
    def list_folder(self, path: str = None) -> List[Dict]:
        """List folder contents"""
        path = path or str(self.home)
        items = []
        
        try:
            for item in Path(path).iterdir():
                stat = item.stat()
                items.append({
                    "name": item.name,
                    "type": "folder" if item.is_dir() else "file",
                    "size": stat.st_size if item.is_file() else 0,
                    "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
                })
        except:
            pass
        
        return sorted(items, key=lambda x: (x['type'], x['name']))
    
    def search_files(self, query: str, directory: str = None) -> List[str]:
        """Search files by name"""
        directory = directory or str(self.home)
        results = []
        
        try:
            for root, dirs, files in os.walk(directory):
                for name in files + dirs:
                    if query.lower() in name.lower():
                        results.append(os.path.join(root, name))
                if len(results) > 50:
                    break
        except:
            pass
        
        return results[:20]
    
    def get_file_info(self, path: str) -> Optional[Dict]:
        """Get file details"""
        try:
            stat = os.stat(path)
            return {
                "name": Path(path).name,
                "size": stat.st_size,
                "size_human": self._human_size(stat.st_size),
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
            }
        except:
            return None
    
    # ===== ORGANIZE =====
    
    def organize_downloads(self) -> Dict:
        """Organize Downloads folder by file type"""
        categories = {
            "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp"],
            "Documents": [".pdf", ".doc", ".docx", ".txt", ".xls", ".xlsx", ".ppt", ".pptx"],
            "Audio": [".mp3", ".wav", ".flac", ".aac", ".ogg"],
            "Video": [".mp4", ".avi", ".mkv", ".mov", ".wmv"],
            "Archives": [".zip", ".rar", ".7z", ".tar", ".gz"],
            "Code": [".py", ".js", ".html", ".css", ".json", ".xml", ".java", ".cpp"],
            "Others": []
        }
        
        result = {}
        downloads = str(self.downloads)
        
        for file in Path(downloads).iterdir():
            if file.is_file():
                ext = file.suffix.lower()
                category = "Others"
                for cat, exts in categories.items():
                    if ext in exts:
                        category = cat
                        break
                
                dest_dir = Path(downloads) / category
                dest_dir.mkdir(exist_ok=True)
                
                try:
                    shutil.move(str(file), str(dest_dir / file.name))
                    result[category] = result.get(category, 0) + 1
                except:
                    pass
        
        print(f"📦 Organized downloads: {result}")
        return result
    
    def get_capabilities(self):
        return ["file_organize", "file_search", "file_create", "file_delete", "file_copy", "file_move", "file_rename", "file_backup"]

    def handle(self, intent: str, entities: Dict) -> Dict:
        cmd = entities.get("original_command", "").lower()
        path = entities.get("path", entities.get("folder", ""))
        query = entities.get("query", "")
        if "organize" in intent or "organize" in cmd or "গোছাও" in cmd:
            folder = path or str(self.downloads)
            result = self.organize_downloads()
            return {"success": True, "message": f"Organized {folder}", "details": result}
        if "search" in intent or "find" in cmd or "search" in cmd or "খুঁজ" in cmd:
            results = self.search_files(query or cmd)
            return {"success": True, "results": results, "count": len(results)}
        if "create" in intent or "new" in cmd or "create" in cmd or "তৈরি" in cmd:
            name = entities.get("name", query or "new_file.txt")
            content = entities.get("content", "")
            success = self.create_file(name, content)
            return {"success": success, "file": name, "message": f"Created {name}" if success else "Failed to create"}
        if "delete" in intent or "delete" in cmd or "remove" in cmd or "মুছ" in cmd:
            success = self.delete_file(path or query)
            return {"success": success, "message": f"Deleted {path or query}" if success else "Failed to delete"}
        if "copy" in intent or "copy" in cmd or "কপি" in cmd:
            dst = entities.get("destination", "")
            success = self.copy_file(path, dst)
            return {"success": success, "message": f"Copied to {dst}" if success else "Failed to copy"}
        if "move" in intent or "move" in cmd or "সরাও" in cmd:
            dst = entities.get("destination", "")
            success = self.move_file(path, dst)
            return {"success": success, "message": f"Moved to {dst}" if success else "Failed to move"}
        if "rename" in intent or "rename" in cmd or "নাম" in cmd:
            new_name = entities.get("new_name", query)
            success = self.rename_file(path, new_name)
            return {"success": success, "message": f"Renamed to {new_name}" if success else "Failed to rename"}
        if "backup" in intent or "backup" in cmd or "ব্যাকআপ" in cmd:
            return {"success": True, "message": "Backup feature coming soon"}
        files = self.list_folder(path or str(self.home))
        return {"success": True, "files": files}

    # ===== HELPERS =====
    
    def _human_size(self, size: int) -> str:
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} PB"
    
    def get_disk_usage(self, path: str = "/") -> Dict:
        """Get disk usage"""
        try:
            import shutil
            usage = shutil.disk_usage(path)
            return {
                "total": self._human_size(usage.total),
                "used": self._human_size(usage.used),
                "free": self._human_size(usage.free),
                "percent": round(usage.used / usage.total * 100, 1)
            }
        except:
            return {}


# Singleton
file_agent = FileAgent()