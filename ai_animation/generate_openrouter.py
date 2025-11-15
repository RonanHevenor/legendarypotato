#!/usr/bin/env python3
"""
Generate complete walk animation using OpenRouter GPT-5 nano
Uses excellent prompt engineering for consistent results
"""

import asyncio
import json
import sys
import httpx

OPENROUTER_API_KEY = "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"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


def create_expert_prompt(character_desc: str, direction: str, phase: int) -> str:
    """Create an expert-level prompt for GPT-5 nano"""

    phase_instructions = {
        0: "LEFT leg forward, RIGHT leg back - character mid-stride",
        1: "BOTH legs together - standing position",
        2: "RIGHT leg forward, LEFT leg back - opposite of phase 0"
    }

    direction_details = {
        "down": "facing TOWARD viewer (front view) - show face, front of body",
        "up": "facing AWAY from viewer (back view) - show back of head, back of body",
        "left": "facing LEFT (side profile) - show left side of body",
        "right": "facing RIGHT (side profile) - show right side of body"
    }

    return f"""You are a pixel art expert creating a 16x16 character sprite for a retro game.

CHARACTER: {character_desc}
DIRECTION: {direction_details[direction]}
ANIMATION: Walk cycle - {phase_instructions[phase]}

CRITICAL RULES:
1. EXACTLY 16 lines, each EXACTLY 16 characters wide
2. Use ONLY these characters: @ # + = - . and space
3. Character meanings:
   @ = main body/armor (dark)
   # = details (medium)
   + = highlights (bright)
   = = medium tones
   - = shadows/outlines (light)
   . = dark outline
   (space) = transparent/empty

4. Create a simple humanoid figure:
   - HEAD: 2-3 pixels tall at top
   - BODY: 4-6 pixels tall in middle
   - ARMS: 2 pixels wide on each side
   - LEGS: Split in middle, 4-5 pixels tall
   - Total height: 12-14 pixels
   - Centered horizontally

5. For walk animation phase {phase}:
   {phase_instructions[phase]}

EXAMPLE FORMAT (different character):
```

      ....
      @@@@
      @@@@
       ##
      +##+
     +====+
     +####+
      +##+
      +##+
     -    -
     -    -
    -      -
   -        -


```

Return ONLY valid JSON:
{{
  "frame": [
    "                ",
    "                ",
    (14 more lines exactly 16 chars each)
  ]
}}

NO markdown, NO explanation, ONLY the JSON object."""


async def generate_frame(char_desc: str, direction: str, phase: int, model: str = "openai/gpt-4o-mini") -> dict:
    """Generate a single frame using OpenRouter"""

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    prompt = create_expert_prompt(char_desc, direction, phase)

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "response_format": {"type": "json_object"},
        "temperature": 0.7,
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

    for direction in directions:
        print(f"\n{direction.upper()} direction:")
        for phase in range(3):
            current += 1
            frame_name = f"walk_{direction}_{phase}"
            print(f"  [{current}/{total}] {frame_name}...", end=" ", flush=True)

            frame_data = await generate_frame(char_desc, direction, phase, model)
            all_frames[frame_name] = frame_data["frame"]

            print("✓")

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
