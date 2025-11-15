#!/usr/bin/env python3
"""
Test script for the animation generation pipeline
Can be run directly without full MCP infrastructure
"""

import asyncio
import json
import sys
from pathlib import Path

# Import the generation function directly
from mcp_server import generate_character_animation, OLLAMA_HOST

async def test_generate(description: str, model: str = "qwen2.5:14b"):
    """Test the animation generation"""
    print(f"Generating character animation for: '{description}'")
    print(f"Using model: {model}")
    print(f"Ollama server: {OLLAMA_HOST}")
    print("-" * 60)

    try:
        # Generate the animation data
        print("Calling LLM...")
        animation_data = await generate_character_animation(description, model)

        # Save to file
        output_file = "test_animation.json"
        with open(output_file, 'w') as f:
            json.dump(animation_data, f, indent=2)

        print(f"\n✓ Animation data generated successfully!")
        print(f"✓ Saved to: {output_file}")
        print(f"\nColor map: {list(animation_data['color_map'].keys())}")
        print(f"Frames generated: {len(animation_data['frames'])}")
        print(f"Frame names: {list(animation_data['frames'].keys())}")

        return animation_data

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


async def main():
    if len(sys.argv) < 2:
        print("Usage: test_generation.py <character_description> [model]")
        print("\nExamples:")
        print("  python test_generation.py 'warrior with red armor'")
        print("  python test_generation.py 'wizard in blue robes' qwen2.5:7b")
        print("  python test_generation.py 'knight with silver helmet' llama3.1:latest")
        sys.exit(1)

    description = sys.argv[1]
    model = sys.argv[2] if len(sys.argv) > 2 else "qwen2.5:14b"

    await test_generate(description, model)


if __name__ == "__main__":
    asyncio.run(main())
