#!/usr/bin/env python3
"""
Enhanced AI Enemy Generation System
"""

import asyncio
import json
import sys
import logging
import os
import random
from pathlib import Path
from typing import Dict, List, Any, Optional

# Try to import httpx, fall back to mock mode if not available
try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    httpx = None
    HTTPX_AVAILABLE = False
    print("Warning: httpx not available. Running in mock mode.")

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
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

if not HTTPX_AVAILABLE:
    print("Note: Install dependencies with: pip install httpx")
    if OPENROUTER_API_KEY:
        print("API key found - will use real generation when httpx is available")
    else:
        print("No API key found - using mock generation")

# Clanker archetypes - mechanical enemies in a story-driven game
ENEMY_ARCHETYPES = {
    "scout_clanker": {
        "description": "fast reconnaissance robot with basic weapons",
        "behavior": "aggressive_melee",
        "health": 60,
        "speed": 120,
        "damage": 15,
        "story": "Basic patrol units that scout ahead of larger formations"
    },
    "combat_clanker": {
        "description": "heavily armed combat robot with ranged weapons",
        "behavior": "ranged_kiting",
        "health": 100,
        "speed": 70,
        "damage": 25,
        "story": "Standard combat units equipped with projectile weapons"
    },
    "heavy_clanker": {
        "description": "slow but powerful assault robot",
        "behavior": "ferocious_charge",
        "health": 200,
        "speed": 40,
        "damage": 40,
        "story": "Heavy assault units designed for breaking through defenses"
    },
    "repair_clanker": {
        "description": "support robot that repairs other clankers",
        "behavior": "persistent_hunter",
        "health": 80,
        "speed": 60,
        "damage": 10,
        "story": "Support units that maintain and repair other clankers"
    }
}

async def call_openrouter(prompt: str, model: str = "openai/gpt-4o-mini") -> Dict[str, Any]:
    """Make API call to OpenRouter or return mock data"""
    if not HTTPX_AVAILABLE or not OPENROUTER_API_KEY:
        return _generate_mock_response(prompt)

    if httpx is None:
        return _generate_mock_response(prompt)

    try:
        headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_object"},
            "temperature": 1.2,
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(OPENROUTER_URL, headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()
            content = result['choices'][0]['message']['content']

            # Clean JSON
            content = content.strip()
            if content.startswith("```json"): content = content[7:]
            if content.endswith("```"): content = content[:-3]
            content = content.strip()

            return json.loads(content)
    except Exception as e:
        print(f"API call failed: {e}. Using mock data.")
        return _generate_mock_response(prompt)

def _generate_mock_response(prompt: str) -> Dict[str, Any]:
    """Generate mock ASCII art for clankers when API is not available"""
    # Create different mock frames based on clanker type
    if "scout" in prompt.lower():
        mock_frame = [
            "   [===]   ",
            "  /     \\  ",
            " |  o o  | ",
            "  \\  ^  /  ",
            "   |===|   ",
            "  /     \\  ",
            " |       | ",
            "  \\     /  ",
            "   =====   ",
            "  /     \\  ",
            " |       | ",
            "  \\     /  ",
            "   =====   ",
            "    |||    ",
            "    |||    ",
            "   /   \\   "
        ]
    elif "combat" in prompt.lower():
        mock_frame = [
            "   [===]   ",
            "  /     \\  ",
            " |  o o  | ",
            "  \\  ^  /  ",
            "   |===|   ",
            "  / ||| \\  ",
            " | |   | | ",
            "  \\ ||| /  ",
            "   =====   ",
            "  /     \\  ",
            " | ===== | ",
            "  \\     /  ",
            "   =====   ",
            "    |||    ",
            "    |||    ",
            "   /   \\   "
        ]
    elif "heavy" in prompt.lower():
        mock_frame = [
            "  [=====]  ",
            " /       \\ ",
            " |  o o  | ",
            "  \\  ^  /  ",
            "   |===|   ",
            "  /|||||\\  ",
            " | ||||| | ",
            "  \\|||||/  ",
            "   ======= ",
            "  /       \\ ",
            " | ======= | ",
            "  \\       /  ",
            "   ======= ",
            "   |||||||  ",
            "   |||||||  ",
            "  /       \\ "
        ]
    elif "repair" in prompt.lower():
        mock_frame = [
            "   [===]   ",
            "  /     \\  ",
            " |  o o  | ",
            "  \\  +  /  ",
            "   |===|   ",
            "  / +++ \\  ",
            " | +   + | ",
            "  \\ +++ /  ",
            "   =====   ",
            "  /     \\  ",
            " | ===== | ",
            "  \\     /  ",
            "   =====   ",
            "    +++    ",
            "    +++    ",
            "   /   \\   "
        ]
    else:  # default clanker
        mock_frame = [
            "   [===]   ",
            "  /     \\  ",
            " |  o o  | ",
            "  \\  ^  /  ",
            "   |===|   ",
            "  /     \\  ",
            " |       | ",
            "  \\     /  ",
            "   =====   ",
            "  /     \\  ",
            " | ===== | ",
            "  \\     /  ",
            "   =====   ",
            "    |||    ",
            "    |||    ",
            "   /   \\   "
        ]

    return {"frames": {"idle": mock_frame}}

def fix_frame(lines: List[str]) -> List[str]:
    """Ensure frame is exactly 16x16"""
    if not lines: return [" " * 16] * 16

    fixed = []
    for line in lines[:16]:
        line = line.rstrip()
        if len(line) < 16: line = line + (" " * (16 - len(line)))
        else: line = line[:16]
        fixed.append(line)

    while len(fixed) < 16: fixed.append(" " * 16)
    return fixed

async def generate_enemy(archetype: str) -> Dict[str, Any]:
    """Generate a basic enemy"""
    enemy_data = ENEMY_ARCHETYPES.get(archetype, ENEMY_ARCHETYPES["warrior"])

    # Generate simple ASCII art
    prompt = f"""Create a 16x16 pixel art {archetype} enemy: {enemy_data['description']}.
Use @ # + = - . and space. Return JSON: {{"frames": {{"idle": [16 lines of 16 chars each]}}}}"""

    data = await call_openrouter(prompt)
    frames = {"idle": fix_frame(data["frames"]["idle"])}

    enemy = {
        "stats": {
            "archetype": archetype,
            "health": enemy_data["health"],
            "speed": enemy_data["speed"],
            "damage": enemy_data["damage"],
            "behavior": enemy_data["behavior"]
        },
        "color_map": {"@": "#FF0000", "#": "#00FF00", "+": "#0000FF", "=": "#FFFF00", "-": "#FF00FF", ".": "#00FFFF", " ": "#00000000"},
        "frames": frames
    }

    return enemy

async def main():
    if len(sys.argv) < 2:
        print("Usage: generate_enemy.py <archetype>")
        print("Archetypes:", ", ".join(ENEMY_ARCHETYPES.keys()))
        sys.exit(1)

    archetype = sys.argv[1].lower()
    enemy = await generate_enemy(archetype)

    output_file = f"enemy_{archetype}.json"
    with open(output_file, 'w') as f:
        json.dump(enemy, f, indent=2)

    print(f"✓ Enemy generated: {output_file}")

if __name__ == "__main__":
    asyncio.run(main())