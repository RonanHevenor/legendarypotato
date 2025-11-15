#!/usr/bin/env python3
"""Convert a single frame JSON to PNG"""

import json
import sys
from PIL import Image


def hex_to_rgba(hex_color: str) -> tuple[int, int, int, int]:
    """Convert hex color string to RGBA tuple"""
    hex_color = hex_color.lstrip('#')

    if len(hex_color) == 8:
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        a = int(hex_color[6:8], 16)
        return (r, g, b, a)
    elif len(hex_color) == 6:
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return (r, g, b, 255)
    else:
        raise ValueError(f"Invalid hex color: {hex_color}")


def ascii_to_image(ascii_lines: list[str], color_map: dict[str, str], scale: int = 1) -> Image.Image:
    """Convert ASCII frame to PIL Image"""
    height = len(ascii_lines)
    width = len(ascii_lines[0]) if ascii_lines else 0

    # Create RGBA image
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    pixels = img.load()

    for y, line in enumerate(ascii_lines):
        for x, char in enumerate(line):
            if char in color_map:
                color = hex_to_rgba(color_map[char])
                pixels[x, y] = color
            else:
                pixels[x, y] = (0, 0, 0, 0)

    # Scale up if needed
    if scale > 1:
        img = img.resize((width * scale, height * scale), Image.NEAREST)

    return img


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: convert_single_frame.py <input.json> <output.png> [scale]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    scale = int(sys.argv[3]) if len(sys.argv) > 3 else 8

    # Load JSON
    with open(input_file, 'r') as f:
        data = json.load(f)

    # Convert and save
    img = ascii_to_image(data["frame"], data["color_map"], scale)
    img.save(output_file)
    print(f"✓ Saved {output_file} ({img.width}x{img.height})")
