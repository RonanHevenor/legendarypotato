# Graphics Improvements

This document outlines all the graphics enhancements made to Legendary Potato.

## Overview

The game graphics have been completely overhauled from basic 16x16 pixel sprites to a modern, polished visual experience with:
- Higher resolution sprites (32x32)
- Advanced shader effects
- Particle systems
- Screen shake and camera effects
- Enhanced UI with better feedback

## New Assets Created

### Sprites
1. **character_hd.png** (96x128) - Higher quality player character with better detail
   - 32x32 pixel frames
   - Better color palette with armor, skin tones, and boots
   - 4 directions × 3 animation frames

2. **enemy_clanker.png** (96x128) - Mechanical enemy sprites
   - Metallic robot design with glowing red eyes
   - Blue core glow effect
   - Distinct mechanical appearance fitting the "Clankers" theme

3. **tiles_hd.png** (256x256) - Enhanced tileset
   - Stone floor tiles with texture variation
   - 3D-looking walls with depth and highlights
   - Better color gradients

### UI Graphics
1. **ui_panel.png** (400x100) - Panel background with border
2. **health_bar_bg.png** (200x20) - Health bar container
3. **health_bar_fill.png** (196x16) - Gradient health bar fill

### Background
1. **bg_stars.png** (512x512) - Starfield background with parallax scrolling

## New Scripts

### Visual Effects

#### camera_effects.gd
Adds screen shake effects for combat feedback:
- `shake(amount)` - Direct shake with specified intensity
- `trauma_shake(trauma)` - Trauma-based shake (0-1 scale)
- Automatic decay over time

#### Particle Systems

1. **hit_effect.gd** - Blood/impact particles on damage
   - 20 particles, 0.5s lifetime
   - Red coloration
   - Explosive emission

2. **death_particles.gd** - Enemy death explosion
   - 30 particles, 1.0s lifetime
   - Smoke/grey coloration
   - Auto-cleanup

3. **attack_particles.gd** - Attack slash effects
   - 15 particles, 0.3s lifetime
   - White/yellow flash
   - Directional emission

4. **ambient_particles.gd** - Background atmosphere
   - 50 continuous particles
   - Slow floating dust effect
   - Adds depth to scenes

### UI Components

#### health_bar.gd
Dynamic health bar with color coding:
- Green (>60% health)
- Yellow (30-60% health)
- Red (<30% health)
- Smooth scaling animation

## Shaders

All shaders are located in `assets/shaders/`:

### Combat Shaders

1. **hit_flash.gdshader** - Flash effect when taking damage
   - Configurable flash color (default: red)
   - Blend amount control
   - Preserves sprite alpha

2. **outline.gdshader** - Character/enemy outlines
   - Configurable outline color and width
   - Perfect for highlighting selected units
   - Smooth anti-aliased edges

3. **glow.gdshader** - Glowing effects
   - For power-ups, special enemies, or effects
   - Configurable intensity and color

### Post-Processing Shaders

1. **vignette.gdshader** - Darkens screen edges
   - Focuses attention on center
   - Adjustable intensity and opacity

2. **chromatic_aberration.gdshader** - RGB color split
   - Retro/glitch effect
   - Subtle by default, can be increased for damage states

3. **pixelate.gdshader** - Pixelation effect
   - Maintains retro aesthetic
   - Adjustable pixel size

4. **parallax_bg.gdshader** - Scrolling background
   - Animated starfield
   - Configurable speed and tint

## Integration Changes

### Player (scripts/player.gd)
- Added camera reference for screen shake
- Added hit particle effects
- Screen shake on successful attacks (3.0 intensity)
- Screen shake when taking damage (5.0 intensity)
- Particle emission on damage

### Enemy (scripts/enemy.gd)
- Added camera reference for screen shake
- Added hit particle effects
- Screen shake on damage (2.0 intensity)
- Death animation with fade and scale
- Larger screen shake on death (4.0 intensity)

### Combat UI (scripts/combat_ui.gd)
- Improved damage numbers with:
  - Larger font size (24px)
  - Black outline for visibility
  - Pop-up scale animation
  - Better floating animation

## How to Use

### Adding Screen Shake

From any script that can access the camera:
```gdscript
var camera = get_viewport().get_camera_2d()
if camera and camera.has_method("shake"):
    camera.shake(5.0)  # Intensity
```

### Adding Particle Effects

1. Instance the particle scene in your node
2. Call `emit_particles()` or set `emitting = true`
3. For death particles, they auto-cleanup

### Applying Shaders

In Godot editor:
1. Select your Sprite2D/AnimatedSprite2D
2. In Inspector → CanvasItem → Material
3. Create new ShaderMaterial
4. Load the desired .gdshader file
5. Adjust uniform parameters

### Using Health Bars

```gdscript
var health_bar = $HealthBar
health_bar.max_value = 100
health_bar.set_value(75)  # Updates display and color
```

## Performance Notes

- All particle systems use CPUParticles2D for compatibility
- Shaders are optimized for 2D rendering
- Background parallax is lightweight
- Screen shake has automatic decay to prevent performance issues

## Future Enhancements

Potential additions:
- Trail effects for fast-moving objects
- More elaborate death animations
- Weather effects (rain, snow)
- Dynamic lighting system
- Sprite deformation on impact
- More elaborate UI transitions
- Sound-reactive visual effects

## Credits

All graphics and shaders created with:
- Python PIL (Pillow) for sprite generation
- GLSL shaders for visual effects
- GDScript for particle systems and effects
