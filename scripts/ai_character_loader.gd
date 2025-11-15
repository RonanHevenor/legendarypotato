extends Node
## Loads AI-generated character sprites and applies them to the player

const FRAME_SIZE = 16  # Size of each frame in the sprite sheet
const SCALE = 8  # How much we scaled up (16px -> 128px)

## Load a sprite sheet and create SpriteFrames from it
func load_sprite_sheet(image_path: String) -> SpriteFrames:
	# Load the image
	var image = Image.new()
	var error = image.load(image_path)

	if error != OK:
		push_error("Failed to load image: " + image_path)
		return null

	# Create texture from image
	var texture = ImageTexture.create_from_image(image)

	# Create new SpriteFrames
	var frames = SpriteFrames.new()

	# Define our animation layout (matches the generator output)
	# Row 0: walk_down (3 frames)
	# Row 1: walk_up (3 frames)
	# Row 2: walk_left (3 frames)
	# Row 3: walk_right (3 frames)
	# Row 4: idle frames (4 frames - down, up, left, right)

	var frame_pixel_size = FRAME_SIZE * SCALE  # 128px

	# Create walk animations
	var directions = ["down", "up", "left", "right"]
	for dir_idx in range(4):
		var dir_name = directions[dir_idx]

		# Create walk animation
		var walk_anim = "walk_" + dir_name
		frames.add_animation(walk_anim)
		frames.set_animation_speed(walk_anim, 10.0)
		frames.set_animation_loop(walk_anim, true)

		# Add 3 walk frames from the sprite sheet
		for frame_idx in range(3):
			var atlas = AtlasTexture.new()
			atlas.atlas = texture
			atlas.region = Rect2(
				frame_idx * frame_pixel_size,  # x
				dir_idx * frame_pixel_size,     # y
				frame_pixel_size,              # width
				frame_pixel_size               # height
			)
			frames.add_frame(walk_anim, atlas)

		# Create idle animation (using middle frame of walk for simplicity)
		var idle_anim = "idle_" + dir_name
		frames.add_animation(idle_anim)
		frames.set_animation_speed(idle_anim, 5.0)
		frames.set_animation_loop(idle_anim, true)

		# Use frame 1 (middle/standing frame) for idle
		var idle_atlas = AtlasTexture.new()
		idle_atlas.atlas = texture
		idle_atlas.region = Rect2(
			1 * frame_pixel_size,          # x (middle frame)
			dir_idx * frame_pixel_size,    # y
			frame_pixel_size,
			frame_pixel_size
		)
		frames.add_frame(idle_anim, idle_atlas)

	return frames


## Apply sprite frames to an AnimatedSprite2D
func apply_to_player(player: Node, sprite_frames: SpriteFrames) -> void:
	var animated_sprite = player.get_node("AnimatedSprite2D")
	if not animated_sprite:
		push_error("Player doesn't have AnimatedSprite2D node")
		return

	# Remember current animation and frame
	var current_animation = animated_sprite.animation
	var was_playing = animated_sprite.is_playing()

	# Apply new sprite frames
	animated_sprite.sprite_frames = sprite_frames

	# Try to restore the same animation (or fall back to idle_down)
	if sprite_frames.has_animation(current_animation):
		animated_sprite.animation = current_animation
	else:
		animated_sprite.animation = "idle_down"

	# Resume playing if it was playing before
	if was_playing:
		animated_sprite.play()

	print("Successfully loaded new character sprites!")


## Generate and load a new character
func generate_and_load(character_description: String, player: Node) -> bool:
	print("Generating character: " + character_description)

	# Path to generator script
	var base_dir = ProjectSettings.globalize_path("res://").get_base_dir()
	var generator_path = base_dir + "/ai_animation/generate_improved.py"
	var venv_python = base_dir + "/ai_animation/venv/bin/python"
	var output_dir = base_dir + "/ai_animation/"

	print("Python path: " + venv_python)
	print("Generator path: " + generator_path)
	print("Starting generation (this will take ~30s)...")

	# Delete old files first to prevent caching
	var json_path = output_dir + "improved_animation.json"
	var sprite_path = output_dir + "generated_character.png"

	if FileAccess.file_exists(json_path):
		DirAccess.remove_absolute(json_path)
	if FileAccess.file_exists(sprite_path):
		DirAccess.remove_absolute(sprite_path)

	print("Deleted old files")

	# Run the generator
	var output = []
	var exit_code = OS.execute(
		venv_python,
		[generator_path, character_description],
		output,
		true,  # blocking
		false  # don't open console
	)

	print("Exit code: " + str(exit_code))
	print("Output: " + str(output))

	if exit_code != 0:
		push_error("Failed to generate character. Exit code: " + str(exit_code))
		push_error("Output: " + str(output))
		return false

	print("Generation complete!")

	# Verify JSON was created
	if not FileAccess.file_exists(json_path):
		push_error("JSON file was not created!")
		return false

	print("JSON file confirmed at: " + json_path)

	# Convert JSON to sprite sheet
	var converter_path = base_dir + "/ai_animation/ascii_to_sprite.py"

	var convert_output = []
	exit_code = OS.execute(
		venv_python,
		[converter_path, json_path, sprite_path, "8"],
		convert_output,
		true,
		false
	)

	if exit_code != 0:
		push_error("Failed to convert sprites. Exit code: " + str(exit_code))
		return false

	print("Conversion complete!")

	# Force reload by clearing cache and loading fresh
	# Wait a moment for file to flush
	await get_tree().create_timer(0.1).timeout

	# Load and apply the sprite sheet
	var sprite_frames = load_sprite_sheet(sprite_path)
	if sprite_frames:
		apply_to_player(player, sprite_frames)
		return true
	else:
		push_error("Failed to load sprite sheet")
		return false
