#!/usr/bin/env python3
"""
Generate 12 walk animation frames (3 phases × 4 directions)
"""

import asyncio
import json
import sys
import httpx

OLLAMA_HOST = "http://100.93.108.89:11434"
FRAME_SIZE = 16


async def call_ollama(prompt: str, model: str = "qwen2.5:14b") -> str:
    """Call Ollama LLM with the given prompt"""
    async with httpx.AsyncClient(timeout=600.0) as client:
        print("Sending request to Ollama...")
        response = await client.post(
            f"{OLLAMA_HOST}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "top_p": 0.9,
                    "num_predict": 10000,
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
        # Pad or truncate to exact width
        if len(line) < target_size:
            line = line + (" " * (target_size - len(line)))
        elif len(line) > target_size:
            line = line[:target_size]
        fixed_lines.append(line)

    # Pad or truncate to exact height
    while len(fixed_lines) < target_size:
        fixed_lines.append(" " * target_size)

    if len(fixed_lines) > target_size:
        fixed_lines = fixed_lines[:target_size]

    return fixed_lines


def create_walk_frames_prompt(character_description: str) -> str:
    """Create a prompt for generating walk animation frames"""
    return f"""You are an expert pixel artist. Create ASCII art walk animation frames for a character.

CHARACTER DESCRIPTION: {character_description}

REQUIREMENTS:
- Generate 12 frames total: 3 walk phases for each of 4 directions
- Each frame must be EXACTLY 16 characters wide and 16 lines tall
- Use these characters only: @ # + = - . (space)
- Each character represents one pixel
- Use @ for the darkest/main color (body/armor)
- Use # for secondary color (details)
- Use + for highlights
- Use = for medium tones
- Use - for light tones
- Use . for very light/outline
- Use space for transparent pixels

WALK CYCLE:
- Phase 0: Left leg forward, right leg back
- Phase 1: Standing position (both legs together)
- Phase 2: Right leg forward, left leg back

DIRECTIONS:
- down: Character facing down/toward viewer
- up: Character facing up/away from viewer
- left: Character facing left
- right: Character facing right

OUTPUT FORMAT - Return ONLY valid JSON:
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
    "walk_down_0": [
      "                ",
      "      ....      ",
      (14 more lines - EXACTLY 16 total)
    ],
    "walk_down_1": [...],
    "walk_down_2": [...],
    "walk_up_0": [...],
    "walk_up_1": [...],
    "walk_up_2": [...],
    "walk_left_0": [...],
    "walk_left_1": [...],
    "walk_left_2": [...],
    "walk_right_0": [...],
    "walk_right_1": [...],
    "walk_right_2": [...]
  }}
}}

Each frame array must have exactly 16 strings, each exactly 16 characters long.
Choose colors that match "{character_description}".
Return ONLY the JSON, nothing else."""


async def test_walk_frames(description: str, model: str = "qwen2.5:14b"):
    """Test generating walk frames"""
    print(f"Generating walk animation for: '{description}'")
    print(f"Using model: {model}")
    print(f"Ollama server: {OLLAMA_HOST}")
    print("-" * 60)

    try:
        # Create the prompt
        prompt = create_walk_frames_prompt(description)

        # Call the LLM
        print("Calling LLM (this may take 1-2 minutes)...")
        response = await call_ollama(prompt, model)

        print("\n✓ Got response from LLM")
        print(f"Response length: {len(response)} characters")

        # Parse the JSON response
        response = response.strip()

        # Sometimes LLMs wrap JSON in markdown code blocks
        if response.startswith("```"):
            lines = response.split("\n")
            response = "\n".join(lines[1:-1])
            if response.startswith("json"):
                response = response[4:].strip()

        print("Parsing JSON...")
        frame_data = json.loads(response)

        # Validate
        if "color_map" not in frame_data or "frames" not in frame_data:
            raise ValueError("Missing color_map or frames in response")

        expected_frames = [
            "walk_down_0", "walk_down_1", "walk_down_2",
            "walk_up_0", "walk_up_1", "walk_up_2",
            "walk_left_0", "walk_left_1", "walk_left_2",
            "walk_right_0", "walk_right_1", "walk_right_2",
        ]

        print(f"\nReceived frames: {list(frame_data['frames'].keys())}")

        # Auto-fix all frames
        for frame_name in expected_frames:
            if frame_name in frame_data["frames"]:
                frame_data["frames"][frame_name] = fix_frame(
                    frame_data["frames"][frame_name],
                    FRAME_SIZE
                )

        # Save to file
        output_file = "walk_animation.json"
        with open(output_file, 'w') as f:
            json.dump(frame_data, f, indent=2)

        print(f"\n✓ Walk animation generated successfully!")
        print(f"✓ Saved to: {output_file}")
        print(f"\nFrames generated: {len(frame_data['frames'])}")
        print(f"Color palette: {list(frame_data['color_map'].keys())}")

        # Preview first frame
        print("\nPreview of walk_down_0:")
        for line in frame_data["frames"].get("walk_down_0", [])[:8]:
            print(f"  {line}")
        print("  ...")

        return frame_data

    except json.JSONDecodeError as e:
        print(f"\n✗ JSON Parse Error: {e}")
        print("\nSaving raw response to walk_animation_raw.txt for debugging...")
        with open("walk_animation_raw.txt", 'w') as f:
            f.write(response)
        return None
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


async def main():
    if len(sys.argv) < 2:
        print("Usage: test_walk_frames.py <character_description> [model]")
        print("\nExamples:")
        print("  python test_walk_frames.py 'red warrior'")
        print("  python test_walk_frames.py 'blue wizard' qwen2.5:7b")
        sys.exit(1)

    description = sys.argv[1]
    model = sys.argv[2] if len(sys.argv) > 2 else "qwen2.5:14b"

    await test_walk_frames(description, model)


if __name__ == "__main__":
    asyncio.run(main())
