extends Node

class_name LevelManager

@export var room_scenes: Array[PackedScene] = []
@export var transition_distance: float = 400.0
@export var rooms_per_level: int = 1

var current_room: Node2D = null
var player: Node2D = null
var rooms_generated: Array = []
var current_room_index: int = 0
var rooms_created_in_level: int = 0

# Failsafe timer to auto-advance if progression stalls
var watchdog_seconds: float = 3.0
var watchdog_timer: float = 0.0

signal room_changed(new_room: Node2D)

var rng: RandomNumberGenerator = RandomNumberGenerator.new()
var procedural_room_scene: PackedScene = preload("res://scenes/levels/room_procedural.tscn")

func _ready():
	add_to_group("level_manager")
	rng.randomize()
	rooms_created_in_level = 0
	watchdog_timer = 0.0
	call_deferred("_initialize_level_manager")

func _initialize_level_manager():
	player = get_tree().get_first_node_in_group("player")
	if not player:
		push_error("No player found!")
		return

	# Start with the initial room (existing scene)
	current_room = get_tree().current_scene
	rooms_generated.append(current_room)
	_setup_room(current_room)
	if current_room and current_room.has_node("EnemySpawner"):
		var spawner = current_room.get_node("EnemySpawner")
		if spawner and spawner.has_signal("room_cleared"):
			spawner.room_cleared.connect(_on_room_cleared)

   # Replace initial room with a procedural variation for immediate randomness
	if current_room:
		var parent = get_tree().root
		var proc_room = procedural_room_scene.instantiate()
		if proc_room.has_method("set_seed"):
			proc_room.set_seed(rng.randi())
		parent.add_child(proc_room)
		proc_room.position = current_room.position
		# Move player to new room before freeing old
		if player and proc_room.has_node("YSort"):
			var new_ysort = proc_room.get_node("YSort")
			player.reparent(new_ysort)
			# Remove the extra Player from the procedural room
			if proc_room.has_node("YSort/Player"):
				proc_room.get_node("YSort/Player").queue_free()
		# Move level manager to root to prevent it from being freed
		var managers = ["GameManager", "AudioManager", "AIGenerator", "CombatUI"]
		for mgr_name in managers:
			if current_room.has_node(mgr_name):
				var mgr = current_room.get_node(mgr_name)
				mgr.reparent(parent)
		self.reparent(parent)
		rooms_generated = [proc_room]
		current_room.queue_free()
		current_room = proc_room
		_setup_room(current_room)
		if current_room and current_room.has_node("EnemySpawner"):
			var spawner2 = current_room.get_node("EnemySpawner")
			if spawner2 and spawner2.has_signal("room_cleared"):
				spawner2.room_cleared.connect(_on_room_cleared)
		print("Init: swapped initial to procedural. Has EnemySpawner? ", current_room.has_node("EnemySpawner"))

func _process(delta):
	# Ensure we have a reference to the player
	if not player:
		player = get_tree().get_first_node_in_group("player")
		if not player:
			return
	if not current_room:
		return
	# watchdog timer to guard against stalls
	watchdog_timer += delta
	if watchdog_timer > watchdog_seconds:
		watchdog_timer = 0.0
		print("[DEBUG] watchdog: stall detected, but not forcing progression")
	
	var player_pos = player.global_position
	var room_center = current_room.global_position
	if player_pos.distance_to(room_center) > transition_distance:
		_generate_new_room(player_pos - room_center)

func _generate_new_room(direction: Vector2):
	var dir_name = _get_direction_name(direction)
	print("Generating new room in direction: ", dir_name)
	var new_room = _create_next_room()
	if not new_room:
		return
	var offset = direction.normalized() * transition_distance * 2
	new_room.position = current_room.position + offset
	get_tree().root.add_child(new_room)
	rooms_generated.append(new_room)
	_setup_room(new_room)
	_transition_to_room(new_room)

func _get_direction_name(direction: Vector2) -> String:
	if abs(direction.x) > abs(direction.y):
		return "east" if direction.x > 0 else "west"
	else:
		return "south" if direction.y > 0 else "north"

func _create_next_room() -> Node2D:
	# Decide between procedural and preset room
	var use_procedural = rng.randf() < 0.5 or room_scenes.size() == 0
	if use_procedural:
		var room = procedural_room_scene.instantiate()
		if room.has_method("set_seed"):
			room.set_seed(rng.randi())
		return room
	else:
		var idx = rng.randi() % room_scenes.size()
		var room = room_scenes[idx].instantiate()
		if room.has_method("set_seed"):
			room.set_seed(rng.randi())
		return room
	return null

