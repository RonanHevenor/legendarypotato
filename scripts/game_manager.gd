extends Node

class_name GameManager

@export var max_player_health: int = 100
@export var starting_room_scene: PackedScene

var current_level: int = 1
var player_score: int = 0
var game_state: String = "playing"  # playing, game_over, victory
var player_node: Node2D = null

signal game_over
signal level_complete
signal score_changed(new_score: int)
signal health_changed(new_health: int)

func _ready():
	add_to_group("game_manager")
	call_deferred("_initialize_game_manager")

func _initialize_game_manager():
	player_node = get_tree().get_first_node_in_group("player")
	if player_node:
		player_node.player_died.connect(_on_player_died)
		player_node.player_damaged.connect(_on_player_damaged)

func _on_player_died():
	game_state = "game_over"
	game_over.emit()
	print("Game Over! Final Score: ", player_score)

func _on_player_damaged(damage: int):
	health_changed.emit(player_node.health)

func add_score(points: int):
	player_score += points
	score_changed.emit(player_score)

func next_level():
	current_level += 1
	level_complete.emit()
	print("Level ", current_level, " complete!")

func reset_game():
	current_level = 1
	player_score = 0
	game_state = "playing"
	if player_node:
		player_node.health = player_node.max_health
		player_node.position = Vector2(0, 0)  # Reset position
		health_changed.emit(player_node.health)

func get_story_text() -> String:
	match current_level:
		1:
			return "The clankers have invaded. Fight your way through the scout patrols!"
		2:
			return "Combat clankers detected. Their projectile weapons are dangerous!"
		3:
			return "Heavy clankers approaching. Their armor is tough, but they move slowly."
		4:
			return "Repair clankers are supporting the invasion. Take them out first!"
		5:
			return "Final assault! The clanker command center is within reach."
		_:
			return "Unknown level"
