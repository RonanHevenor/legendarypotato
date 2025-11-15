extends Node2D

@onready var floor_layer = $TileMapLayer
@onready var wall_layer = $WallLayer

func _ready():
	expand_floor()

func expand_floor():
	# Expand the floor to a much larger area
	var room_width = 50
	var room_height = 40

	# Add more floor tiles
	for x in range(-room_width/2, room_width/2):
		for y in range(-room_height/2, room_height/2):
			# Check if tile doesn't already exist
			if floor_layer.get_cell_source_id(Vector2i(x, y)) == -1:
				# Add floor variation
				var floor_tile = (x + y) % 3  # Pattern-based variation
				floor_layer.set_cell(Vector2i(x, y), 0, Vector2i(floor_tile, 0))

	# Extend walls
	for x in range(-room_width/2, room_width/2):
		wall_layer.set_cell(Vector2i(x, -room_height/2 - 1), 0, Vector2i(0, 6))
		wall_layer.set_cell(Vector2i(x, room_height/2), 0, Vector2i(0, 6))

	for y in range(-room_height/2, room_height/2 + 1):
		wall_layer.set_cell(Vector2i(-room_width/2 - 1, y), 0, Vector2i(1, 6))
		wall_layer.set_cell(Vector2i(room_width/2, y), 0, Vector2i(1, 6))