func _create_basic_room() -> Node2D:
	# Fallback basic room if needed
	var room = Node2D.new()
	room.name = "GeneratedRoom"
	var tilemap = TileMapLayer.new()
	tilemap.name = "TileMapLayer"
	room.add_child(tilemap)
	var spawner = Node2D.new()
	spawner.name = "EnemySpawner"
	spawner.script = load("res://scripts/enemy_spawner.gd")
	spawner.enemy_scene = load("res://scenes/enemy/enemy.tscn")
	room.add_child(spawner)
	return room

func _setup_room(room: Node2D):
	if not room.has_node("EnemySpawner"):
		var spawner = Node2D.new()
		spawner.name = "EnemySpawner"
		spawner.script = load("res://scripts/enemy_spawner.gd")
		spawner.enemy_scene = load("res://scenes/enemy/enemy.tscn")
		room.add_child(spawner)

	var ui = get_tree().get_first_node_in_group("combat_ui")
	if ui and room.has_node("EnemySpawner"):
		var spawner = room.get_node("EnemySpawner")
		if not spawner.enemy_spawned.is_connected(ui._on_enemy_spawned):
			spawner.enemy_spawned.connect(ui._on_enemy_spawned)
		if spawner.has_signal("room_cleared") and not spawner.room_cleared.is_connected(_on_room_cleared):
			spawner.room_cleared.connect(_on_room_cleared)

func _transition_to_room(new_room: Node2D):
	var old_room = current_room
	current_room = new_room
	current_room_index = rooms_generated.size() - 1
	room_changed.emit(new_room)
	# Hybrid landing: SpawnPoint if available; otherwise preserve world position, with minimal reparenting
	if player and new_room.has_node("YSort"):
		var new_ysort = new_room.get_node("YSort")
		if new_room.has_node("SpawnPoint"):
			var sp = new_room.get_node("SpawnPoint")
			player.global_position = sp.global_position
			player.reparent(new_ysort)
		else:
			var old_pos = player.global_position
			player.reparent(new_ysort)
			player.global_position = old_pos
		if new_room.has_node("YSort/Player"):
			new_room.get_node("YSort/Player").queue_free()
	var camera = player.get_node_or_null("Camera2D")
	if camera:
		pass
	
	print("Transitioned to room: ", new_room.name)
	# Post-transition interior nudge to improve collisions
	if player and new_room and new_room.has_node("YSort") and not new_room.has_node("SpawnPoint"):
		var center = current_room.global_position
		var to_center = (center - player.global_position).normalized()
		if to_center != Vector2.ZERO:
			player.global_position += to_center * 16.0




func _on_room_cleared():
	print("[DEBUG] _on_room_cleared: current_room_index=", current_room_index, " rooms_per_level=", rooms_per_level)
	print("[DEBUG] progress path: spawning next room or level")
	watchdog_timer = 0.0
	# Room cleared: either load next variation or advance level
	current_room_index += 1
	if current_room_index < rooms_per_level:
		var next_room = _create_next_room()
		if next_room:
			next_room.position = current_room.position + Vector2(transition_distance * 2, 0)
			get_tree().root.add_child(next_room)
			rooms_generated.append(next_room)
			_setup_room(next_room)
			_transition_to_room(next_room)
		else:
			print("[DEBUG] No next room created; advancing level if possible")
			var gm = get_tree().get_first_node_in_group("game_manager")
			if gm:
				gm.next_level()
			current_room_index = 0  # Reset for new level
			# Generate a new room for the new level
			var new_room = _create_next_room()
			if new_room:
				new_room.position = current_room.position + Vector2(transition_distance * 2, 0)
				get_tree().root.add_child(new_room)
				rooms_generated.append(new_room)
				_setup_room(new_room)
				_transition_to_room(new_room)
			else:
				print("[DEBUG] No next room created for new level")
	else:
		print("[DEBUG] All rooms in level cleared; advancing level")
		var gm = get_tree().get_first_node_in_group("game_manager")
		if gm:
			gm.next_level()
		current_room_index = 0  # Reset for new level
		# Generate a new room for the new level
		var new_room = _create_next_room()
		if new_room:
			new_room.position = current_room.position + Vector2(transition_distance * 2, 0)
			get_tree().root.add_child(new_room)
			rooms_generated.append(new_room)
			_setup_room(new_room)
			_transition_to_room(new_room)
		else:
			print("[DEBUG] No next room created for new level")

# Advancement helper for external calls
func advance_room_or_level():
	_on_room_cleared()

# AI Integration helper
func spawn_ai_enemy_in_current_room(enemy_data: Dictionary):
	if not current_room or not current_room.has_node("EnemySpawner"):
		return
	var spawner = current_room.get_node("EnemySpawner")
	if spawner.has_method("spawn_ai_enemy"):
		spawner.spawn_ai_enemy(enemy_data)
