#!/usr/bin/env python3
"""
Robust animation generation with error handling and retries
Generates 3 frames at a time to avoid duplication
"""

import asyncio
import json
import sys
import httpx
from typing import Optional

OLLAMA_HOST = "http://100.93.108.89:11434"
FRAME_SIZE = 16


async def call_ollama(prompt: str, model: str = "qwen2.5:7b", timeout: float = 120.0) -> str:
    """Call Ollama with error handling"""
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                f"{OLLAMA_HOST}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "num_predict": 2000,
                    }
                }
            )
            response.raise_for_status()
            result = response.json()
            return result.get("response", "")
    except Exception as e:
        print(f"    ✗ LLM call failed: {e}")
        return ""


def fix_frame(frame_lines: list[str]) -> list[str]:
    """Fix frame to exactly 16x16"""
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


def parse_json_response(response: str) -> Optional[dict]:
    """Parse JSON from LLM response with multiple strategies"""
    if not response or not response.strip():
        return None

    response = response.strip()

    # Strategy 1: Direct parse
    try:
        return json.loads(response)
    except:
        pass

    # Strategy 2: Remove markdown code blocks
    if response.startswith("```"):
        lines = response.split("\n")
        response = "\n".join(lines[1:-1])
        if response.startswith("json"):
            response = response[4:].strip()
        try:
            return json.loads(response)
        except:
            pass

    # Strategy 3: Find JSON object
    start = response.find("{")
    end = response.rfind("}") + 1
    if start >= 0 and end > start:
        try:
            return json.loads(response[start:end])
        except:
            pass

    return None


def create_3frame_prompt(char_desc: str, direction: str) -> str:
    """Create prompt for exactly 3 walk frames in one direction"""

    dir_info = {
        "down": "facing FORWARD (you see the face)",
        "up": "facing AWAY (you see the back)",
        "left": "facing LEFT (side profile, face points left)",
        "right": "facing RIGHT (side profile, face points right)"
    }

    return f"""Create 3 DIFFERENT walk animation frames for a {char_desc}.

Direction: {dir_info[direction]}

Make a simple humanoid (head, body, 2 arms, 2 legs). About 12 pixels tall, centered.

IMPORTANT - Create 3 UNIQUE frames:
1. Frame 0: Wide stance - LEFT leg forward, RIGHT leg back
2. Frame 1: Standing - both legs together
3. Frame 2: Wide stance - RIGHT leg forward, LEFT leg back

Each frame MUST look different! Different leg positions!

16x16 grid. Use: @ (body) # (detail) + (light) = (medium) - (shadow) . (outline) space (empty)

Return ONLY this exact JSON format:
{{
  "f0": ["line1 (16 chars)", "line2", ... 16 lines total],
  "f1": ["line1 (16 chars)", "line2", ... 16 lines total],
  "f2": ["line1 (16 chars)", "line2", ... 16 lines total]
}}

No other text. Just the JSON."""


async def generate_3_frames(char_desc: str, direction: str, model: str, max_retries: int = 3) -> Optional[dict]:
    """Generate 3 frames with retries"""

    for attempt in range(max_retries):
        if attempt > 0:
            print(f"    Retry {attempt}...")

        prompt = create_3frame_prompt(char_desc, direction)
        response = await call_ollama(prompt, model)

        if not response:
            continue

        data = parse_json_response(response)

        if data and "f0" in data and "f1" in data and "f2" in data:
            # Validate and fix frames
            try:
                frames = {
                    "f0": fix_frame(data["f0"]),
                    "f1": fix_frame(data["f1"]),
                    "f2": fix_frame(data["f2"])
                }

                # Check they're actually different
                if frames["f0"] == frames["f1"] == frames["f2"]:
                    print(f"    ⚠ All frames identical, retrying...")
                    continue

                return frames

            except Exception as e:
                print(f"    ⚠ Frame validation failed: {e}")
                continue
        else:
            print(f"    ⚠ Invalid response structure")
            if data:
                print(f"    Got keys: {list(data.keys())}")

    return None


async def generate_all_frames(char_desc: str, model: str = "qwen2.5:7b"):
    """Generate all walk frames"""

    print(f"Generating walk animation: '{char_desc}'")
    print(f"Model: {model}")
    print("=" * 60)

    all_frames = {}
    directions = ["down", "up", "left", "right"]

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
        print(f"\nDirection: {direction}")
        print(f"  Generating 3 frames...", end=" ")

        frames = await generate_3_frames(char_desc, direction, model)

        if frames:
            print("✓")
            # Add with proper naming
            all_frames[f"walk_{direction}_0"] = frames["f0"]
            all_frames[f"walk_{direction}_1"] = frames["f1"]
            all_frames[f"walk_{direction}_2"] = frames["f2"]
        else:
            print("✗ FAILED")
            # Create fallback frames
            print(f"  Using fallback frames...")
            fallback = [" " * 16] * 16
            all_frames[f"walk_{direction}_0"] = fallback
            all_frames[f"walk_{direction}_1"] = fallback
            all_frames[f"walk_{direction}_2"] = fallback

    # Save result
    result = {
        "color_map": color_map,
        "frames": all_frames
    }

    output_file = "walk_robust.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)

    print(f"\n{'=' * 60}")
    print(f"✓ Generated {len(all_frames)} total frames")
    print(f"✓ Saved to: {output_file}")

    # Preview
    if "walk_down_1" in all_frames:
        print(f"\nPreview walk_down_1:")
        for i, line in enumerate(all_frames["walk_down_1"][:10]):
            print(f"  {i:2d}: {line}")
        print("  ...")

    return result


async def main():
    if len(sys.argv) < 2:
        print("Usage: generate_robust.py <description> [model]")
        print("\nExamples:")
        print("  python generate_robust.py 'red warrior'")
        print("  python generate_robust.py 'blue mage' qwen2.5:7b")
        sys.exit(1)

    description = sys.argv[1]
    model = sys.argv[2] if len(sys.argv) > 2 else "qwen2.5:7b"

    await generate_all_frames(description, model)


if __name__ == "__main__":
    asyncio.run(main())
