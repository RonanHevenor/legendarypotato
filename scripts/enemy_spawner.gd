extends Node2D

@export var enemy_scene: PackedScene
@export var spawn_interval: float = 5.0
@export var max_enemies: int = 2  # Start with fewer enemies
@export var spawn_radius: float = 200.0

var enemies: Array = []
var spawn_timer: float = 0.0
var player: Node2D = null
var game_manager: Node = null
var enemies_per_level = [2, 3, 4, 5, 6]  # Progressive difficulty

signal enemy_spawned(enemy: Node)

func _ready():
	add_to_group("enemy_spawner")
	call_deferred("_initialize_spawner")

func _initialize_spawner():
	player = get_tree().get_first_node_in_group("player")
	if not player:
		push_error("No player found in group 'player'")
		return

	game_manager = get_tree().get_first_node_in_group("game_manager")

	if game_manager:
		game_manager.level_complete.connect(_on_level_complete)
		_update_max_enemies()

	# Spawn initial enemies
	call_deferred("_spawn_initial_enemies")

func _spawn_initial_enemies():
	# Spawn initial enemies
	if not player:
		push_error("Cannot spawn enemies - no player found")
		return

	for i in range(max_enemies):
		_spawn_enemy()

func _process(delta):
	if not player:
		return

	spawn_timer += delta
	if spawn_timer >= spawn_interval and enemies.size() < max_enemies:
		spawn_timer = 0.0
		_spawn_enemy()

	# Clean up dead enemies
	enemies = enemies.filter(func(enemy): return is_instance_valid(enemy))

func _spawn_enemy():
	if not enemy_scene:
		push_error("No enemy scene assigned")
		return

	if not player:
		return

	# Find spawn position away from player
	var spawn_pos = _find_spawn_position()
	if spawn_pos == Vector2.ZERO:
		return

	var enemy = enemy_scene.instantiate()
	enemy.position = spawn_pos
	enemy.add_to_group("enemies")

	# Make sure enemy is visible
	enemy.visible = true
	enemy.modulate = Color(1, 1, 1, 1)  # Normal white color
	enemy.z_index = 1  # Make sure it's above the floor

	# Connect signals
	enemy.enemy_died.connect(_on_enemy_died.bind(enemy))

	# Add to YSort for proper layering
	var ysort = get_parent().get_node("YSort")
	if ysort:
		ysort.add_child(enemy)
	else:
		get_parent().add_child(enemy)
	enemies.append(enemy)
	enemy_spawned.emit(enemy)

	print("Enemy spawned at: ", spawn_pos, " visible: ", enemy.visible)

func _find_spawn_position() -> Vector2:
	# Try to find a valid spawn position
	for attempt in range(10):
		var angle = randf() * TAU
		var distance = randf_range(100, spawn_radius)
		var candidate_pos = player.position + Vector2(cos(angle), sin(angle)) * distance

		# Check if position is valid (not in walls, etc.)
		if _is_position_valid(candidate_pos):
			return candidate_pos

	return Vector2.ZERO

func _is_position_valid(pos: Vector2) -> bool:
	# Simplified: just check if position is not too close to player
	var distance_to_player = pos.distance_to(player.position)
	return distance_to_player >= 100 and distance_to_player <= spawn_radius

func _on_enemy_died(enemy: Node):
	enemies.erase(enemy)
	print("Enemy died, remaining: ", enemies.size())

	# Check if level is complete (all enemies defeated)
	if enemies.size() == 0 and game_manager:
		game_manager.next_level()

func _on_level_complete():
	_update_max_enemies()
	# Spawn new enemies for the next level
	for i in range(max_enemies):
		_spawn_enemy()

func _update_max_enemies():
	if game_manager:
		var level = min(game_manager.current_level - 1, enemies_per_level.size() - 1)
		max_enemies = enemies_per_level[level]

# AI Generation Integration
func spawn_ai_enemy(enemy_data: Dictionary):
	if not enemy_scene:
		return

	var spawn_pos = _find_spawn_position()
	if spawn_pos == Vector2.ZERO:
		return

	var enemy = enemy_scene.instantiate()
	enemy.position = spawn_pos
	enemy.add_to_group("enemies")

	# Load AI-generated data
	if enemy.has_method("load_ai_generated_sprite"):
		enemy.load_ai_generated_sprite(enemy_data)

	# Set basic stats (simplified)
	enemy.max_health = 60
	enemy.speed = 60.0
	enemy.attack_damage = 10

	enemy.enemy_died.connect(_on_enemy_died.bind(enemy))
	get_parent().add_child(enemy)
	enemies.append(enemy)
	enemy_spawned.emit(enemy)

	print("Spawned AI enemy: ", enemy_data.get("stats", {}).get("archetype", "unknown"))
