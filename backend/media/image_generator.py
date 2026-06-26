import os
import random
import logging
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

logger = logging.getLogger(__name__)


class ImageGenerator:
    def __init__(self, width: int = 512, height: int = 512, provider: str = "mock"):
        self.width = width
        self.height = height
        self.provider = provider

    def _generate_mock_image(self, prompt: str) -> Image.Image:
        image = Image.new("RGB", (self.width, self.height), self._random_color())
        draw = ImageDraw.Draw(image)
        for _ in range(random.randint(5, 15)):
            x0 = random.randint(0, self.width)
            y0 = random.randint(0, self.height)
            x1 = random.randint(x0, self.width)
            y1 = random.randint(y0, self.height)
            draw.ellipse([x0, y0, x1, y1], fill=self._random_color(), outline=None)
        for _ in range(random.randint(3, 8)):
            x0 = random.randint(0, self.width)
            y0 = random.randint(0, self.height)
            x1 = random.randint(x0, self.width)
            y1 = random.randint(y0, self.height)
            draw.rectangle([x0, y0, x1, y1], fill=self._random_color(), outline=None)
        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except (OSError, IOError):
            font = ImageFont.load_default()
        lines = self._wrap_text(prompt, font, self.width - 40)
        y_pos = 10
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            tw = bbox[2] - bbox[0]
            draw.text(((self.width - tw) // 2, y_pos), line, fill="white", font=font)
            y_pos += bbox[3] - bbox[1] + 5
        image = image.filter(ImageFilter.SMOOTH_MORE)
        return image

    @staticmethod
    def _random_color() -> tuple:
        return (
            random.randint(30, 225),
            random.randint(30, 225),
            random.randint(30, 225),
        )

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

    def save_image(self, image: Image.Image, output_path: str) -> str:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        image.save(output_path)
        logger.info("Image saved to %s", output_path)
        return output_path

    def generate_from_prompt(self, prompt: str, output_path: str) -> str:
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty")
        image = self._generate_mock_image(prompt)
        return self.save_image(image, output_path)

    def generate_variation(self, image_path: str, output_path: str, variation_level: float = 0.3) -> str:
        if not 0 <= variation_level <= 1:
            raise ValueError("variation_level must be between 0 and 1")
        image = Image.open(image_path).convert("RGB")
        blur = int(variation_level * 10) or 1
        image = image.filter(ImageFilter.GaussianBlur(radius=blur))
        draw = ImageDraw.Draw(image)
        noise_pixels = int(image.width * image.height * variation_level * 0.1)
        for _ in range(noise_pixels):
            x = random.randint(0, image.width - 1)
            y = random.randint(0, image.height - 1)
            draw.point((x, y), fill=self._random_color())
        return self.save_image(image, output_path)

    def resize_image(self, image_path: str, width: int, height: int, output_path: str) -> str:
        image = Image.open(image_path)
        resized = image.resize((width, height), Image.LANCZOS)
        return self.save_image(resized, output_path)

    def get_info(self) -> dict:
        return {"width": self.width, "height": self.height, "provider": self.provider}
