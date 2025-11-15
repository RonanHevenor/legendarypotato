#!/usr/bin/env python3
"""
Test OpenRouter API with GPT-5 nano
"""

import asyncio
import json
import httpx
import os

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY environment variable not set. Please set it or create a .env file.")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


async def test_openrouter():
    """Test basic request to OpenRouter GPT-5 nano"""

    print("Testing OpenRouter GPT-5 nano...")
    print("=" * 60)

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "openai/gpt-4o-mini",  # Start with a known working model
        "messages": [
            {
                "role": "user",
                "content": "Say 'Hello, I am working!' and nothing else."
            }
        ]
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            print("Sending request...")
            response = await client.post(
                OPENROUTER_URL,
                headers=headers,
                json=payload
            )
            response.raise_for_status()

            result = response.json()
            print(f"\n✓ Success!")
            print(f"Response: {result['choices'][0]['message']['content']}")
            print(f"Model used: {result.get('model', 'unknown')}")

            return result

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


async def test_ascii_generation():
    """Test ASCII art generation with OpenRouter"""

    print("\n\nTesting ASCII art generation...")
    print("=" * 60)

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    prompt = """Create a simple 16x16 ASCII art of a warrior character facing down.

Use only these characters: @ # + = - . (space)
Return ONLY this JSON format:

{
  "frame": [
    "                ",
    "      ....      ",
    (14 more lines - exactly 16 total)
  ]
}

Make a simple humanoid with head, body, arms, legs. Each line must be exactly 16 characters."""

    payload = {
        "model": "openai/gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "response_format": { "type": "json_object" }
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            print("Generating ASCII art...")
            response = await client.post(
                OPENROUTER_URL,
                headers=headers,
                json=payload
            )
            response.raise_for_status()

            result = response.json()
            content = result['choices'][0]['message']['content']

            print(f"\n✓ Generated!")
            print(f"Raw response length: {len(content)} chars")

            # Parse JSON
            data = json.loads(content)

            if "frame" in data:
                print(f"\nASCII Art Preview:")
                for i, line in enumerate(data["frame"]):
                    print(f"  {i:2d}: {line} ({len(line)} chars)")

                # Save
                with open("openrouter_test.json", 'w') as f:
                    json.dump(data, f, indent=2)
                print(f"\n✓ Saved to openrouter_test.json")

            return data

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


async def main():
    # Test 1: Basic connectivity
    await test_openrouter()

    # Test 2: ASCII generation
    await test_ascii_generation()


if __name__ == "__main__":
    asyncio.run(main())
