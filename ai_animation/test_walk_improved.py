#!/usr/bin/env python3
"""
Generate walk animation frames with better prompting and examples
"""

import asyncio
import json
import sys
import httpx

OLLAMA_HOST = "http://100.93.108.89:11434"
FRAME_SIZE = 16


async def call_ollama(prompt: str, model: str = "qwen2.5:7b") -> str:
    """Call Ollama LLM with the given prompt"""
    async with httpx.AsyncClient(timeout=600.0) as client:
        response = await client.post(
            f"{OLLAMA_HOST}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.5,
                    "top_p": 0.9,
                    "num_predict": 12000,
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


def create_improved_prompt(character_description: str) -> str:
    """Create an improved prompt with examples"""
    return f"""You are an expert pixel artist creating a 16x16 character sprite for a game.

CHARACTER: {character_description}

Create 12 walk animation frames (3 phases × 4 directions).

PIXEL ART RULES:
- Each frame is 16×16 characters (one char = one pixel)
- Characters: @ (body) # (details) + (bright) = (medium) - (light) . (outline) (space=transparent)
- Make a recognizable humanoid character with head, body, arms, legs
- Center the character in the frame
- Character should be about 12-14 pixels tall

EXAMPLE FRAME (warrior facing down):
```

    ....
   .++++.
   .++++.
  ..####..
 .@@@@@@@@.
.@@@@##@@@@.
.@@@@##@@@@.
 .@@@@@@@@.
  .@@@@@@.
  .@..@..
 .@. .@.
.@.  .@.
@.    .@
.      .

```

WALK CYCLE (3 phases):
- Phase 0: Left leg forward, right leg back (wide stance)
- Phase 1: Both legs together (standing)
- Phase 2: Right leg forward, left leg back (wide stance)

For side views, show the character from the side (profile view).
For up views, show the back of the head.

OUTPUT ONLY THIS JSON (no other text):
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
  "frames": {{
    "walk_down_0": [16 lines of 16 chars each],
    "walk_down_1": [16 lines of 16 chars each],
    "walk_down_2": [16 lines of 16 chars each],
    "walk_up_0": [16 lines of 16 chars each],
    "walk_up_1": [16 lines of 16 chars each],
    "walk_up_2": [16 lines of 16 chars each],
    "walk_left_0": [16 lines of 16 chars each],
    "walk_left_1": [16 lines of 16 chars each],
    "walk_left_2": [16 lines of 16 chars each],
    "walk_right_0": [16 lines of 16 chars each],
    "walk_right_1": [16 lines of 16 chars each],
    "walk_right_2": [16 lines of 16 chars each]
  }}
}}

Make each frame unique with different leg positions. Use colors matching "{character_description}"."""


async def test_improved(description: str, model: str = "qwen2.5:7b"):
    """Test with improved prompt"""
    print(f"Generating improved walk animation for: '{description}'")
    print(f"Using model: {model}")
    print("-" * 60)

    try:
        prompt = create_improved_prompt(description)
        print("Calling LLM with improved prompt...")
        response = await call_ollama(prompt, model)

        print(f"\n✓ Got response ({len(response)} chars)")

        # Parse JSON
        response = response.strip()
        if response.startswith("```"):
            lines = response.split("\n")
            response = "\n".join(lines[1:-1])
            if response.startswith("json"):
                response = response[4:].strip()

        frame_data = json.loads(response)

        if "color_map" not in frame_data or "frames" not in frame_data:
            raise ValueError("Missing color_map or frames")

        # Auto-fix all frames
        for frame_name in frame_data["frames"]:
            frame_data["frames"][frame_name] = fix_frame(
                frame_data["frames"][frame_name], FRAME_SIZE
            )

        # Save
        output_file = "walk_animation_improved.json"
        with open(output_file, 'w') as f:
            json.dump(frame_data, f, indent=2)

        print(f"\n✓ Saved to: {output_file}")
        print(f"Frames: {len(frame_data['frames'])}")

        # Show preview
        print("\nPreview of walk_down_1:")
        for line in frame_data["frames"].get("walk_down_1", []):
            print(f"  {line}")

        return frame_data

    except json.JSONDecodeError as e:
        print(f"\n✗ JSON Parse Error: {e}")
        with open("walk_improved_raw.txt", 'w') as f:
            f.write(response)
        print("Saved raw response to walk_improved_raw.txt")
        return None
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


async def main():
    if len(sys.argv) < 2:
        print("Usage: test_walk_improved.py <character_description> [model]")
        sys.exit(1)

    description = sys.argv[1]
    model = sys.argv[2] if len(sys.argv) > 2 else "qwen2.5:7b"
    await test_improved(description, model)


if __name__ == "__main__":
    asyncio.run(main())
