extends Node

class_name AudioManager

func _ready():
	add_to_group("audio_manager")

func play_attack_sound():
	# Audio not implemented yet - placeholder
	pass

func play_hurt_sound():
	# Audio not implemented yet - placeholder
	pass

func play_enemy_death_sound():
	# Audio not implemented yet - placeholder
	pass

func play_generation_sound():
	# Audio not implemented yet - placeholder
	pass

# Connect to game events
func connect_to_game_events():
	var player = get_tree().get_first_node_in_group("player")
	if player:
		player.player_damaged.connect(play_hurt_sound)

	var enemy_spawner = get_tree().get_first_node_in_group("enemy_spawner")
	if enemy_spawner:
		enemy_spawner.enemy_spawned.connect(_on_enemy_spawned)

	var ai_generator = get_tree().get_first_node_in_group("ai_generator")
	if ai_generator:
		ai_generator.enemy_generated.connect(play_generation_sound)

func _on_enemy_spawned(enemy: Node):
	if enemy and enemy.has_method("enemy_died"):
		enemy.enemy_died.connect(play_enemy_death_sound)