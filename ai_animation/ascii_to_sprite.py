#!/usr/bin/env python3
"""
Convert ASCII art frames to PNG sprite sheets
Each character in the ASCII art represents one pixel
"""

import json
import sys
from pathlib import Path
from PIL import Image, ImageDraw


def hex_to_rgba(hex_color: str) -> tuple[int, int, int, int]:
    """Convert hex color string to RGBA tuple"""
    hex_color = hex_color.lstrip('#')

    # Handle #RRGGBBAA format
    if len(hex_color) == 8:
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        a = int(hex_color[6:8], 16)
        return (r, g, b, a)
    # Handle #RRGGBB format
    elif len(hex_color) == 6:
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return (r, g, b, 255)
    else:
        raise ValueError(f"Invalid hex color: {hex_color}")


def ascii_to_image(ascii_lines: list[str], color_map: dict[str, str]) -> Image.Image:
    """Convert a single ASCII frame to a PIL Image"""
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
                # Default to transparent for unknown characters
                pixels[x, y] = (0, 0, 0, 0)

    return img


def create_sprite_sheet(animation_data: dict, output_path: str, scale: int = 1):
    """
    Create a sprite sheet from animation data

    Layout matches Godot's expectation:
    Row 0: walk_down (4 frames)
    Row 1: walk_up (4 frames)
    Row 2: walk_left (4 frames)
    Row 3: walk_right (4 frames)
    Row 4: idle_down, idle_up, idle_left, idle_right (1 frame each)
    """
    color_map = animation_data["color_map"]
    frames = animation_data["frames"]

    # Frame organization
    frame_layout = [
        ["walk_down_0", "walk_down_1", "walk_down_2", "walk_down_3"],
        ["walk_up_0", "walk_up_1", "walk_up_2", "walk_up_3"],
        ["walk_left_0", "walk_left_1", "walk_left_2", "walk_left_3"],
        ["walk_right_0", "walk_right_1", "walk_right_2", "walk_right_3"],
        ["idle_down_0", "idle_up_0", "idle_left_0", "idle_right_0"],
    ]

    # Determine frame size (should be 16x16 from the ASCII)
    first_frame = next(iter(frames.values()))
    frame_height = len(first_frame)
    frame_width = len(first_frame[0]) if first_frame else 0

    # Calculate sprite sheet dimensions
    cols = 4
    rows = len(frame_layout)
    sheet_width = cols * frame_width * scale
    sheet_height = rows * frame_height * scale

    # Create the sprite sheet
    sprite_sheet = Image.new('RGBA', (sheet_width, sheet_height), (0, 0, 0, 0))

    # Place each frame
    for row_idx, row in enumerate(frame_layout):
        for col_idx, frame_name in enumerate(row):
            if frame_name in frames:
                # Convert ASCII to image
                frame_img = ascii_to_image(frames[frame_name], color_map)

                # Scale up if needed
                if scale > 1:
                    frame_img = frame_img.resize(
                        (frame_width * scale, frame_height * scale),
                        Image.NEAREST  # Use nearest neighbor for pixel art
                    )

                # Paste into sprite sheet
                x = col_idx * frame_width * scale
                y = row_idx * frame_height * scale
                sprite_sheet.paste(frame_img, (x, y))

    # Save the sprite sheet
    sprite_sheet.save(output_path)
    print(f"Sprite sheet saved to: {output_path}")
    print(f"Dimensions: {sheet_width}x{sheet_height} ({cols} cols × {rows} rows)")
    print(f"Frame size: {frame_width * scale}x{frame_height * scale}")


def create_individual_frames(animation_data: dict, output_dir: str, scale: int = 1):
    """Create individual PNG files for each frame"""
    color_map = animation_data["color_map"]
    frames = animation_data["frames"]

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    for frame_name, ascii_lines in frames.items():
        # Convert to image
        frame_img = ascii_to_image(ascii_lines, color_map)

        # Scale if needed
        if scale > 1:
            width, height = frame_img.size
            frame_img = frame_img.resize(
                (width * scale, height * scale),
                Image.NEAREST
            )

        # Save
        frame_path = output_path / f"{frame_name}.png"
        frame_img.save(frame_path)
        print(f"Created: {frame_path}")


def main():
    """Main entry point"""
    if len(sys.argv) < 3:
        print("Usage: ascii_to_sprite.py <input.json> <output.png> [scale]")
        print("  or:  ascii_to_sprite.py <input.json> --frames <output_dir> [scale]")
        print()
        print("Examples:")
        print("  ascii_to_sprite.py animation.json sprite_sheet.png 2")
        print("  ascii_to_sprite.py animation.json --frames ./frames/ 1")
        sys.exit(1)

    input_file = sys.argv[1]
    scale = int(sys.argv[3]) if len(sys.argv) > 3 else 1

    # Load animation data
    with open(input_file, 'r') as f:
        animation_data = json.load(f)

    # Check output mode
    if sys.argv[2] == "--frames":
        output_dir = sys.argv[3] if len(sys.argv) > 3 else "./frames"
        scale = int(sys.argv[4]) if len(sys.argv) > 4 else 1
        create_individual_frames(animation_data, output_dir, scale)
    else:
        output_file = sys.argv[2]
        create_sprite_sheet(animation_data, output_file, scale)


if __name__ == "__main__":
    main()
