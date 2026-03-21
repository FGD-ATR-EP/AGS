import math
import random
from typing import List, Tuple, Optional

class FormationManager:
    """Generates coordinate sets for particle formations.

    Coordinates are normalized (0.0 to 1.0) relative to the provided canvas dimensions,
    facilitating resolution-independent rendering on the frontend.
    """

    def calculate_formation(self, shape_type: str, particle_count: int, canvas_width: int, canvas_height: int) -> List[Tuple[float, float, str]]:
        """Calculates normalized particle coordinates for a given shape.

        This acts as an adapter method that currently ignores canvas dimensions
        to return normalized coordinates (0.0-1.0), which is the expected format
        for the current frontend renderer.

        Args:
            shape_type: The name of the shape (e.g., "circle", "square").
            particle_count: The number of particles to generate.
            canvas_width: The width of the canvas (unused, for interface compatibility).
            canvas_height: The height of the canvas (unused, for interface compatibility).

        Returns:
            A list of tuples, where each tuple contains (x, y, color_hint).
            x and y are floats between 0.0 and 1.0.
        """
        return self.get_formation(shape_type, particle_count)

    @staticmethod
    def get_formation(shape: str, count: int, center: Tuple[float, float] = (0.5, 0.5), scale: float = 0.3) -> List[Tuple[float, float, str]]:
        """Generates formation coordinates based on shape name.

        Args:
            shape: The name of the shape (case-insensitive).
            count: The number of particles.
            center: A tuple (x, y) for the center point. Defaults to (0.5, 0.5).
            scale: The scale of the formation relative to the canvas size. Defaults to 0.3.

        Returns:
            A list of (x, y, color_hint) tuples.
        """
        shape = shape.lower().strip()
        points = []

        if shape == "circle" or shape == "ring":
            points = FormationManager._circle(count, center, scale)
        elif shape == "square" or shape == "box":
            points = FormationManager._square(count, center, scale)
        elif shape == "line" or shape == "horizontal":
            points = FormationManager._line(count, center, scale)
        elif shape == "vertical":
            points = FormationManager._vertical_line(count, center, scale)
        elif shape == "spiral" or shape == "vortex":
            points = FormationManager._spiral(count, center, scale)
        elif shape == "cross" or shape == "x":
            points = FormationManager._cross(count, center, scale)
        else:
            # Default to random scatter (Nebula)
            points = FormationManager._scatter(count, center, scale)

        return points

    @staticmethod
    def _circle(count: int, center: Tuple[float, float], scale: float) -> List[Tuple[float, float, str]]:
        """Generates points arranged in a circle."""
        cx, cy = center
        points = []
        for i in range(count):
            angle = (i / count) * 2 * math.pi
            x = cx + math.cos(angle) * scale
            # Aspect ratio correction could be applied here if needed, but assuming square canvas for now
            y = cy + math.sin(angle) * scale
            points.append((x, y, "default"))
        return points

    @staticmethod
    def _square(count: int, center: Tuple[float, float], scale: float) -> List[Tuple[float, float, str]]:
        """Generates points arranged in a square outline."""
        cx, cy = center
        points = []
        side = scale * 2
        per_side = count // 4
        # Top
        for i in range(per_side):
            x = cx - scale + (i / per_side) * side
            y = cy - scale
            points.append((x, y, "default"))
        # Right
        for i in range(per_side):
            x = cx + scale
            y = cy - scale + (i / per_side) * side
            points.append((x, y, "default"))
        # Bottom
        for i in range(per_side):
            x = cx + scale - (i / per_side) * side
            y = cy + scale
            points.append((x, y, "default"))
        # Left
        for i in range(count - 3 * per_side): # Remainder
            x = cx - scale
            y = cy + scale - (i / (count - 3 * per_side)) * side
            points.append((x, y, "default"))
        return points

    @staticmethod
    def _line(count: int, center: Tuple[float, float], scale: float) -> List[Tuple[float, float, str]]:
        """Generates points arranged in a horizontal line."""
        cx, cy = center
        points = []
        start_x = cx - scale
        width = scale * 2
        for i in range(count):
            x = start_x + (i / count) * width
            y = cy
            points.append((x, y, "default"))
        return points

    @staticmethod
    def _vertical_line(count: int, center: Tuple[float, float], scale: float) -> List[Tuple[float, float, str]]:
        """Generates points arranged in a vertical line."""
        cx, cy = center
        points = []
        start_y = cy - scale
        height = scale * 2
        for i in range(count):
            x = cx
            y = start_y + (i / count) * height
            points.append((x, y, "default"))
        return points

    @staticmethod
    def _spiral(count: int, center: Tuple[float, float], scale: float) -> List[Tuple[float, float, str]]:
        """Generates points arranged in a spiral."""
        cx, cy = center
        points = []
        rotations = 3
        for i in range(count):
            progress = i / count
            angle = progress * rotations * 2 * math.pi
            radius = progress * scale
            x = cx + math.cos(angle) * radius
            y = cy + math.sin(angle) * radius
            points.append((x, y, "default"))
        return points

    @staticmethod
    def _cross(count: int, center: Tuple[float, float], scale: float) -> List[Tuple[float, float, str]]:
        """Generates points arranged in a cross (+)."""
        cx, cy = center
        points = []
        half = count // 2
        # Horizontal
        for i in range(half):
            x = (cx - scale) + (i / half) * (scale * 2)
            y = cy
            points.append((x, y, "default"))
        # Vertical
        remainder = count - half
        for i in range(remainder):
            x = cx
            y = (cy - scale) + (i / remainder) * (scale * 2)
            points.append((x, y, "default"))
        return points

    @staticmethod
    def _scatter(count: int, center: Tuple[float, float], scale: float) -> List[Tuple[float, float, str]]:
        """Generates points scattered randomly within a circle."""
        cx, cy = center
        points = []
        for _ in range(count):
            # Random inside circle
            angle = random.random() * 2 * math.pi
            radius = math.sqrt(random.random()) * scale
            x = cx + math.cos(angle) * radius
            y = cy + math.sin(angle) * radius
            points.append((x, y, "default"))
        return points
