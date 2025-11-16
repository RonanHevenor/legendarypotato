extends Node2D

@onready var floor_layer = $TileMapLayer
@onready var wall_layer = $WallLayer

func _ready():
	expand_floor()

func expand_floor():
	# Expand the floor to a much larger area
	var room_width = 60
	var room_height = 50

	# Add more floor tiles with variation for a nice dungeon floor
	for x in range(-room_width/2, room_width/2):
		for y in range(-room_height/2, room_height/2):
			# Add floor variation using multiple tile patterns
			var random_val = randi() % 100
			var floor_tile_x = 0
			var floor_tile_y = 0
			
			# Create a varied floor pattern
			if random_val < 70:
				floor_tile_x = 0  # Main floor tile
				floor_tile_y = 0
			elif random_val < 85:
				floor_tile_x = 1  # Variation 1
				floor_tile_y = 0
			elif random_val < 95:
				floor_tile_x = 2  # Variation 2
				floor_tile_y = 0
			else:
				floor_tile_x = 3  # Variation 3
				floor_tile_y = 0
			
			floor_layer.set_cell(Vector2i(x, y), 0, Vector2i(floor_tile_x, floor_tile_y))

	# Extend walls around the perimeter
	for x in range(-room_width/2, room_width/2):
		wall_layer.set_cell(Vector2i(x, -room_height/2 - 1), 0, Vector2i(0, 6))
		wall_layer.set_cell(Vector2i(x, room_height/2), 0, Vector2i(0, 6))

	for y in range(-room_height/2, room_height/2 + 1):
		wall_layer.set_cell(Vector2i(-room_width/2 - 1, y), 0, Vector2i(1, 6))
		wall_layer.set_cell(Vector2i(room_width/2, y), 0, Vector2i(1, 6))
