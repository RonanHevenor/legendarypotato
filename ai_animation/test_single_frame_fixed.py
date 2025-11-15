#!/usr/bin/env python3
"""
Test script for generating a single animation frame with auto-fixing
"""

import asyncio
import json
import sys
import httpx

OLLAMA_HOST = "http://100.93.108.89:11434"
FRAME_SIZE = 16


async def call_ollama(prompt: str, model: str = "qwen2.5:14b") -> str:
    """Call Ollama LLM with the given prompt"""
    async with httpx.AsyncClient(timeout=300.0) as client:
        response = await client.post(
            f"{OLLAMA_HOST}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "top_p": 0.9,
                    "num_predict": 1000,
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


def create_single_frame_prompt(character_description: str) -> str:
    """Create a prompt for generating a single frame"""
    return f"""You are an expert pixel artist. Create ASCII art for ONE frame of a character.

CHARACTER DESCRIPTION: {character_description}

REQUIREMENTS:
- The frame must be EXACTLY 16 characters wide and 16 lines tall
- Use these characters only: @ # + = - . (space)
- Each character represents one pixel
- Use @ for the darkest/main color (body/armor)
- Use # for secondary color (details)
- Use + for highlights
- Use = for medium tones
- Use - for light tones
- Use . for very light/outline
- Use space for transparent pixels
- Make a simple, recognizable character facing down/forward

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
  "frame": [
    "                ",
    "                ",
    "      ....      ",
    "     .@@@@.     ",
    (12 more lines - EXACTLY 16 total)
  ]
}}

The frame array must have exactly 16 strings, each exactly 16 characters long.
Choose colors that match "{character_description}".
Return ONLY the JSON, nothing else."""


async def test_single_frame(description: str, model: str = "qwen2.5:14b"):
    """Test generating a single frame"""
    print(f"Generating single frame for: '{description}'")
    print(f"Using model: {model}")
    print(f"Ollama server: {OLLAMA_HOST}")
    print("-" * 60)

    try:
        # Create the prompt
        prompt = create_single_frame_prompt(description)

        # Call the LLM
        print("Calling LLM...")
        response = await call_ollama(prompt, model)

        print("\nRaw LLM response:")
        print("=" * 60)
        print(response)
        print("=" * 60)

        # Parse the JSON response
        response = response.strip()

        # Sometimes LLMs wrap JSON in markdown code blocks
        if response.startswith("```"):
            lines = response.split("\n")
            response = "\n".join(lines[1:-1])
            if response.startswith("json"):
                response = response[4:].strip()

        frame_data = json.loads(response)

        # Validate
        if "color_map" not in frame_data or "frame" not in frame_data:
            raise ValueError("Missing color_map or frame in response")

        # Auto-fix the frame size
        print(f"\nOriginal frame: {len(frame_data['frame'])} lines")
        frame_data["frame"] = fix_frame(frame_data["frame"], FRAME_SIZE)
        print(f"Fixed frame: {len(frame_data['frame'])} lines")

        # Save to file
        output_file = "test_single_frame.json"
        with open(output_file, 'w') as f:
            json.dump(frame_data, f, indent=2)

        print(f"\n✓ Frame generated successfully!")
        print(f"✓ Saved to: {output_file}")
        print(f"\nPreview:")
        for i, line in enumerate(frame_data["frame"]):
            print(f"  {i:2d}: {line} ({len(line)} chars)")

        return frame_data

    except json.JSONDecodeError as e:
        print(f"\n✗ JSON Parse Error: {e}")
        print(f"Failed to parse response as JSON")
        return None
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


async def main():
    if len(sys.argv) < 2:
        print("Usage: test_single_frame_fixed.py <character_description> [model]")
        print("\nExamples:")
        print("  python test_single_frame_fixed.py 'red warrior'")
        print("  python test_single_frame_fixed.py 'blue wizard' qwen2.5:7b")
        sys.exit(1)

    description = sys.argv[1]
    model = sys.argv[2] if len(sys.argv) > 2 else "qwen2.5:14b"

    await test_single_frame(description, model)


if __name__ == "__main__":
    asyncio.run(main())
