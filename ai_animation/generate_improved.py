#!/usr/bin/env python3
"""
Improved generation with 6 API calls for better consistency:
1. Base character
2. 4 rotations (down, up, left, right)
3-6. 3 walk frames for each rotation
"""

import asyncio
import json
import sys
import httpx
import logging

OPENROUTER_API_KEY = "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"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


async def call_openrouter(prompt: str, model: str = "openai/gpt-5-nano") -> dict:
    """Make API call to OpenRouter"""
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "response_format": {"type": "json_object"},
        "temperature": 1.2,  # Higher temperature for more creative variety
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(OPENROUTER_URL, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        content = result['choices'][0]['message']['content']
        return json.loads(content)


def fix_frame(lines: list[str]) -> list[str]:
    """Ensure frame is exactly 16x16"""
    fixed = []
    for line in lines:
        if len(line) < 16:
            line = line + (" " * (16 - len(line)))
        elif len(line) > 16:
            line = line[:16]
        fixed.append(line)
    while len(fixed) < 16:
        fixed.append(" " * 16)
    return fixed[:16]


async def step1_base_character(char_desc: str, model: str) -> dict:
    """Step 1: Generate base character design"""
    print("\n[1/6] Generating base character design...")
    print("PROGRESS:16")  # 1/6 ≈ 16%

    prompt = f"""Create a 16x16 pixel art {char_desc} facing DOWN. EXACTLY 16 lines × 16 chars. Use: @ # + = - . and space.

CRITICAL REQUIREMENTS:
1. NO BACKGROUND - Use ONLY space characters for empty areas around the character
2. Character should be CENTERED and occupy roughly 60-70% of the canvas
3. Leave transparent space (spaces) around the character edges
4. Character ONLY - no floor, no scenery, no background elements
5. Keep character simple and recognizable

Character structure:
- HEAD: rows 2-4 (centered)
- BODY/TORSO: rows 5-9 (centered)
- LEGS: rows 10-14 (centered, facing down)
- ARMS: attached to body sides

Use character meanings:
@ = main body/solid areas
# = medium details
+ = highlights/bright areas
= = secondary body parts
- = light shadows/edges
. = dark outlines
(space) = TRANSPARENT/EMPTY - use liberally around character!

JSON only:
{{
  "base_frame": ["line1", "line2", ...]
}}"""

    data = await call_openrouter(prompt, model)
    base = fix_frame(data["base_frame"])
    print("  ✓ Base character created")
    return {"base_frame": base}


async def step2_rotations(base_frame: list[str], char_desc: str, model: str) -> dict:
    """Step 2: Generate 4 rotations of the base character"""
    print("\n[2/6] Generating 4 directional rotations...")
    print("PROGRESS:33")  # 2/6 ≈ 33%

    base_str = "\n".join(base_frame)

    prompt = f"""Rotate this {char_desc} to 4 directions. Keep EXACT same character design, colors, and proportions. ONLY change the viewing angle.

BASE CHARACTER (facing DOWN):
{base_str}

REQUIREMENTS:
1. MAINTAIN character identity - same design elements in all views
2. NO BACKGROUND in any view - use space characters for transparency
3. Keep character CENTERED in all frames
4. Preserve size and proportions across all views

Direction guidelines:
- DOWN: front view (like the base above)
- UP: back view (show back of head/body)
- LEFT: left side profile
- RIGHT: right side profile (mirror of left, but adjusted for details)

Return 16x16 pixel art for each direction.

JSON only:
{{
  "down": [...],
  "up": [...],
  "left": [...],
  "right": [...]
}}"""

    data = await call_openrouter(prompt, model)

    rotations = {
        "down": fix_frame(data["down"]),
        "up": fix_frame(data["up"]),
        "left": fix_frame(data["left"]),
        "right": fix_frame(data["right"])
    }

    print("  ✓ 4 rotations created")
    return rotations


async def step3_animate_direction(rotation_frame: list[str], direction: str, char_desc: str, model: str) -> dict:
    """Steps 3-6: Generate 3 walk frames for a direction"""

    dir_num = {"down": 3, "up": 4, "left": 5, "right": 6}[direction]
    progress = {3: 50, 4: 66, 5: 83, 6: 100}[dir_num]
    print(f"\n[{dir_num}/6] Animating {direction.upper()} direction (3 walk frames)...")
    print(f"PROGRESS:{progress}")

    # Generate each frame individually for more control
    frames = {}

    for phase in range(3):
        phase_desc = {
            0: "LEFT leg stepping FORWARD (extended), RIGHT leg back (bent), arms swinging opposite",
            1: "STANDING position - BOTH legs straight and together under body, arms at sides",
            2: "RIGHT leg stepping FORWARD (extended), LEFT leg back (bent), arms swinging opposite"
        }[phase]

        rotation_str = "\n".join(rotation_frame)

        prompt = f"""Create ONE specific walk frame for a {char_desc} walking {direction}.

THIS IS FRAME {phase} OF 3 - {phase_desc}

BASE REFERENCE (standing neutral):
{rotation_str}

YOU MUST CREATE A DIFFERENT POSE FROM THE BASE! This is frame {phase}:

FRAME {phase} REQUIREMENTS - BE VERY SPECIFIC:
"""

        if phase == 0:
            prompt += """
- LEFT LEG: Move 3-4 pixels FORWARD from base position
- RIGHT LEG: Move 2-3 pixels BACK from base position
- LEFT ARM: Swing 2 pixels BACK (opposite of leg)
- RIGHT ARM: Swing 2 pixels FORWARD
- Body can tilt slightly forward (1 pixel)
- LEGS MUST BE VISIBLY SPLIT/SEPARATED
"""
        elif phase == 1:
            prompt += """
- BOTH LEGS: Straight, together, centered under body
- BOTH ARMS: Hanging straight at sides, neutral position
- Body upright, centered
- This is the STANDING/NEUTRAL pose
- Legs should be CLOSE TOGETHER or touching
"""
        else:  # phase == 2
            prompt += """
- RIGHT LEG: Move 3-4 pixels FORWARD from base position
- LEFT LEG: Move 2-3 pixels BACK from base position
- RIGHT ARM: Swing 2 pixels BACK (opposite of leg)
- LEFT ARM: Swing 2 pixels FORWARD
- Body can tilt slightly forward (1 pixel)
- LEGS MUST BE VISIBLY SPLIT/SEPARATED - OPPOSITE OF FRAME 0
"""

        prompt += f"""

CRITICAL RULES:
1. HEAD position NEVER changes - keep it identical to reference
2. BODY/TORSO stays in same vertical position (±1 pixel max)
3. NO BACKGROUND - only use spaces for empty areas
4. Character must look NOTICEABLY DIFFERENT from the base reference!
5. Keep character CENTERED and same size

WALKING means MOVING LIMBS! Make the leg positions CLEARLY DIFFERENT!
If generating frame {phase}, the legs MUST be in a different position than standing!

Return EXACTLY 16x16 pixel art.

JSON only:
{{
  "frame": [16 lines of 16 chars each]
}}"""

        data = await call_openrouter(prompt, model)
        frames[phase] = fix_frame(data["frame"])

        # Small delay between frames to avoid rate limiting
        if phase < 2:
            await asyncio.sleep(0.5)

    print(f"  ✓ 3 walk frames for {direction}")
    return frames


def get_color_map(char_desc: str) -> dict:
    """Extract color from description and create color map"""
    desc_lower = char_desc.lower()

    # Define color palettes
    colors = {
        "red": {"@": "#8B0000", "#": "#CD5C5C", "+": "#FFB6C1", "=": "#A52A2A"},
        "blue": {"@": "#00008B", "#": "#4169E1", "+": "#87CEEB", "=": "#1E90FF"},
        "green": {"@": "#006400", "#": "#32CD32", "+": "#90EE90", "=": "#228B22"},
        "yellow": {"@": "#B8860B", "#": "#FFD700", "+": "#FFFFE0", "=": "#DAA520"},
        "purple": {"@": "#4B0082", "#": "#8B008B", "+": "#DDA0DD", "=": "#9370DB"},
        "orange": {"@": "#CC5500", "#": "#FF8C00", "+": "#FFD700", "=": "#FFA500"},
        "pink": {"@": "#C71585", "#": "#FF69B4", "+": "#FFB6C1", "=": "#FF1493"},
        "brown": {"@": "#654321", "#": "#8B4513", "+": "#D2B48C", "=": "#A0522D"},
        "gray": {"@": "#2F4F4F", "#": "#696969", "+": "#D3D3D3", "=": "#808080"},
        "black": {"@": "#000000", "#": "#36454F", "+": "#696969", "=": "#2F2F2F"},
    }

    # Find color in description
    for color_name, palette in colors.items():
        if color_name in desc_lower:
            print(f"Color detected: {color_name}")
            return {**palette, "-": "#D3D3D3", ".": "#696969", " ": "#00000000"}

    # Default to red if no color found
    print("No color detected, using red")
    return {
        "@": "#8B0000", "#": "#CD5C5C", "+": "#FFB6C1", "=": "#A52A2A",
        "-": "#D3D3D3", ".": "#696969", " ": "#00000000"
    }


async def generate_complete(char_desc: str, model: str = "openai/gpt-4o-mini"):
    """Generate complete animation with 6 API calls"""

    print(f"Generating animation: '{char_desc}'")
    print(f"Model: {model}")
    print("=" * 60)

    # Step 1: Base character
    base = await step1_base_character(char_desc, model)

    # Step 2: 4 rotations
    rotations = await step2_rotations(base["base_frame"], char_desc, model)

    # Steps 3-6: Animate each rotation
    all_frames = {}
    for direction in ["down", "up", "left", "right"]:
        frames = await step3_animate_direction(rotations[direction], direction, char_desc, model)
        for phase, frame in frames.items():
            all_frames[f"walk_{direction}_{phase}"] = frame

    # Create result with dynamic color map
    result = {
        "color_map": get_color_map(char_desc),
        "frames": all_frames
    }

    # Save to absolute path
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(script_dir, "improved_animation.json")
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)

    print(f"\n{'=' * 60}")
    print(f"✓ Generated {len(all_frames)} frames with 6 API calls")
    print(f"✓ Saved to: {output_file}")

    # Preview
    print(f"\nPreview walk_down_1:")
    for i, line in enumerate(all_frames["walk_down_1"][:12]):
        print(f"  {i:2d}: {line}")
    print("  ...")

    return result


async def main():
    if len(sys.argv) < 2:
        print("Usage: generate_improved.py <character_description> [model]")
        print("\nExamples:")
        print("  python generate_improved.py 'red warrior'")
        print("  python generate_improved.py 'blue wizard'")
        sys.exit(1)

    description = sys.argv[1]
    model = sys.argv[2] if len(sys.argv) > 2 else "openai/gpt-4o-mini"

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(message)s',
        handlers=[
            logging.FileHandler('generation.log'),
            logging.StreamHandler()
        ]
    )

    logging.info(f"Starting generation: '{description}' with {model}")
    await generate_complete(description, model)
    logging.info("Generation complete")


if __name__ == "__main__":
    asyncio.run(main())
