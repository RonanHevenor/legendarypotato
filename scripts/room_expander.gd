extends Node2D

@onready var floor_layer = $TileMapLayer
@onready var wall_layer = $WallLayer

func _ready():
	# Defer expansion to ensure nodes are ready
	call_deferred("expand_floor")

func expand_floor():
	# Check if nodes exist
	if not floor_layer or not wall_layer:
		push_error("TileMapLayer nodes not found!")
		return

	# Check if tileset exists
	if not floor_layer.tile_set or not wall_layer.tile_set:
		push_error("TileSet not assigned to TileMapLayer nodes!")
		return

	print("Starting floor expansion...")

	# Start with a simple test - just set a few tiles
	var test_tiles = [
		[0, 0, 0],  # Floor tile at (0,0)
		[1, 0, 0],  # Variation at (1,0)
		[0, 1, 0],  # Floor tile at (0,1)
		[1, 1, 0]   # Variation at (1,1)
	]

	for tile in test_tiles:
		var x = tile[0]
		var y = tile[1]
		var tile_x = tile[2]
		floor_layer.set_cell(Vector2i(x, y), 0, Vector2i(tile_x, 0))
		print("Set tile at (", x, ",", y, ") to (", tile_x, ", 0)")

	# Add some walls
	wall_layer.set_cell(Vector2i(-1, -1), 0, Vector2i(0, 6))
	wall_layer.set_cell(Vector2i(0, -1), 0, Vector2i(0, 6))
	wall_layer.set_cell(Vector2i(1, -1), 0, Vector2i(0, 6))

	print("Floor expansion complete")
