extends Node

class_name LevelManager

@export var room_scenes: Array[PackedScene] = []
@export var transition_distance: float = 400.0

var current_room: Node2D = null
var player: Node2D = null
var rooms_generated: Array = []
var current_room_index: int = 0

signal room_changed(new_room: Node2D)

func _ready():
	add_to_group("level_manager")
	player = get_tree().get_first_node_in_group("player")
	if not player:
		push_error("No player found!")
		return

	# Start with the initial room
	current_room = get_parent()
	rooms_generated.append(current_room)
	_setup_room(current_room)

func _process(delta):
	if not player or not current_room:
		return

	# Check if player has moved far enough to generate a new room
	var player_pos = player.global_position
	var room_center = current_room.global_position

	if player_pos.distance_to(room_center) > transition_distance:
		_generate_new_room(player_pos - room_center)

func _generate_new_room(direction: Vector2):
	# Determine which direction to generate the room
	var dir_name = _get_direction_name(direction)

	print("Generating new room in direction: ", dir_name)

	# Create a new room
	var new_room = _create_random_room()
	if not new_room:
		return

	# Position the new room adjacent to current room
	var offset = direction.normalized() * transition_distance * 2
	new_room.position = current_room.position + offset

	# Add to scene
	get_parent().add_child(new_room)
	rooms_generated.append(new_room)

	# Setup the new room
	_setup_room(new_room)

	# Transition to new room
	_transition_to_room(new_room)

func _get_direction_name(direction: Vector2) -> String:
	if abs(direction.x) > abs(direction.y):
		return "east" if direction.x > 0 else "west"
	else:
		return "south" if direction.y > 0 else "north"

func _create_random_room() -> Node2D:
	if room_scenes.is_empty():
		# Fallback: create a basic room
		return _create_basic_room()

	var room_scene = room_scenes[randi() % room_scenes.size()]
	return room_scene.instantiate()

func _create_basic_room() -> Node2D:
	var room = Node2D.new()
	room.name = "GeneratedRoom"

	# Add basic components (simplified version of room_01)
	var tilemap = TileMapLayer.new()
	tilemap.name = "TileMapLayer"
	room.add_child(tilemap)

	# Add enemy spawner
	var spawner = Node2D.new()
	spawner.name = "EnemySpawner"
	spawner.script = load("res://scripts/enemy_spawner.gd")
	spawner.enemy_scene = load("res://scenes/enemy/enemy.tscn")
	room.add_child(spawner)

	return room

func _setup_room(room: Node2D):
	# Ensure room has necessary components
	if not room.has_node("EnemySpawner"):
		var spawner = Node2D.new()
		spawner.name = "EnemySpawner"
		spawner.script = load("res://scripts/enemy_spawner.gd")
		spawner.enemy_scene = load("res://scenes/enemy/enemy.tscn")
		room.add_child(spawner)

	# Connect enemy spawner signals if UI exists
	var ui = get_tree().get_first_node_in_group("combat_ui")
	if ui and room.has_node("EnemySpawner"):
		var spawner = room.get_node("EnemySpawner")
		spawner.enemy_spawned.connect(ui._on_enemy_spawned)

func _transition_to_room(new_room: Node2D):
	current_room = new_room
	current_room_index = rooms_generated.size() - 1

	room_changed.emit(new_room)

	# Move camera to new room center
	var camera = player.get_node_or_null("Camera2D")
	if camera:
		var tween = create_tween()
		tween.tween_property(camera, "global_position", new_room.global_position, 0.5)

	print("Transitioned to room: ", new_room.name)

# AI Integration
func spawn_ai_enemy_in_current_room(enemy_data: Dictionary):
	if not current_room or not current_room.has_node("EnemySpawner"):
		return

	var spawner = current_room.get_node("EnemySpawner")
	if spawner.has_method("spawn_ai_enemy"):
		spawner.spawn_ai_enemy(enemy_data)