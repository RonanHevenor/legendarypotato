# AI Character Animation Generator

Dynamically generate character sprites and animations in-game using AI.

## How It Works

1. **In-game UI**: Press `Tab` while playing to open the character generator
2. **Enter prompt**: Type a character description (e.g., "red warrior", "blue wizard")
3. **Generate**: Press Enter or click Generate button
4. **Wait ~30s**: AI generates 12 animation frames (4 directions × 3 walk frames)
5. **Auto-apply**: Your character sprite changes to the AI-generated one!

## Architecture

```
Player presses Tab → UI appears
Player enters "blue wizard" → Generation starts
├─ Python: generate_improved.py (6 API calls)
│  ├─ Step 1: Generate base character design
│  ├─ Step 2: Create 4 rotations (down, up, left, right)
│  └─ Steps 3-6: Animate each rotation (3 walk frames each)
├─ Output: improved_animation.json (ASCII art + color map)
├─ Python: ascii_to_sprite.py
│  └─ Converts ASCII → PNG sprite sheet (512×512, 8× scale)
└─ Godot: ai_character_loader.gd
   ├─ Loads PNG as ImageTexture
   ├─ Creates SpriteFrames with walk/idle animations
   └─ Applies to player's AnimatedSprite2D
```

## Files

### Python Scripts
- `generate_improved.py` - Main generation script (uses OpenRouter API)
- `ascii_to_sprite.py` - Converts ASCII JSON to PNG sprite sheets
- `mcp_server.py` - MCP server (not used in final implementation)

### Godot Scripts
- `scripts/character_generator_ui.gd` - UI controller (Tab key toggle)
- `scripts/ai_character_loader.gd` - Sprite loader and SpriteFrames creator
- `scenes/ui/character_generator_ui.tscn` - UI scene

### Integration
- Player scene: Added "player" group for UI to find it
- Main scene (room_01.tscn): Added CharacterGeneratorUI instance

## API Details

**Model**: OpenRouter GPT-5-nano (fast, cheap, good for ASCII art)
**Cost**: ~6 API calls per character (~$0.01-0.02)
**Time**: ~30 seconds total

## Manual Testing

Generate a character from command line:
```bash
cd ai_animation
source venv/bin/activate
python generate_improved.py "red warrior"
python ascii_to_sprite.py improved_animation.json generated_character.png 8
```

Preview the sprite sheet: `generated_character.png`

## Known Issues

- GPT-5-nano occasionally doesn't follow JSON format strictly - generation may fail
- Threading in Godot: Uses call_deferred to ensure thread safety
- Generation is blocking (~30s) - UI shows status but game continues in background

## Future Improvements

- Add retry logic for failed generations
- Cache generated characters
- Add preview before applying to player
- Support for different character types (enemies, NPCs)
