#!/usr/bin/env python3
"""
Generate base frame first, then variations
This ensures consistency while getting variety
"""

import asyncio
import json
import sys
import httpx

OLLAMA_HOST = "http://100.93.108.89:11434"
FRAME_SIZE = 16


async def call_ollama(prompt: str, model: str = "llama3.2:3b") -> str:
    """Call Ollama LLM"""
    async with httpx.AsyncClient(timeout=300.0) as client:
        response = await client.post(
            f"{OLLAMA_HOST}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "num_predict": 1500,
                }
            }
        )
        response.raise_for_status()
        result = response.json()
        return result.get("response", "")


def fix_frame(frame_lines: list[str]) -> list[str]:
    """Fix frame to be exactly 16x16"""
    fixed = []
    for line in frame_lines:
        if len(line) < 16:
            line = line + (" " * (16 - len(line)))
        elif len(line) > 16:
            line = line[:16]
        fixed.append(line)

    while len(fixed) < 16:
        fixed.append(" " * 16)
    return fixed[:16]


async def generate_base_frame(description: str, model: str) -> tuple[list[str], dict]:
    """Generate the base character design"""
    print(f"Step 1: Generating base character design...")

    prompt = f"""Create ONE 16x16 pixel art frame of a {description} facing down.

Make a simple humanoid: head, body, 2 arms, 2 legs. 12-14 pixels tall, centered.

Characters: @ (body) # (details) + (bright) = (medium) - (light) . (outline) space (transparent)

Return ONLY this JSON:
{{
  "color_map": {{
    "@": "#8B0000",
    "#": "#CD5C5C",
    "+": "#FFB6C1",
    "=": "#A52A2A",
    "-": "#D3D3D3",
    ".": "#696969",
    " ": "#00000000"
  }},
  "base_frame": [16 strings of 16 chars each]
}}"""

    response = await call_ollama(prompt, model)

    # Parse
    response = response.strip()
    if response.startswith("```"):
        lines = response.split("\n")
        response = "\n".join(lines[1:-1])
        if response.startswith("json"):
            response = response[4:].strip()

    data = json.loads(response)
    base_frame = fix_frame(data["base_frame"])
    color_map = data.get("color_map", {})

    print(f"✓ Base frame generated")
    print("Preview:")
    for line in base_frame[:8]:
        print(f"  {line}")
    print("  ...")

    return base_frame, color_map


async def generate_variation(base_frame: list[str], direction: str, phase: int, model: str) -> list[str]:
    """Generate a variation based on the base frame"""

    phase_desc = {
        0: "left leg forward, right leg back",
        1: "both legs together (standing)",
        2: "right leg forward, left leg back"
    }

    direction_desc = {
        "down": "facing toward viewer (front)",
        "up": "facing away (back of head visible)",
        "left": "facing left (side profile)",
        "right": "facing right (side profile)"
    }

    # Show base frame as reference
    base_str = "\n".join(base_frame)

    prompt = f"""You created this base character:
```
{base_str}
```

Now modify it to show the SAME character but:
- Direction: {direction_desc[direction]}
- Leg position: {phase_desc[phase]}

Keep the same style, size, and character design. Only change:
1. The direction it's facing
2. The leg positions

Return ONLY this JSON:
{{
  "frame": [16 strings of 16 chars each]
}}"""

    response = await call_ollama(prompt, model)

    # Parse
    response = response.strip()
    if response.startswith("```"):
        lines = response.split("\n")
        response = "\n".join(lines[1:-1])
        if response.startswith("json"):
            response = response[4:].strip()

    data = json.loads(response)
    frame = fix_frame(data["frame"])

    return frame


async def generate_all(description: str, model: str = "llama3.2:3b"):
    """Generate base + all variations"""
    print(f"Generating animation for: '{description}'")
    print(f"Model: {model}")
    print("=" * 60)

    # Step 1: Base frame
    base_frame, color_map = await generate_base_frame(description, model)

    all_frames = {}
    all_frames["walk_down_1"] = base_frame  # Use base as standing frame

    # Step 2: Generate variations
    directions = ["down", "up", "left", "right"]

    for direction in directions:
        print(f"\nGenerating {direction} variations...")

        for phase in [0, 1, 2]:
            frame_name = f"walk_{direction}_{phase}"

            if frame_name == "walk_down_1":
                continue  # Already have this

            print(f"  - {frame_name}...", end=" ")
            frame = await generate_variation(base_frame, direction, phase, model)
            all_frames[frame_name] = frame
            print("✓")

    # Save
    result = {
        "color_map": color_map,
        "frames": all_frames
    }

    output_file = "walk_variations.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)

    print(f"\n{'=' * 60}")
    print(f"✓ Generated {len(all_frames)} frames")
    print(f"✓ Saved to: {output_file}")

    return result


async def main():
    if len(sys.argv) < 2:
        print("Usage: generate_with_variations.py <description> [model]")
        print("\nExample: python generate_with_variations.py 'red warrior'")
        sys.exit(1)

    description = sys.argv[1]
    model = sys.argv[2] if len(sys.argv) > 2 else "llama3.2:3b"

    try:
        await generate_all(description, model)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
