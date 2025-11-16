extends Node2D

signal room_ready

@export var room_width = 30
@export var seed = 0
@export var room_height = 20

@onready var floor_layer = $TileMapLayer
@onready var wall_layer = $WallLayer
@onready var ysort = $YSort
var rng = RandomNumberGenerator.new()

# Prop scenes
var prop_scenes = {
	"chest": preload("res://scenes/props/chest.tscn"),
	"pot": preload("res://scenes/props/pot.tscn"),
	"stairs": preload("res://scenes/props/stairs.tscn"),
	"torch": preload("res://scenes/props/torch.tscn"),
	"skull": preload("res://scenes/props/skull.tscn"),
	"door": preload("res://scenes/door/door.tscn")
}

var occupied_positions = []

func _ready():
	# Initialize RNG and seed for variation
	rng = RandomNumberGenerator.new()
	if seed != 0:
		rng.seed = seed
	else:
		rng.randomize()
	generate_room()
	wall_layer.force_update_transform()
	emit_signal("room_ready")

func generate_room():
	occupied_positions.clear()
	floor_layer.clear()
	wall_layer.clear()

	# Generate floor with pattern
	for x in range(-room_width/2, room_width/2):
		for y in range(-room_height/2, room_height/2):
			var floor_tile = get_floor_pattern(x, y)
			floor_layer.set_cell(Vector2i(x, y), 0, floor_tile)

	# Generate outer walls
	generate_perimeter_walls()

	# Add interior structure
	generate_interior_features()

	# Place props strategically
	place_room_features()

func get_floor_pattern(x: int, y: int) -> Vector2i:
	# Create a more structured floor pattern
	var pat_array = [Vector2i(1,1), Vector2i(4,0), Vector2i(6,0)]
	if abs(x) % 4 == 0 and abs(y) % 4 == 0:
		return pat_array.pick_random() # Accent tiles at regular intervals
	elif (x + y) % 8 == 0:
		return pat_array.pick_random()
	return pat_array.pick_random()

func generate_perimeter_walls():
	for x in range(-room_width/2, room_width/2):
		wall_layer.set_cell(Vector2i(x, -room_height/2 - 1), 0, Vector2i(6, 0))
		wall_layer.set_cell(Vector2i(x, room_height/2), 0, Vector2i(6, 0))

	for y in range(-room_height/2, room_height/2 + 1):
		wall_layer.set_cell(Vector2i(-room_width/2 - 1, y), 0, Vector2i(5, 0))
		wall_layer.set_cell(Vector2i(room_width/2, y), 0, Vector2i(5, 0))

func generate_interior_features():
	var layout_type = randi() % 3

	match layout_type:
		0:  # Pillars layout
			create_pillars()
		1:  # Alcoves layout
			create_alcoves()
		2:  # Center room layout
			create_center_room()

func create_pillars():
	# Create 4 pillars in quadrants
	var pillar_positions = [
		Vector2i(-room_width/4, -room_height/4),
		Vector2i(room_width/4, -room_height/4),
		Vector2i(-room_width/4, room_height/4),
		Vector2i(room_width/4, room_height/4)
	]

	for pos in pillar_positions:
		# 2x2 pillar
		for dx in range(-1, 2):
			for dy in range(-1, 2):
				if abs(dx) + abs(dy) <= 1:  # Plus shape
					wall_layer.set_cell(pos + Vector2i(dx, dy), 0, Vector2i(2, 0))
					mark_occupied(pos + Vector2i(dx, dy))

func create_alcoves():
	# Create small alcoves on walls
	var alcove_count = randi() % 3 + 2  # 2-4 alcoves

	for i in range(alcove_count):
		var wall = randi() % 4
		create_alcove(wall)

func create_alcove(wall: int):
	var depth = 2
	match wall:
		0:  # Top
			var x = randi() % (room_width - 8) - room_width/2 + 4
			for dx in range(-2, 3):
				for dy in range(0, depth):
					var pos = Vector2i(x + dx, -room_height/2 - 1 + dy)
					if abs(dx) == 2:  # Side walls
						wall_layer.set_cell(pos, 0, Vector2i(6, 0))
					mark_occupied(pos)
		1:  # Bottom
			var x = randi() % (room_width - 8) - room_width/2 + 4
			for dx in range(-2, 3):
				for dy in range(-depth + 1, 1):
					var pos = Vector2i(x + dx, room_height/2 + dy)
					if abs(dx) == 2:
						wall_layer.set_cell(pos, 0, Vector2i(6, 0))
					mark_occupied(pos)

