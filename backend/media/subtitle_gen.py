import os
import re
import logging
from pathlib import Path
from datetime import timedelta
from typing import Optional

logger = logging.getLogger(__name__)

_SRT_TIMECODE_RE = re.compile(r"(\d{2}):(\d{2}):(\d{2}),(\d{3})")
_VTT_TIMECODE_RE = re.compile(r"(\d{2}):(\d{2}):(\d{2})\.(\d{3})")


def _seconds_to_srt_timecode(seconds: float) -> str:
    td = timedelta(seconds=seconds)
    total = int(td.total_seconds())
    h = total // 3600
    m = (total % 3600) // 60
    s = total % 60
    ms = int((td.total_seconds() - int(td.total_seconds())) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def _seconds_to_vtt_timecode(seconds: float) -> str:
    td = timedelta(seconds=seconds)
    total = int(td.total_seconds())
    h = total // 3600
    m = (total % 3600) // 60
    s = total % 60
    ms = int((td.total_seconds() - int(td.total_seconds())) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d}.{ms:03d}"


def _srt_timecode_to_seconds(tc: str) -> float:
    m = _SRT_TIMECODE_RE.match(tc)
    if not m:
        return 0.0
    h, mi, s, ms = int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4))
    return h * 3600 + mi * 60 + s + ms / 1000.0


def _vtt_timecode_to_seconds(tc: str) -> float:
    m = _VTT_TIMECODE_RE.match(tc)
    if not m:
        return 0.0
    h, mi, s, ms = int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4))
    return h * 3600 + mi * 60 + s + ms / 1000.0


class SubtitleGenerator:
    def __init__(self, default_duration: float = 3.0, max_line_length: int = 42):
        self.default_duration = default_duration
        self.max_line_length = max_line_length

    def generate_subtitles(self, text: str, output_path: str, format: str = "srt") -> str:
        if not text.strip():
            raise ValueError("Text cannot be empty")
        words = text.split()
        chunks = []
        current = ""
        for word in words:
            test = f"{current} {word}".strip()
            if len(test) <= self.max_line_length:
                current = test
            else:
                if current:
                    chunks.append(current)
                current = word
        if current:
            chunks.append(current)
        lines = []
        start = 0.0
        for i, chunk in enumerate(chunks):
            end = start + self.default_duration
            lines.append({"index": i + 1, "start": start, "end": end, "text": chunk})
            start = end
        return self._write_file(lines, output_path, format)

    def edit_subtitles(self, input_path: str, edits: list, output_path: str, format: str = "srt") -> str:
        subs = self.parse_subtitles(input_path)
        for edit in edits:
            idx = edit.get("index")
            for sub in subs:
                if sub["index"] == idx:
                    if "text" in edit:
                        sub["text"] = edit["text"]
                    if "start" in edit:
                        sub["start"] = edit["start"]
                    if "end" in edit:
                        sub["end"] = edit["end"]
                    break
        return self._write_file(subs, output_path, format)

    def parse_subtitles(self, file_path: str) -> list:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Subtitle file not found: {file_path}")
        ext = Path(file_path).suffix.lower()
        if ext == ".srt":
            return self._parse_srt(file_path)
        elif ext == ".vtt":
            return self._parse_vtt(file_path)
        else:
            raise ValueError(f"Unsupported subtitle format: {ext}")

    def _parse_srt(self, file_path: str) -> list:
        subs = []
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
        blocks = re.split(r"\n\s*\n", content)
        for block in blocks:
            lines = block.strip().split("\n")
            if len(lines) < 3:
                continue
            try:
                idx = int(lines[0])
            except ValueError:
                continue
            tc_match = re.match(
                r"(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})", lines[1]
            )
            if not tc_match:
                continue
            start = _srt_timecode_to_seconds(tc_match.group(1))
            end = _srt_timecode_to_seconds(tc_match.group(2))
            text = "\n".join(lines[2:])
            subs.append({"index": idx, "start": start, "end": end, "text": text})
        return subs

    def _parse_vtt(self, file_path: str) -> list:
        subs = []
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
        if content.startswith("WEBVTT"):
            content = content.split("\n", 1)[-1].strip()
        blocks = re.split(r"\n\s*\n", content)
        idx = 1
        for block in blocks:
            lines = block.strip().split("\n")
            if len(lines) < 2:
                continue
            tc_match = re.match(
                r"(\d{2}:\d{2}:\d{2}\.\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}\.\d{3})", lines[0]
            )
            if not tc_match:
                continue
            start = _vtt_timecode_to_seconds(tc_match.group(1))
            end = _vtt_timecode_to_seconds(tc_match.group(2))
            text = "\n".join(lines[1:])
            subs.append({"index": idx, "start": start, "end": end, "text": text})
            idx += 1
        return subs

    def _write_file(self, subs: list, output_path: str, format: str) -> str:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        fmt = format.lower().lstrip(".")
        if fmt == "srt":
            content = self._to_srt(subs)
        elif fmt == "vtt":
            content = self._to_vtt(subs)
        else:
            raise ValueError(f"Unsupported output format: {format}")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        logger.info("Subtitles written to %s", output_path)
        return output_path

    @staticmethod
    def _to_srt(subs: list) -> str:
        lines = []
        for sub in subs:
            lines.append(str(sub["index"]))
            lines.append(
                f"{_seconds_to_srt_timecode(sub['start'])} --> {_seconds_to_srt_timecode(sub['end'])}"
            )
            lines.append(sub["text"])
            lines.append("")
        return "\n".join(lines)

    @staticmethod
    def _to_vtt(subs: list) -> str:
        lines = ["WEBVTT", ""]
        for sub in subs:
            lines.append(
                f"{_seconds_to_vtt_timecode(sub['start'])} --> {_seconds_to_vtt_timecode(sub['end'])}"
            )
            lines.append(sub["text"])
            lines.append("")
        return "\n".join(lines)

    def convert_format(self, input_path: str, output_format: str) -> str:
        subs = self.parse_subtitles(input_path)
        ext = output_format.lower().lstrip(".")
        stem = Path(input_path).stem
        output_path = str(Path(input_path).parent / f"{stem}.{ext}")
        return self._write_file(subs, output_path, output_format)

    def shift_timing(self, input_path: str, offset_seconds: float, output_path: str, format: str = None) -> str:
        subs = self.parse_subtitles(input_path)
        if format is None:
            format = Path(input_path).suffix.lstrip(".")
        for sub in subs:
            sub["start"] = max(0, sub["start"] + offset_seconds)
            sub["end"] = max(0, sub["end"] + offset_seconds)
        return self._write_file(subs, output_path, format)

    def merge_subtitles(self, input_paths: list, output_path: str, format: str = "srt") -> str:
        all_subs = []
        idx = 1
        last_end = 0.0
        for path in input_paths:
            subs = self.parse_subtitles(path)
            gap = subs[0]["start"] if subs else 0
            shift = last_end - gap
            for sub in subs:
                sub["index"] = idx
                sub["start"] += shift
                sub["end"] += shift
                idx += 1
                all_subs.append(sub)
            if subs:
                last_end = subs[-1]["end"]
        return self._write_file(all_subs, output_path, format)
