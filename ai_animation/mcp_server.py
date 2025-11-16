#!/usr/bin/env python3
"""
MCP Server for AI-Generated Character Animations
Generates ASCII art frames that can be converted to pixel sprites
"""

import asyncio
import json
from typing import Any, Dict, List
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import httpx
import logging

# Ollama server configuration
OLLAMA_HOST = "http://100.93.108.89:11434"
DEFAULT_MODEL = "qwen2.5:7b"  # Fast and good at structured JSON output

# Frame definitions for character animations
REQUIRED_FRAMES = {
    "idle_down": 1,
    "idle_up": 1,
    "idle_left": 1,
    "idle_right": 1,
    "walk_down": 4,
    "walk_up": 4,
    "walk_left": 4,
    "walk_right": 4,
}

FRAME_SIZE = 16  # 16x16 pixels


async def call_ollama(prompt: str, model: str = DEFAULT_MODEL) -> str:
    """Call Ollama LLM with the given prompt"""
    try:
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
                        "num_predict": 8000,
                    }
                }
            )
            response.raise_for_status()
            result = response.json()

            if "response" not in result:
                raise ValueError(f"Ollama returned invalid response structure: {result}")

            return result["response"]
    except httpx.TimeoutException:
        raise ValueError(f"Request to Ollama ({model}) timed out after 300 seconds")
    except httpx.HTTPStatusError as e:
        raise ValueError(f"HTTP error {e.response.status_code} from Ollama: {e.response.text}")
    except Exception as e:
        raise ValueError(f"Unexpected error calling Ollama: {str(e)}")


def create_animation_prompt(character_description: str) -> str:
    """Create a detailed prompt for the LLM to generate ASCII art animations"""
    return f"""You are an expert pixel artist. Create ASCII art for a character animation sprite sheet.

CHARACTER DESCRIPTION: {character_description}

REQUIREMENTS:
- Each frame must be EXACTLY 16 characters wide and 16 lines tall
- Use these characters only: @ # + = - . (space)
- Each character represents one pixel
- Use @ for the darkest/main color
- Use # for secondary color
- Use + for highlights
- Use = for medium tones
- Use - for light tones
- Use . for very light/outline
- Use space for transparent pixels
- Create a simple, recognizable character in pixel art style
- Character should face the specified direction
- Walking frames should show slight movement (legs, arms)

Generate frames for these animations:
1. idle_down (1 frame) - character facing down/front, standing still
2. idle_up (1 frame) - character facing up/back, standing still
3. idle_left (1 frame) - character facing left, standing still
4. idle_right (1 frame) - character facing right, standing still
5. walk_down (4 frames) - walking animation facing down
6. walk_up (4 frames) - walking animation facing up
7. walk_left (4 frames) - walking animation facing left
8. walk_right (4 frames) - walking animation facing right

OUTPUT FORMAT - Return ONLY valid JSON, no other text:
{{
  "color_map": {{
    "@": "#HEXCOLOR",
    "#": "#HEXCOLOR",
    "+": "#HEXCOLOR",
    "=": "#HEXCOLOR",
    "-": "#HEXCOLOR",
    ".": "#HEXCOLOR",
    " ": "#00000000"
  }},
  "frames": {{
    "idle_down_0": [
      "                ",
      "                ",
      "line 3 here...",
      ... (16 lines total)
    ],
    "idle_up_0": [...],
    "idle_left_0": [...],
    "idle_right_0": [...],
    "walk_down_0": [...],
    "walk_down_1": [...],
    "walk_down_2": [...],
    "walk_down_3": [...],
    "walk_up_0": [...],
    ... (all frames)
  }}
}}

Choose colors that match the character description. Return ONLY the JSON, nothing else."""


async def generate_character_animation(character_description: str, model: str = DEFAULT_MODEL) -> Dict[str, Any]:
    """Generate ASCII art animation frames using LLM"""

    # Create the prompt
    prompt = create_animation_prompt(character_description)

    # Call the LLM
    response = await call_ollama(prompt, model)

    # Parse the JSON response
    try:
        # Try to extract JSON from the response
        response = response.strip()

        # Sometimes LLMs wrap JSON in markdown code blocks
        if response.startswith("```"):
            lines = response.split("\n")
            response = "\n".join(lines[1:-1])  # Remove first and last line
            if response.startswith("json"):
                response = response[4:].strip()

        animation_data = json.loads(response)

        # Validate the structure
        if "color_map" not in animation_data or "frames" not in animation_data:
            raise ValueError("Missing color_map or frames in response")

        # Validate all required frames are present
        expected_frames = []
        for anim_name, count in REQUIRED_FRAMES.items():
            for i in range(count):
                expected_frames.append(f"{anim_name}_{i}")

        missing_frames = set(expected_frames) - set(animation_data["frames"].keys())
        if missing_frames:
            raise ValueError(f"Missing frames: {missing_frames}")

        # Validate frame dimensions
        for frame_name, lines in animation_data["frames"].items():
            if len(lines) != FRAME_SIZE:
                raise ValueError(f"Frame {frame_name} has {len(lines)} lines, expected {FRAME_SIZE}")
            for i, line in enumerate(lines):
                if len(line) != FRAME_SIZE:
                    raise ValueError(f"Frame {frame_name} line {i} has {len(line)} chars, expected {FRAME_SIZE}")

        return animation_data

    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse JSON from LLM response: {e}\n\nResponse:\n{response}")
    except Exception as e:
        raise ValueError(f"Invalid animation data: {e}")


# Create the MCP server
app = Server("character-animation-generator")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools"""
    return [
        Tool(
            name="generate_character_animation",
            description="Generate ASCII art character animation frames for a 2D game. "
                       "Creates all required frames (idle and walk in 4 directions) as ASCII art "
                       "with a color mapping that can be converted to pixel sprites.",
            inputSchema={
                "type": "object",
                "properties": {
                    "character_description": {
                        "type": "string",
                        "description": "Description of the character to generate (e.g., 'warrior with red armor', 'wizard in blue robes')"
                    },
                    "model": {
                        "type": "string",
                        "description": f"Ollama model to use (default: {DEFAULT_MODEL})",
                        "default": DEFAULT_MODEL
                    }
                },
                "required": ["character_description"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls"""
    if name == "generate_character_animation":
        character_description = arguments.get("character_description")
        model = arguments.get("model", DEFAULT_MODEL)

        if not character_description:
            raise ValueError("character_description is required")

        try:
            animation_data = await generate_character_animation(character_description, model)

            return [
                TextContent(
                    type="text",
                    text=json.dumps(animation_data, indent=2)
                )
            ]
        except Exception as e:
            return [
                TextContent(
                    type="text",
                    text=f"Error generating animation: {str(e)}"
                )
            ]
    else:
        raise ValueError(f"Unknown tool: {name}")


async def main():
    """Run the MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
