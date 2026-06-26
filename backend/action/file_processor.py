# backend/action/file_processor.py
import os
import csv
import json
from pathlib import Path
from datetime import datetime


def _resolve_path(raw: str) -> Path:
    shortcuts = {
        "desktop":   Path.home() / "Desktop",
        "downloads": Path.home() / "Downloads",
        "documents": Path.home() / "Documents",
        "pictures":  Path.home() / "Pictures",
    }
    lower = raw.strip().lower()
    if lower in shortcuts:
        return shortcuts[lower]
    return Path(raw).expanduser()


def _format_size(bytes_size: int) -> str:
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if bytes_size < 1024:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024
    return f"{bytes_size:.1f} TB"


def merge_csv(file1: str, file2: str, output: str = "", key_column: str = "") -> str:
    try:
        p1 = _resolve_path(file1)
        p2 = _resolve_path(file2)
        if not p1.exists():
            return f"File not found: {file1}"
        if not p2.exists():
            return f"File not found: {file2}"

        out_path = _resolve_path(output) if output else p1.parent / f"merged_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        rows1 = []
        with open(p1, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            for row in reader:
                rows1.append(row)

        rows2 = []
        with open(p2, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows2.append(row)

        all_fieldnames = list(dict.fromkeys((fieldnames or []) + (reader.fieldnames or [])))

        if key_column and key_column in all_fieldnames:
            merged = {r.get(key_column, ""): r for r in rows2}
            merged.update({r.get(key_column, ""): r for r in rows1})
            merged_rows = list(merged.values())
        else:
            merged_rows = rows1 + rows2

        with open(out_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=all_fieldnames)
            writer.writeheader()
            writer.writerows(merged_rows)

        return f"Merged {len(rows1)} + {len(rows2)} rows -> {len(merged_rows)} rows. Saved: {out_path}"
    except Exception as e:
        return f"CSV merge error: {e}"


def convert_csv_to_json(file_path: str, output_path: str = "") -> str:
    try:
        src = _resolve_path(file_path)
        if not src.exists():
            return f"File not found: {file_path}"

        out = _resolve_path(output_path) if output_path else src.with_suffix(".json")

        rows = []
        with open(src, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(row)

        out.write_text(json.dumps(rows, indent=2), encoding="utf-8")
        return f"Converted CSV ({len(rows)} rows) -> JSON. Saved: {out}"
    except Exception as e:
        return f"CSV->JSON error: {e}"


def convert_json_to_csv(file_path: str, output_path: str = "") -> str:
    try:
        src = _resolve_path(file_path)
        if not src.exists():
            return f"File not found: {file_path}"

        out = _resolve_path(output_path) if output_path else src.with_suffix(".csv")

        data = json.loads(src.read_text(encoding="utf-8"))
        if not isinstance(data, list) or not data:
            return "JSON must be a non-empty array of objects."

        fieldnames = list(data[0].keys())
        with open(out, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)

        return f"Converted JSON ({len(data)} rows) -> CSV. Saved: {out}"
    except Exception as e:
        return f"JSON->CSV error: {e}"


def batch_rename(directory: str, find_text: str, replace_text: str, dry_run: bool = False) -> str:
    try:
        folder = _resolve_path(directory)
        if not folder.exists():
            return f"Directory not found: {directory}"

        renamed = []
        for item in folder.iterdir():
            if item.is_file() and find_text in item.name:
                new_name = item.name.replace(find_text, replace_text)
                new_path = item.parent / new_name
                if not dry_run:
                    item.rename(new_path)
                renamed.append(f"{item.name} -> {new_name}")

        if not renamed:
            return f"No files matched '{find_text}' in {folder.name}/"
        return f"{'[DRY RUN] ' if dry_run else ''}Renamed {len(renamed)} file(s):\n" + "\n".join(renamed[:20])
    except Exception as e:
        return f"Batch rename error: {e}"


def batch_resize_images(directory: str, max_width: int = 1920, max_height: int = 1080, output_format: str = "") -> str:
    try:
        from PIL import Image
    except ImportError:
        return "Pillow not installed. Run: pip install Pillow"

    try:
        folder = _resolve_path(directory)
        if not folder.exists():
            return f"Directory not found: {directory}"

        ext_whitelist = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
        converted = 0
        errors = []

        for item in folder.iterdir():
            if item.suffix.lower() not in ext_whitelist:
                continue

            try:
                img = Image.open(item)
                img.thumbnail((max_width, max_height), Image.LANCZOS)

                fmt = output_format.lower() if output_format else img.format or "JPEG"
                save_kwargs = {"quality": 85, "optimize": True}

                if fmt == "png":
                    save_kwargs = {}
                elif fmt == "webp":
                    save_kwargs = {"quality": 80}

                ext = {  # noqa: F841
                    "jpeg": ".jpg", "jpg": ".jpg", "png": ".png", "webp": ".webp",
                }.get(fmt, img.suffix.lower())

                new_path = item.parent / f"{item.stem}_{max_width}x{max_height}{img.suffix.lower()}"
                img.save(new_path, format=fmt.upper() if fmt else img.format, **save_kwargs)
                converted += 1

            except Exception as e:
                errors.append(f"{item.name}: {e}")

        msg = f"Resized {converted} image(s) to max {max_width}x{max_height}."
        if errors:
            msg += f"\nErrors: {'; '.join(errors[:5])}"
        return msg

    except Exception as e:
        return f"Batch resize error: {e}"


def extract_text_from_pdf(file_path: str, output_path: str = "") -> str:
    try:
        import PyPDF2
    except ImportError:
        return "PyPDF2 not installed. Run: pip install PyPDF2"

    try:
        src = _resolve_path(file_path)
        if not src.exists():
            return f"File not found: {file_path}"

        text_parts = []
        with open(src, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page_num, page in enumerate(reader.pages, 1):
                page_text = page.extract_text()
                if page_text.strip():
                    text_parts.append(f"--- Page {page_num} ---\n{page_text.strip()}")

        full_text = "\n\n".join(text_parts)

        if output_path:
            out = _resolve_path(output_path)
            out.write_text(full_text, encoding="utf-8")
            return f"Extracted {len(text_parts)} pages -> {out}"
        return f"Extracted {len(text_parts)} pages:\n\n{full_text[:3000]}"
    except Exception as e:
        return f"PDF extraction error: {e}"


def count_words(file_path: str) -> str:
    try:
        src = _resolve_path(file_path)
        if not src.exists():
            return f"File not found: {file_path}"

        text = src.read_text(encoding="utf-8", errors="ignore")
        char_count = len(text)
        word_count = len(text.split())
        line_count = len(text.splitlines())

        return (
            f"File: {src.name}\n"
            f"  Lines : {line_count}\n"
            f"  Words : {word_count}\n"
            f"  Chars : {char_count}\n"
            f"  Size  : {_format_size(src.stat().st_size)}"
        )
    except Exception as e:
        return f"Count error: {e}"


def file_processor(parameters: dict, response=None, player=None, session_memory=None) -> str:
    params = parameters or {}
    action = params.get("action", "").lower().strip()

    if not action:
        return "No action specified for file_processor."

    if player:
        player.write_log(f"[FileProcessor] {action}")

    try:
        if action == "merge_csv":
            return merge_csv(
                params.get("file1", ""),
                params.get("file2", ""),
                params.get("output", ""),
                params.get("key_column", ""),
            )
        elif action == "csv_to_json":
            return convert_csv_to_json(params.get("path", ""), params.get("output", ""))
        elif action == "json_to_csv":
            return convert_json_to_csv(params.get("path", ""), params.get("output", ""))
        elif action == "batch_rename":
            return batch_rename(
                params.get("directory", ""),
                params.get("find", ""),
                params.get("replace", ""),
                params.get("dry_run", False),
            )
        elif action == "batch_resize":
            return batch_resize_images(
                params.get("directory", ""),
                int(params.get("max_width", 1920)),
                int(params.get("max_height", 1080)),
                params.get("format", ""),
            )
        elif action == "extract_pdf":
            return extract_text_from_pdf(params.get("path", ""), params.get("output", ""))
        elif action == "count_words":
            return count_words(params.get("path", ""))
        else:
            return f"Unknown action: '{action}'"
    except Exception as e:
        return f"File processor error: {e}"
