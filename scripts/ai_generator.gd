extends Node

class_name AIGenerator

@export var auto_generate: bool = false
@export var generation_interval: float = 30.0  # Generate new enemy every 30 seconds

var generation_timer: float = 0.0
var level_manager: Node = null
var enemy_archetypes = ["scout_clanker", "combat_clanker", "heavy_clanker", "repair_clanker"]

signal enemy_generated(archetype: String, enemy_data: Dictionary)

func _ready():
	add_to_group("ai_generator")
	call_deferred("_initialize_ai_generator")

func _initialize_ai_generator():
	level_manager = get_tree().get_first_node_in_group("level_manager")

	if auto_generate:
		generation_timer = generation_interval * 0.5  # Start with half interval
		# Generate initial enemy after a short delay
		call_deferred("_generate_initial_enemy")

func _generate_initial_enemy():
	await get_tree().create_timer(2.0).timeout  # Give more time for initialization
	if level_manager:
		generate_random_enemy()
	else:
		push_error("AI Generator: Level manager not found, skipping initial enemy generation")

func _process(delta):
	if not auto_generate or not level_manager:
		return

	generation_timer += delta
	if generation_timer >= generation_interval:
		generation_timer = 0.0
		generate_random_enemy()

func generate_random_enemy():
	if not level_manager:
		level_manager = get_tree().get_first_node_in_group("level_manager")
		if not level_manager:
			print("AI Generator: No level manager found, skipping enemy generation")
			return

	var archetype = enemy_archetypes[randi() % enemy_archetypes.size()]
	print("AI Generator: Creating ", archetype, " enemy...")

	# In a real implementation, this would call the Python script
	# For now, create mock enemy data
	var enemy_data = _create_mock_enemy_data(archetype)

	# Spawn the enemy
	if level_manager.has_method("spawn_ai_enemy_in_current_room"):
		level_manager.spawn_ai_enemy_in_current_room(enemy_data)

	enemy_generated.emit(archetype, enemy_data)

func generate_specific_enemy(archetype: String):
	if not level_manager:
		level_manager = get_tree().get_first_node_in_group("level_manager")
		if not level_manager:
			print("AI Generator: No level manager found, skipping enemy generation")
			return

	print("AI Generator: Creating specific ", archetype, " enemy...")

	var enemy_data = _create_mock_enemy_data(archetype)

	if level_manager.has_method("spawn_ai_enemy_in_current_room"):
		level_manager.spawn_ai_enemy_in_current_room(enemy_data)

	enemy_generated.emit(archetype, enemy_data)

func _create_mock_enemy_data(archetype: String) -> Dictionary:
	# Create mock clanker data for testing
	var stats = {
		"scout_clanker": {"health": 60, "speed": 120, "damage": 15, "behavior": "aggressive_melee"},
		"combat_clanker": {"health": 100, "speed": 70, "damage": 25, "behavior": "ranged_kiting"},
		"heavy_clanker": {"health": 200, "speed": 40, "damage": 40, "behavior": "ferocious_charge"},
		"repair_clanker": {"health": 80, "speed": 60, "damage": 10, "behavior": "persistent_hunter"}
	}

	var enemy_stats = stats.get(archetype, stats["scout_clanker"])
	enemy_stats["archetype"] = archetype

	# Create simple ASCII frames based on clanker archetype
	var frames = {}
	var idle_frame = []

	match archetype:
		"scout_clanker":
			idle_frame = [
				"   [===]   ",
				"  /     \\  ",
				" |  o o  | ",
				"  \\  ^  /  ",
				"   |===|   ",
				"  /     \\  ",
				" |       | ",
				"  \\     /  ",
				"   =====   ",
				"  /     \\  ",
				" |       | ",
				"  \\     /  ",
				"   =====   ",
				"    |||    ",
				"    |||    ",
				"   /   \\   "
			]
		"combat_clanker":
			idle_frame = [
				"   [===]   ",
				"  /     \\  ",
				" |  o o  | ",
				"  \\  ^  /  ",
				"   |===|   ",
				"  / ||| \\  ",
				" | |   | | ",
				"  \\ ||| /  ",
				"   =====   ",
				"  /     \\  ",
				" | ===== | ",
				"  \\     /  ",
				"   =====   ",
				"    |||    ",
				"    |||    ",
				"   /   \\   "
			]
		"heavy_clanker":
			idle_frame = [
				"  [=====]  ",
				" /       \\ ",
				" |  o o  | ",
				"  \\  ^  /  ",
				"   |===|   ",
				"  /|||||\\  ",
				" | ||||| | ",
				"  \\|||||/  ",
				"   ======= ",
				"  /       \\ ",
				" | ======= | ",
				"  \\       /  ",
				"   ======= ",
				"   |||||||  ",
				"   |||||||  ",
				"  /       \\ "
			]
		"repair_clanker":
			idle_frame = [
				"   [===]   ",
				"  /     \\  ",
				" |  o o  | ",
				"  \\  +  /  ",
				"   |===|   ",
				"  / +++ \\  ",
				" | +   + | ",
				"  \\ +++ /  ",
				"   =====   ",
				"  /     \\  ",
				" | ===== | ",
				"  \\     /  ",
				"   =====   ",
				"    +++    ",
				"    +++    ",
				"   /   \\   "
			]
		_:
			idle_frame = [
				"   [===]   ",
				"  /     \\  ",
				" |  o o  | ",
				"  \\  ^  /  ",
				"   |===|   ",
				"  /     \\  ",
				" |       | ",
				"  \\     /  ",
				"   =====   ",
				"  /     \\  ",
				" | ===== | ",
				"  \\     /  ",
				"   =====   ",
				"    |||    ",
				"    |||    ",
				"   /   \\   "
			]

	# Create all required frames (simplified - just copy idle for now)
	frames["idle_down"] = idle_frame
	frames["walk_down_0"] = idle_frame
	frames["walk_down_1"] = idle_frame
	frames["walk_down_2"] = idle_frame
	frames["attack_down_0"] = idle_frame
	frames["attack_down_1"] = idle_frame

	return {
		"stats": enemy_stats,
		"color_map": {
			"@": "#FF0000", "#": "#00FF00", "+": "#0000FF", "=": "#FFFF00",
			"-": "#FF00FF", ".": "#00FFFF", " ": "#00000000"
		},
		"frames": frames
	}

# Python Integration (for future use)
func call_python_generator(archetype: String) -> Dictionary:
	# This would call the Python script via OS.execute or similar
	# For now, return mock data
	return _create_mock_enemy_data(archetype)