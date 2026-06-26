import os
import logging
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)

_TEMPLATES = {
    "classic": {"top_ratio": 0.08, "bottom_ratio": 0.85, "font_ratio": 0.06},
    "drake": {"top_ratio": 0.05, "bottom_ratio": 0.52, "font_ratio": 0.05},
    "caption": {"top_ratio": 0.85, "bottom_ratio": None, "font_ratio": 0.05},
}


class MemeGenerator:
    def __init__(self, font_path: str = None, default_style: str = "classic"):
        self.font_path = font_path
        self.default_style = default_style
        if default_style not in _TEMPLATES:
            raise ValueError(f"Unknown style '{default_style}'. Available: {list(_TEMPLATES.keys())}")

    @staticmethod
    def list_templates() -> list:
        return list(_TEMPLATES.keys())

    @staticmethod
    def _get_font(size: int, font_path: str = None):
        if font_path and os.path.exists(font_path):
            return ImageFont.truetype(font_path, size)
        try:
            return ImageFont.truetype("arial.ttf", size)
        except (OSError, IOError):
            return ImageFont.load_default()

    def _draw_text(
        self,
        draw: ImageDraw.Draw,
        text: str,
        position: tuple,
        font: ImageFont.FreeTypeFont,
        image_width: int,
        align: str = "center",
    ):
        lines = self._wrap_text(text.upper(), font, image_width - 40)
        y = position[1]
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x = (image_width - text_width) // 2 if align == "center" else 20
            draw.text((x, y), line, fill="white", font=font, stroke_width=2, stroke_color="black")
            y += text_height + 8

    @staticmethod
    def _wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list:
        words = text.split()
        lines = []
        current = ""
        for word in words:
            test = f"{current} {word}".strip()
            bbox = font.getbbox(test)
            if bbox and (bbox[2] - bbox[0]) <= max_width:
                current = test
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines or [text]

    def create_meme(
        self,
        image_path: str,
        top_text: str,
        bottom_text: str,
        output_path: str,
        style: str = None,
    ) -> str:
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")
        style = style or self.default_style
        if style not in _TEMPLATES:
            raise ValueError(f"Unknown style '{style}'. Available: {list(_TEMPLATES.keys())}")
        image = Image.open(image_path).convert("RGB")
        img_w, img_h = image.size
        config = _TEMPLATES[style]
        font_size = max(20, int(img_w * config["font_ratio"]))
        font = self._get_font(font_size, self.font_path)
        draw = ImageDraw.Draw(image)
        if top_text:
            top_y = int(img_h * config["top_ratio"])
            self._draw_text(draw, top_text, (0, top_y), font, img_w)
        if bottom_text and config["bottom_ratio"] is not None:
            bottom_y = int(img_h * config["bottom_ratio"])
            self._draw_text(draw, bottom_text, (0, bottom_y), font, img_w)
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        image.save(output_path)
        logger.info("Meme saved to %s", output_path)
        return output_path

    def create_custom_meme(
        self,
        image_path: str,
        texts: list,
        positions: list,
        output_path: str,
        font_size: int = 40,
        color: str = "white",
        stroke_color: str = "black",
    ) -> str:
        if len(texts) != len(positions):
            raise ValueError("texts and positions must have the same length")
        image = Image.open(image_path).convert("RGB")
        draw = ImageDraw.Draw(image)
        font = self._get_font(font_size, self.font_path)
        for text, pos in zip(texts, positions):
            draw.text(pos, text.upper(), fill=color, font=font, stroke_width=2, stroke_color=stroke_color)
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        image.save(output_path)
        logger.info("Custom meme saved to %s", output_path)
        return output_path

    def add_watermark(self, meme_path: str, watermark_text: str, output_path: str) -> str:
        image = Image.open(meme_path).convert("RGBA")
        overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        font = self._get_font(20, self.font_path)
        bbox = draw.textbbox((0, 0), watermark_text, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        x = image.width - tw - 10
        y = image.height - th - 10
        draw.text((x, y), watermark_text, fill=(255, 255, 255, 128), font=font)
        watermarked = Image.alpha_composite(image, overlay)
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        watermarked.convert("RGB").save(output_path)
        return output_path
