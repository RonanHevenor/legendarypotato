#!/usr/bin/env python3
"""
Generate complete walk animation using OpenRouter GPT-5 nano
Uses excellent prompt engineering for consistent results
"""

import asyncio
import json
import sys
import httpx
import os
from pathlib import Path

# Load .env file if it exists
def load_env():
    env_file = Path(__file__).parent / '.env'
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

load_env()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY environment variable not set. Please set it or create a .env file.")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


async def generate_standing_frame(char_desc: str, direction: str, model: str = "openai/gpt-4o-mini") -> dict:
    """Generate a standing/neutral frame for a direction"""
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    direction_details = {
        "down": "facing TOWARD viewer (front view) - show face, front of body",
        "up": "facing AWAY from viewer (back view) - show back of head, back of body",
        "left": "facing LEFT (side profile) - show left side of body",
        "right": "facing RIGHT (side profile) - show right side of body"
    }

    prompt = f"""Create a 16x16 pixel art {char_desc} STANDING in neutral pose, facing {direction}.

DIRECTION: {direction_details[direction]}

CRITICAL RULES:
1. EXACTLY 16 lines, each EXACTLY 16 characters wide
2. Use ONLY: @ # + = - . and space
3. NO BACKGROUND - use spaces for empty areas
4. Character CENTERED, occupying 60-70% of canvas
5. STANDING POSE - legs together, arms at sides, upright

Character structure:
- HEAD: rows 2-4 (centered)
- BODY/TORSO: rows 5-9 (centered)
- ARMS: at sides, hanging down
- LEGS: rows 10-14, together/touching, straight down

Return EXACTLY 16x16 pixel art.

JSON only:
{{
  "frame": [16 lines of 16 chars each]
}}"""

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "response_format": {"type": "json_object"},
        "temperature": 1.2,
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(OPENROUTER_URL, headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()
            content = result['choices'][0]['message']['content']
            data = json.loads(content)

            if "frame" not in data:
                raise ValueError("No frame in response")

            frame = data["frame"]
            while len(frame) < 16:
                frame.append(" " * 16)
            frame = frame[:16]

            fixed_frame = []
            for line in frame:
                if len(line) < 16:
                    line = line + (" " * (16 - len(line)))
                elif len(line) > 16:
                    line = line[:16]
                fixed_frame.append(line)

            return {"frame": fixed_frame}

    except Exception as e:
        print(f"Error: {e}")
        return {"frame": [" " * 16] * 16}


async def generate_walk_frame(char_desc: str, direction: str, phase: int, base_frame: list[str], model: str = "openai/gpt-4o-mini") -> dict:
    """Generate a walk animation frame based on standing pose"""

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    base_str = "\n".join(base_frame)

    phase_desc = {
        0: "LEFT leg stepping FORWARD, RIGHT leg BACK",
        1: "BOTH legs together STANDING (neutral)",
        2: "RIGHT leg stepping FORWARD, LEFT leg BACK"
    }[phase]

    direction_details = {
        "down": "facing TOWARD viewer (front view)",
        "up": "facing AWAY from viewer (back view)",
        "left": "facing LEFT (side profile)",
        "right": "facing RIGHT (side profile)"
    }

    prompt = f"""Modify this {char_desc} to create a WALK animation frame.

BASE STANDING POSE ({direction_details[direction]}):
{base_str}

CREATE FRAME {phase}: {phase_desc}

YOU MUST MODIFY THE LEG POSITIONS! This is frame {phase} of the walk cycle:
"""

    if phase == 0:
        prompt += """
FRAME 0 SPECIFIC CHANGES:
- LEFT LEG: Move 3-4 pixels FORWARD (front/down)
- RIGHT LEG: Move 2-3 pixels BACK (stay behind)
- LEFT ARM: Swing 2 pixels BACK
- RIGHT ARM: Swing 2 pixels FORWARD
- LEGS MUST BE CLEARLY SEPARATED (split stance)
"""
    elif phase == 1:
        prompt += """
FRAME 1 SPECIFIC CHANGES:
- Keep BOTH LEGS together and centered (standing)
- BOTH ARMS at sides (neutral)
- Body upright
- This should look like the base pose (but confirm it's standing)
"""
    else:  # phase == 2
        prompt += """
FRAME 2 SPECIFIC CHANGES:
- RIGHT LEG: Move 3-4 pixels FORWARD (front/down)
- LEFT LEG: Move 2-3 pixels BACK (stay behind)
- RIGHT ARM: Swing 2 pixels BACK
- LEFT ARM: Swing 2 pixels FORWARD
- LEGS MUST BE CLEARLY SEPARATED - OPPOSITE of frame 0!
"""

    prompt += """

REQUIREMENTS:
1. HEAD stays in EXACT same position as base
2. BODY/TORSO stays vertically aligned (±1 pixel)
3. NO BACKGROUND - maintain spaces
4. Character stays CENTERED and same size
5. MAKE THE CHANGES VISIBLE! Don't just copy the base!

If this is frame 0 or 2, the legs MUST be in different positions (one forward, one back)!
WALKING means MOVING LIMBS!

Return EXACTLY 16x16 pixel art.

JSON only:
{{
  "frame": [16 lines of 16 chars each]
}}"""

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "response_format": {"type": "json_object"},
        "temperature": 1.2,  # Higher temperature for more creative variety
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(OPENROUTER_URL, headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()
            content = result['choices'][0]['message']['content']
            data = json.loads(content)

            if "frame" not in data:
                raise ValueError("No frame in response")

            # Ensure exactly 16 lines
            frame = data["frame"]
            while len(frame) < 16:
                frame.append(" " * 16)
            frame = frame[:16]

            # Ensure each line is exactly 16 chars
            fixed_frame = []
            for line in frame:
                if len(line) < 16:
                    line = line + (" " * (16 - len(line)))
                elif len(line) > 16:
                    line = line[:16]
                fixed_frame.append(line)

            return {"frame": fixed_frame}

    except Exception as e:
        print(f"Error: {e}")
        # Return blank frame on error
        return {"frame": [" " * 16] * 16}


async def generate_all_frames(char_desc: str, model: str = "openai/gpt-4o-mini"):
    """Generate all 12 walk frames"""

    print(f"Generating complete walk animation: '{char_desc}'")
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

    total = 12
    current = 0

    # First, generate a base standing frame for each direction
    base_frames = {}
    for direction in directions:
        print(f"\n{direction.upper()} - generating base standing pose...")
        frame_data = await generate_standing_frame(char_desc, direction, model)
        base_frames[direction] = frame_data["frame"]
        await asyncio.sleep(0.3)

    # Now generate walk frames based on the standing pose
    for direction in directions:
        print(f"\n{direction.upper()} direction - animating walk:")
        for phase in range(3):
            current += 1
            progress = int((current / total) * 100)
            frame_name = f"walk_{direction}_{phase}"
            print(f"  [{current}/{total}] {frame_name}...", end=" ", flush=True)
            print(f"\nPROGRESS:{progress}")

            frame_data = await generate_walk_frame(char_desc, direction, phase, base_frames[direction], model)
            all_frames[frame_name] = frame_data["frame"]

            print("✓")
            await asyncio.sleep(0.3)

    # Create result
    result = {
        "color_map": color_map,
        "frames": all_frames
    }

    # Save
    output_file = "openrouter_animation.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)

    print(f"\n{'=' * 60}")
    print(f"✓ Generated {len(all_frames)} frames")
    print(f"✓ Saved to: {output_file}")

    # Preview
    print(f"\nPreview walk_down_1:")
    for i, line in enumerate(all_frames["walk_down_1"][:12]):
        print(f"  {i:2d}: {line}")
    print("  ...")

    return result


async def main():
    if len(sys.argv) < 2:
        print("Usage: generate_openrouter.py <character_description> [model]")
        print("\nExamples:")
        print("  python generate_openrouter.py 'red warrior'")
        print("  python generate_openrouter.py 'blue wizard' 'anthropic/claude-3-haiku'")
        sys.exit(1)

    description = sys.argv[1]
    model = sys.argv[2] if len(sys.argv) > 2 else "openai/gpt-4o-mini"

    await generate_all_frames(description, model)


if __name__ == "__main__":
    asyncio.run(main())