func create_center_room():
	# Small central structure
	var cx = 0
	var cy = 0
	var size = 4

	for dx in range(-size, size + 1):
		for dy in range(-size, size + 1):
			if abs(dx) == size or abs(dy) == size:
				wall_layer.set_cell(Vector2i(cx + dx, cy + dy), 0, Vector2i(2, 7))
				mark_occupied(Vector2i(cx + dx, cy + dy))

func place_room_features():
	# Place door at top center
	var door_x = (randi() % 3 - 1) * 16  # -16, 0, or 16
	spawn_prop("door", Vector2(door_x, -room_height/2 * 16 + 16))

	# Place torches evenly along walls
	place_wall_torches()

	# Place chests in corners
	place_corner_chests()

	# Place decorative elements
	place_decorations()

func place_wall_torches():
	var torch_spacing = 5

	# Top and bottom walls
	for x in range(-room_width/2 + 3, room_width/2 - 2, torch_spacing):
		if not is_position_occupied(Vector2i(x, -room_height/2 + 1)):
			spawn_prop("torch", Vector2(x * 16, (-room_height/2 + 1) * 16))
		if not is_position_occupied(Vector2i(x, room_height/2 - 1)):
			spawn_prop("torch", Vector2(x * 16, (room_height/2 - 1) * 16))

	# Left and right walls
	for y in range(-room_height/2 + 3, room_height/2 - 2, torch_spacing):
		if not is_position_occupied(Vector2i(-room_width/2 + 1, y)):
			spawn_prop("torch", Vector2((-room_width/2 + 1) * 16, y * 16))
		if not is_position_occupied(Vector2i(room_width/2 - 1, y)):
			spawn_prop("torch", Vector2((room_width/2 - 1) * 16, y * 16))

func place_corner_chests():
	var corners = [
		Vector2((-room_width/2 + 2) * 16, (-room_height/2 + 2) * 16),
		Vector2((room_width/2 - 2) * 16, (-room_height/2 + 2) * 16),
		Vector2((-room_width/2 + 2) * 16, (room_height/2 - 2) * 16),
		Vector2((room_width/2 - 2) * 16, (room_height/2 - 2) * 16)
	]

	# Place 1-2 chests randomly in corners
	var num_chests = randi() % 2 + 1
	corners.shuffle()
	for i in range(num_chests):
		spawn_prop("chest", corners[i])

func place_decorations():
	# Place pots in strategic locations
	var pot_count = randi() % 4 + 3
	for i in range(pot_count):
		var pos = get_clear_position()
		if pos != Vector2.ZERO:
			spawn_prop("pot", pos)

	# Scatter some skulls
	var skull_count = randi() % 3 + 2
	for i in range(skull_count):
		var pos = get_clear_position()
		if pos != Vector2.ZERO:
			spawn_prop("skull", pos)

	# Place stairs near a wall
	var stairs_x = (randi() % (room_width/2) - room_width/4) * 16
	var stairs_y = (room_height/2 - 3) * 16
	spawn_prop("stairs", Vector2(stairs_x, stairs_y))

func spawn_prop(prop_type: String, pos: Vector2):
	if prop_scenes.has(prop_type):
		var prop = prop_scenes[prop_type].instantiate()
		prop.position = pos
		ysort.add_child(prop)

func get_clear_position() -> Vector2:
	var attempts = 20
	for i in range(attempts):
		var x = (randi() % (room_width - 8) - room_width/2 + 4)
		var y = (randi() % (room_height - 8) - room_height/2 + 4)

		if not is_position_occupied(Vector2i(x, y)):
			mark_occupied(Vector2i(x, y))
			return Vector2(x * 16, y * 16)

	return Vector2.ZERO

func is_position_occupied(pos: Vector2i) -> bool:
	return occupied_positions.has(pos)

func mark_occupied(pos: Vector2i):
	if not occupied_positions.has(pos):
		occupied_positions.append(pos)

func set_seed(p_seed: int) -> void:
	seed = p_seed
