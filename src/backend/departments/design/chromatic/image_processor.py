from PIL import Image
import numpy as np
from typing import List, Tuple

class ImageProcessor:
    """Vision Core (BioVisionNet Surrogate).

    Translates visual data (Images) into Structural Light Data (Particle Targets)
    for the rendering engine.
    """

    @staticmethod
    def process_image_to_particles(image: Image.Image, max_particles: int = 300) -> List[Tuple[float, float, str]]:
        """Converts an image into a set of particle targets.

        Resizes the image to a low-resolution grid and maps non-empty pixels to
        normalized coordinates.

        Args:
            image: A PIL Image object.
            max_particles: Maximum number of points to extract.

        Returns:
            A list of (x, y, color_hex) tuples, where x and y are normalized [0, 1].
        """
        # Resize to a grid that roughly approximates the particle count
        # Square root of max_particles to get grid side
        side = int(np.sqrt(max_particles))
        img_small = image.resize((side, side), Image.Resampling.LANCZOS)

        # Convert to RGBA to handle transparency if present
        if img_small.mode != 'RGBA':
            img_small = img_small.convert('RGBA')

        width, height = img_small.size
        pixels = list(img_small.getdata())

        targets = []

        for i, pixel in enumerate(pixels):
            r, g, b, a = pixel

            # Skip transparent or very dark pixels
            if a < 50 or (r < 30 and g < 30 and b < 30):
                continue

            x = (i % width) / width
            y = (i // width) / height

            # Convert RGB to Hex
            color_hex = "#{:02x}{:02x}{:02x}".format(r, g, b)

            targets.append((x, y, color_hex))

        return targets

    @staticmethod
    def create_text_image(text: str) -> Image.Image:
        """Generates a fallback image containing the specified text.

        Used when image generation services are unavailable.

        Args:
            text: The text to render onto the image.

        Returns:
            A PIL Image object with the text rendered on a black background.
        """
        from PIL import ImageDraw, ImageFont
        img = Image.new('RGB', (200, 200), color=(0, 0, 0))
        d = ImageDraw.Draw(img)
        # Default font might not be available, use load_default
        try:
            # Try to load a generic font or fallback
            font = ImageFont.load_default()
        except:
            font = None

        d.text((10, 90), text, fill=(255, 255, 255), font=font)
        return img
