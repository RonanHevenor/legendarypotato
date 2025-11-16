extends Node
## Loads AI-generated character sprites and applies them to the player

signal progress_updated(progress: int)
signal generation_complete(success: bool)

const FRAME_SIZE = 16  # Size of each frame in the sprite sheet
const SCALE = 1  # Match default sprite size (16px)
const SPRITE_RENDER_SCALE = 1.0  # Match default character size
const PROGRESS_CHECK_INTERVAL = 0.5  # How often to check progress
const MAX_GENERATION_TIME = 480.0  # Maximum time to wait for generation

var progress_timer: Timer
var generation_thread: Thread
var thread_result: Dictionary
var log_path: String
var last_progress: int = 0
var elapsed: float = 0.0
var max_wait_time: float = 480.0
var sprite_path: String
var json_path: String
var target_player: Node

func _ready():
	# Create timer for non-blocking progress checks
	progress_timer = Timer.new()
	progress_timer.wait_time = PROGRESS_CHECK_INTERVAL
	progress_timer.timeout.connect(_check_progress)
	add_child(progress_timer)

func _check_progress():
	if not generation_thread or not generation_thread.is_alive():
		# Thread finished
		progress_timer.stop()
		_finish_generation()
		return

	elapsed += progress_timer.wait_time

	# Check if timed out
	if elapsed >= MAX_GENERATION_TIME:
		progress_timer.stop()
		push_error("Generation timed out after " + str(MAX_GENERATION_TIME) + " seconds")
		generation_complete.emit(false)
		return

	# Try to read progress from log file
	if FileAccess.file_exists(log_path):
		var file = FileAccess.open(log_path, FileAccess.READ)
		if file:
			var content = file.get_as_text()
			file.close()

			# Look for PROGRESS:XX lines
			var lines = content.split("\n", false)  # Don't include empty strings
			for line in lines:
				if "PROGRESS:" in line:
					var parts = line.split("PROGRESS:")
					if parts.size() > 1:
						var progress_str = parts[1].strip_edges()
						if progress_str.is_valid_int():
							var progress = int(progress_str)
							if progress >= 0 and progress <= 100 and progress > last_progress:
								last_progress = progress
								progress_updated.emit(progress)

	# Also provide time-based estimate if no progress from log
	if last_progress == 0:
		var estimated_progress = min(int((elapsed / MAX_GENERATION_TIME) * 90), 90)
		if estimated_progress > last_progress:
			progress_updated.emit(estimated_progress)

func _finish_generation():
	if not generation_thread:
		return

	# Wait for thread to finish
	generation_thread.wait_to_finish()

	var exit_code = thread_result.exit_code
	var output = thread_result.output

	print("Exit code: " + str(exit_code))
	print("Output: " + str(output))

	if exit_code != 0:
		push_error("Failed to generate character. Exit code: " + str(exit_code))
		push_error("Output: " + str(output))
		generation_complete.emit(false)
		return

	print("Generation complete!")
	progress_updated.emit(95)

	# Verify JSON was created
	if not FileAccess.file_exists(json_path):
		push_error("JSON file was not created!")
		generation_complete.emit(false)
		return

	print("JSON file confirmed at: " + json_path)

	# Convert JSON to sprite sheet
	var base_dir = ProjectSettings.globalize_path("res://").get_base_dir()
	var converter_path = base_dir + "/ai_animation/ascii_to_sprite.py"
	var venv_python = base_dir + "/ai_animation/venv/bin/python"

	var convert_output = []
	var convert_exit_code = OS.execute(
		venv_python,
		[converter_path, json_path, sprite_path, "1"],
		convert_output,
		true,
		false
	)

	if convert_exit_code != 0:
		push_error("Failed to convert sprites. Exit code: " + str(convert_exit_code))
		generation_complete.emit(false)
		return

	print("Conversion complete!")
	progress_updated.emit(98)

	# Force reload by clearing cache and loading fresh
	await get_tree().create_timer(0.1).timeout

	# Load and apply the sprite sheet
	var sprite_frames = load_sprite_sheet(sprite_path)
	if sprite_frames and target_player:
		apply_to_player(target_player, sprite_frames)
		progress_updated.emit(100)
		generation_complete.emit(true)
	else:
		push_error("Failed to load sprite sheet")
		generation_complete.emit(false)

