# Graphics Quick Start Guide

## What Was Fixed

The graphics have been completely overhauled! Here's what changed:

### Before
- Tiny 16x16 pixel sprites
- No visual feedback
- Basic 8-bit graphics
- No effects or polish

### After
- Sharp 32x32 pixel sprites
- Screen shake on every hit
- Particle effects everywhere
- Professional shaders
- Smooth animations
- Modern UI with health bars

## Quick Setup in Godot

### 1. Add Camera with Screen Shake

In your main scene:
1. Add a Camera2D node
2. Attach `scripts/camera_effects.gd`
3. Make it current camera

### 2. Add Particles to Player/Enemies

For each character:
1. Add CPUParticles2D child node
2. Name it "HitParticles"
3. Attach `scripts/hit_effect.gd`

### 3. Use New Sprites

Player:
- Open `scenes/player/player.tscn`
- In AnimatedSprite2D, change texture to `assets/sprites/character_hd.png`
- Update frame regions to 32x32 grid

Enemies:
- Use `assets/sprites/enemy_clanker.png`
- Same 32x32 grid layout

Tiles:
- Use `assets/sprites/tiles_hd.png` in TileMap
- Set tile size to 32x32

### 4. Add Shaders (Optional but Awesome)

For damage flash:
1. Select player sprite
2. Material → New ShaderMaterial
3. Shader → Load `assets/shaders/hit_flash.gdshader`
4. Animate `flash_amount` parameter when taking damage

For outlines:
1. Same process with `assets/shaders/outline.gdshader`
2. Set outline_color to white/yellow
3. Great for highlighting!

### 5. Add Screen Transitions

In your UI layer:
1. Add ColorRect node (covers full screen)
2. Attach `scripts/screen_transition.gd`
3. Call `fade_in()` or `fade_out()` for level changes

## Code Examples

### Screen Shake on Hit
```gdscript
func take_damage(amount):
    var camera = get_viewport().get_camera_2d()
    if camera and camera.has_method("shake"):
        camera.shake(5.0)  # Big shake
```

### Spawn Particles
```gdscript
func _on_hit():
    if $HitParticles:
        $HitParticles.emitting = true
```

### Flash on Damage
```gdscript
func take_damage(amount):
    modulate = Color.RED
    await get_tree().create_timer(0.1).timeout
    modulate = Color.WHITE
```

### Health Bar Update
```gdscript
func update_health(current, maximum):
    $HealthBar.max_value = maximum
    $HealthBar.set_value(current)
```

### Level Transition
```gdscript
func change_level():
    await $ScreenTransition.fade_in(0.5)
    get_tree().change_scene_to_file("res://scenes/next_level.tscn")
    await $ScreenTransition.fade_out(0.5)
```

## Asset Reference

**High Priority (Use These First)**
- `character_hd.png` - Better player sprite
- `enemy_clanker.png` - Cool robot enemies
- `camera_effects.gd` - Screen shake (MUST HAVE)
- `hit_effect.gd` - Blood splatter particles

**Medium Priority**
- `tiles_hd.png` - Better floors/walls
- `health_bar.gd` - Fancy health bars
- `hit_flash.gdshader` - Damage flash effect

**Nice to Have**
- `ambient_particles.gd` - Floating dust
- `vignette.gdshader` - Dramatic lighting
- `screen_transition.gd` - Smooth fades
- `bg_stars.png` - Animated background

## Testing

Run the game and:
1. Take damage - should see: red flash, screen shake, particles
2. Attack enemy - should see: screen shake, impact effect
3. Kill enemy - should see: big shake, death animation, fade out
4. Check UI - health bar should change colors

## Troubleshooting

**No screen shake?**
- Check camera has `camera_effects.gd` attached
- Verify camera is set as current

**No particles?**
- Node must be named "HitParticles"
- Must be child of player/enemy
- Check script is attached

**Sprites look wrong?**
- Verify texture filter is set to "Nearest" for pixel art
- Check frame regions are 32x32
- Make sure you're using the _hd.png versions

**Shaders not working?**
- Material must be ShaderMaterial (not CanvasItemMaterial)
- Shader file must be .gdshader format
- Check uniform parameters are set

## Next Steps

Once basics work:
1. Tune screen shake values for feel
2. Adjust particle colors to match theme
3. Add more shader effects
4. Create custom particle patterns
5. Add sound effects to match visuals

The game should now look MUCH better! 🎮✨
