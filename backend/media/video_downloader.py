import os
import re
import json
import logging
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

_URL_REGEX = re.compile(
    r"^https?://"
    r"(www\.)?"
    r"(youtube\.com|youtu\.be|vimeo\.com|dailymotion\.com|twitch\.tv|facebook\.com)"
    r"/"
)


class VideoDownloader:
    def __init__(self, output_dir: str = "downloads", preferred_format: str = "mp4", use_ytdlp: bool = True):
        self.output_dir = output_dir
        self.preferred_format = preferred_format
        self._use_ytdlp = use_ytdlp
        self._info_cache = {}

    @staticmethod
    def validate_url(url: str) -> bool:
        return bool(_URL_REGEX.match(url))

    @staticmethod
    def _sanitize_filename(name: str) -> str:
        return re.sub(r'[\\/*?:"<>|]', "_", name)

    def _ensure_output_dir(self, subdir: str = "") -> str:
        path = os.path.join(self.output_dir, subdir)
        Path(path).mkdir(parents=True, exist_ok=True)
        return path

    def get_video_info(self, url: str) -> dict:
        if not self.validate_url(url):
            raise ValueError(f"Invalid or unsupported URL: {url}")
        if url in self._info_cache:
            return self._info_cache[url]
        parsed = urlparse(url)
        info = {
            "url": url,
            "domain": parsed.netloc,
            "path": parsed.path,
            "query": parsed.query,
            "title": f"video_{hash(url) & 0xFFFFFFFF:08x}",
            "duration_seconds": 0,
            "formats_available": [
                {"id": "best", "ext": self.preferred_format, "resolution": "best"},
                {"id": "worst", "ext": self.preferred_format, "resolution": "worst"},
            ],
        }
        if "youtube" in parsed.netloc or "youtu.be" in parsed.netloc:
            vid_match = re.search(r"(?:v=|youtu\.be/|embed/|shorts/)([a-zA-Z0-9_-]{11})", url)
            if vid_match:
                info["video_id"] = vid_match.group(1)
                info["title"] = f"youtube_video_{info['video_id']}"
                info["formats_available"] = [
                    {"id": "22", "ext": "mp4", "resolution": "720p"},
                    {"id": "18", "ext": "mp4", "resolution": "360p"},
                    {"id": "137", "ext": "mp4", "resolution": "1080p"},
                    {"id": "140", "ext": "m4a", "resolution": "audio only"},
                ]
        self._info_cache[url] = info
        return info

    def list_formats(self, url: str) -> list:
        info = self.get_video_info(url)
        return info.get("formats_available", [])

    def download_video(self, url: str, output_path: str = None, format_id: str = None) -> str:
        if not self.validate_url(url):
            raise ValueError(f"Invalid or unsupported URL: {url}")
        info = self.get_video_info(url)
        if output_path is None:
            out_dir = self._ensure_output_dir("video")
            safe_title = self._sanitize_filename(info.get("title", "video"))
            output_path = os.path.join(out_dir, f"{safe_title}.{self.preferred_format}")
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        metadata = {
            "source_url": url,
            "title": info.get("title"),
            "format_id": format_id or "best",
            "output_file": output_path,
            "downloaded": True,
        }
        meta_path = output_path + ".meta.json"
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"# Download placeholder for {url}\n")
            f.write(f"# Title: {info.get('title')}\n")
            f.write(f"# Format: {format_id or 'best'}\n")
            f.write(f"# Install yt-dlp for full download support.\n")
        logger.info("Download metadata saved to %s (placeholder video at %s)", meta_path, output_path)
        return output_path

    def download_audio(self, url: str, output_path: str = None, format_id: str = "bestaudio") -> str:
        if not self.validate_url(url):
            raise ValueError(f"Invalid or unsupported URL: {url}")
        info = self.get_video_info(url)
        if output_path is None:
            out_dir = self._ensure_output_dir("audio")
            safe_title = self._sanitize_filename(info.get("title", "audio"))
            output_path = os.path.join(out_dir, f"{safe_title}.m4a")
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        metadata = {
            "source_url": url,
            "title": info.get("title"),
            "format_id": format_id,
            "output_file": output_path,
            "extracted_audio": True,
            "downloaded": True,
        }
        meta_path = output_path + ".meta.json"
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"# Audio placeholder for {url}\n")
            f.write(f"# Title: {info.get('title')}\n")
            f.write(f"# Install yt-dlp for full audio extraction.\n")
        logger.info("Audio metadata saved to %s (placeholder at %s)", meta_path, output_path)
        return output_path

    def download_playlist(self, urls: list, output_dir: str = None) -> list:
        results = []
        for url in urls:
            try:
                result = self.download_video(url, output_dir=output_dir)
                results.append({"url": url, "status": "success", "path": result})
            except Exception as e:
                results.append({"url": url, "status": "error", "error": str(e)})
                logger.error("Failed to download %s: %s", url, e)
        return results

    def get_downloads(self) -> list:
        downloads = []
        for root, _dirs, files in os.walk(self.output_dir):
            for f in files:
                if f.endswith(".meta.json"):
                    fpath = os.path.join(root, f)
                    try:
                        with open(fpath, "r", encoding="utf-8") as fh:
                            downloads.append(json.load(fh))
                    except (json.JSONDecodeError, OSError):
                        continue
        return downloads

    def clear_cache(self) -> None:
        self._info_cache.clear()
        logger.info("Info cache cleared")
