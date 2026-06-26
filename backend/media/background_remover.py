import os
import logging
from pathlib import Path
from PIL import Image, ImageFilter

logger = logging.getLogger(__name__)


class BackgroundRemover:
    def __init__(self, threshold: int = 200, blur_radius: int = 5):
        self.threshold = threshold
        self.blur_radius = blur_radius

    def load_image(self, image_path: str) -> Image.Image:
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")
        return Image.open(image_path).convert("RGBA")

    def save_image(self, image: Image.Image, output_path: str) -> str:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        image.save(output_path, format="PNG")
        logger.info("Saved background-removed image to %s", output_path)
        return output_path

    def remove_background(self, image_path: str, output_path: str) -> str:
        image = self.load_image(image_path)
        image = image.convert("RGBA")
        gray = image.convert("L")
        mask = gray.point(lambda x: 0 if x < self.threshold else 255, "L")
        mask = mask.filter(ImageFilter.GaussianBlur(radius=self.blur_radius))
        result = Image.new("RGBA", image.size, (0, 0, 0, 0))
        result.paste(image, mask=mask)
        return self.save_image(result, output_path)

    def remove_background_color_key(
        self, image_path: str, key_color: tuple, output_path: str, tolerance: int = 60
    ) -> str:
        image = self.load_image(image_path).convert("RGBA")
        pixels = image.load()
        for y in range(image.height):
            for x in range(image.width):
                r, g, b, a = pixels[x, y]
                if (
                    abs(r - key_color[0]) < tolerance
                    and abs(g - key_color[1]) < tolerance
                    and abs(b - key_color[2]) < tolerance
                ):
                    pixels[x, y] = (0, 0, 0, 0)
        return self.save_image(image, output_path)

    def apply_mask(self, image_path: str, mask_path: str, output_path: str) -> str:
        image = self.load_image(image_path)
        mask = Image.open(mask_path).convert("L").resize(image.size)
        result = Image.new("RGBA", image.size, (0, 0, 0, 0))
        result.paste(image, mask=mask)
        return self.save_image(result, output_path)

    def composite_on_background(
        self, foreground_path: str, background_path: str, output_path: str, position: tuple = (0, 0)
    ) -> str:
        fg = self.load_image(foreground_path)
        bg = Image.open(background_path).convert("RGBA")
        bg.paste(fg, position, fg)
        return self.save_image(bg, output_path)
