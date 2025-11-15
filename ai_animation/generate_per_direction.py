#!/usr/bin/env python3
"""
Generate animation frames ONE DIRECTION AT A TIME
This prevents the LLM from lazily duplicating frames
"""

import asyncio
import json
import sys
import httpx

OLLAMA_HOST = "http://100.93.108.89:11434"
FRAME_SIZE = 16


async def call_ollama(prompt: str, model: str = "qwen2.5:7b") -> str:
    """Call Ollama LLM with the given prompt"""
    async with httpx.AsyncClient(timeout=300.0) as client:
        response = await client.post(
            f"{OLLAMA_HOST}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.6,
                    "top_p": 0.9,
                    "num_predict": 2000,
                }
            }
        )
        response.raise_for_status()
        result = response.json()
        return result.get("response", "")


def fix_frame(frame_lines: list[str], target_size: int = 16) -> list[str]:
    """Fix frame to be exactly target_size x target_size"""
    fixed_lines = []
    for line in frame_lines:
        if len(line) < target_size:
            line = line + (" " * (target_size - len(line)))
        elif len(line) > target_size:
            line = line[:target_size]
        fixed_lines.append(line)

    while len(fixed_lines) < target_size:
        fixed_lines.append(" " * target_size)
    if len(fixed_lines) > target_size:
        fixed_lines = fixed_lines[:target_size]

    return fixed_lines


def create_direction_prompt(character_description: str, direction: str) -> str:
    """Create prompt for ONE direction with 3 walk phases"""

    direction_desc = {
        "down": "facing TOWARD viewer (front view) - you can see the face",
        "up": "facing AWAY from viewer (back view) - you see the back of head",
        "left": "facing LEFT (side profile) - character faces to the left side",
        "right": "facing RIGHT (side profile) - character faces to the right side"
    }

    return f"""Create 3 walk animation frames for a {character_description} facing {direction}.

DIRECTION: Character is {direction_desc[direction]}

CHARACTER: Make a simple humanoid with head, body, arms, legs (12-14 pixels tall, centered)

WALK CYCLE (3 UNIQUE frames):
- Frame 0: Left leg FORWARD, right leg BACK (wide stance)
- Frame 1: Both legs TOGETHER (standing/middle position)
- Frame 2: Right leg FORWARD, left leg BACK (wide stance - OPPOSITE of frame 0)

EACH FRAME MUST BE DIFFERENT! Show the legs in different positions!

16x16 grid. Characters: @ (body) # (details) + (highlights) = (medium) - (light) . (outline) (space)

Return ONLY this JSON:
{{
  "frame_0": [16 lines of 16 chars],
  "frame_1": [16 lines of 16 chars],
  "frame_2": [16 lines of 16 chars]
}}

Make frame_0, frame_1, frame_2 VISIBLY DIFFERENT from each other!"""


async def generate_direction(description: str, direction: str, model: str) -> dict:
    """Generate 3 frames for one direction"""
    print(f"\n--- Generating {direction} direction ---")

    prompt = create_direction_prompt(description, direction)
    response = await call_ollama(prompt, model)

    # Parse JSON
    response = response.strip()
    if response.startswith("```"):
        lines = response.split("\n")
        response = "\n".join(lines[1:-1])
        if response.startswith("json"):
            response = response[4:].strip()

    try:
        data = json.loads(response)

        # Fix frames
        for i in range(3):
            key = f"frame_{i}"
            if key in data:
                data[key] = fix_frame(data[key], FRAME_SIZE)

        print(f"✓ Generated {direction}: {list(data.keys())}")
        return data

    except json.JSONDecodeError as e:
        print(f"✗ JSON error for {direction}: {e}")
        print(f"Response: {response[:200]}...")
        return {}


async def generate_all_directions(description: str, model: str = "qwen2.5:7b"):
    """Generate walk animation by generating each direction separately"""
    print(f"Generating walk animation for: '{description}'")
    print(f"Model: {model}")
    print("=" * 60)

    directions = ["down", "up", "left", "right"]
    all_frames = {}

    color_map = {
        "@": "#8B0000",
        "#": "#CD5C5C",
        "+": "#FFB6C1",
        "=": "#A52A2A",
        "-": "#D3D3D3",
        ".": "#696969",
        " ": "#00000000"
    }

    # Generate each direction
    for direction in directions:
        dir_frames = await generate_direction(description, direction, model)

        # Add to all_frames with proper naming
        for i in range(3):
            frame_key = f"walk_{direction}_{i}"
            if f"frame_{i}" in dir_frames:
                all_frames[frame_key] = dir_frames[f"frame_{i}"]

    # Save result
    result = {
        "color_map": color_map,
        "frames": all_frames
    }

    output_file = "walk_per_direction.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)

    print(f"\n{'=' * 60}")
    print(f"✓ Generated {len(all_frames)} frames total")
    print(f"✓ Saved to: {output_file}")

    # Show a preview
    if "walk_down_1" in all_frames:
        print(f"\nPreview of walk_down_1:")
        for line in all_frames["walk_down_1"][:8]:
            print(f"  {line}")
        print("  ...")

    return result


async def main():
    if len(sys.argv) < 2:
        print("Usage: generate_per_direction.py <character_description> [model]")
        print("\nExample: python generate_per_direction.py 'red warrior'")
        sys.exit(1)

    description = sys.argv[1]
    model = sys.argv[2] if len(sys.argv) > 2 else "qwen2.5:7b"

    await generate_all_directions(description, model)


if __name__ == "__main__":
    asyncio.run(main())