## Load a sprite sheet and create SpriteFrames from it
func load_sprite_sheet(image_path: String) -> SpriteFrames:
	# Validate input
	if image_path.is_empty():
		push_error("Image path is empty")
		return null

	# Check if file exists
	if not FileAccess.file_exists(image_path):
		push_error("Image file does not exist: " + image_path)
		return null

	# Load the image
	var image = Image.new()
	var error = image.load(image_path)

	if error != OK:
		push_error("Failed to load image '" + image_path + "' (error code: " + str(error) + ")")
		return null

	# Validate image dimensions (should be multiple of frame size)
	var image_size = image.get_size()
	var expected_width = 3 * FRAME_SIZE  # 3 frames per row
	var expected_height = 4 * FRAME_SIZE  # 4 rows

	if image_size.x < expected_width or image_size.y < expected_height:
		push_error("Image too small. Expected at least " + str(expected_width) + "x" + str(expected_height) +
				  ", got " + str(image_size.x) + "x" + str(image_size.y))
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

	var frame_pixel_size = FRAME_SIZE * SCALE  # 16px per frame

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
	# Validate inputs
	if not player:
		push_error("Player node is null")
		return

	if not sprite_frames:
		push_error("Sprite frames is null")
		return

	var animated_sprite = player.get_node("AnimatedSprite2D")
	if not animated_sprite:
		push_error("Player doesn't have AnimatedSprite2D node")
		return

	# Remember current animation and frame
	var current_animation = animated_sprite.animation
	var was_playing = animated_sprite.is_playing()

	# Apply new sprite frames
	animated_sprite.sprite_frames = sprite_frames

	# Apply render scale to make sprite appear smaller
	animated_sprite.scale = Vector2(SPRITE_RENDER_SCALE, SPRITE_RENDER_SCALE)

	# Try to restore the same animation (or fall back to idle_down)
	if sprite_frames.has_animation(current_animation):
		animated_sprite.animation = current_animation
	else:
		# Find a valid animation to fall back to
		var valid_animations = sprite_frames.get_animation_names()
		if valid_animations.size() > 0:
			animated_sprite.animation = valid_animations[0]  # Use first available animation
		else:
			push_error("No valid animations found in sprite frames")
			return

	# Resume playing if it was playing before
	# Disabled to prevent animation errors
	#if was_playing:
	#	animated_sprite.play()

	print("Successfully loaded new character sprites!")


## Generate and load a new character (non-blocking)
func generate_and_load(character_description: String, player: Node, model: String = "openai/gpt-4o-mini") -> void:
	print("Generating character: " + character_description)
	print("Using model: " + model)

	# Store player reference
	target_player = player

	# Path to generator script
	var base_dir = ProjectSettings.globalize_path("res://").get_base_dir()
	var generator_path = base_dir + "/ai_animation/generate_improved.py"
	var venv_python = base_dir + "/ai_animation/venv/bin/python"
	var output_dir = base_dir + "/ai_animation/"
	log_path = base_dir + "/generation.log"

	print("Python path: " + venv_python)
	print("Generator path: " + generator_path)
	print("Starting generation...")

	# Delete old files first to prevent caching
	json_path = output_dir + "improved_animation.json"
	sprite_path = output_dir + "generated_character.png"

	if FileAccess.file_exists(json_path):
		DirAccess.remove_absolute(json_path)
	if FileAccess.file_exists(sprite_path):
		DirAccess.remove_absolute(sprite_path)
	if FileAccess.file_exists(log_path):
		DirAccess.remove_absolute(log_path)

	print("Deleted old files")
	progress_updated.emit(0)

	# Reset state
	last_progress = 0
	elapsed = 0.0
	thread_result = {"exit_code": -1, "output": []}

	# Start the generator process in background using a thread
	generation_thread = Thread.new()

	generation_thread.start(func():
		var output = []
		var exit_code = OS.execute(
			venv_python,
			[generator_path, character_description, model],
			output,
			true,
			false
		)
		thread_result.exit_code = exit_code
		thread_result.output = output
	)

	# Start the progress monitoring timer (non-blocking)
	progress_timer.start()
