extends CanvasLayer

@onready var health_bar = $HealthBar
@onready var health_label = $HealthBar/HealthLabel
@onready var enemy_count_label = $EnemyCountLabel
@onready var score_label = $ScoreLabel
@onready var level_label = $LevelLabel
@onready var story_label = $StoryLabel
@onready var generation_status_label = $GenerationStatus
@onready var game_over_panel = $GameOverPanel
@onready var game_over_label = $GameOverPanel/GameOverLabel
@onready var damage_numbers = $DamageNumbers

var player: Node2D = null
var enemy_spawner: Node2D = null
var ai_generator: Node2D = null
var game_manager: Node2D = null
var score: int = 0

func _ready():
	player = get_tree().get_first_node_in_group("player")
	enemy_spawner = get_tree().get_first_node_in_group("enemy_spawner")
	ai_generator = get_tree().get_first_node_in_group("ai_generator")
	game_manager = get_tree().get_first_node_in_group("game_manager")

	if player:
		player.player_damaged.connect(_on_player_damaged)
		player.player_died.connect(_on_game_over)
		_update_health_display()

	if enemy_spawner:
		enemy_spawner.enemy_spawned.connect(_on_enemy_spawned)
		_update_enemy_count()

	if ai_generator:
		ai_generator.enemy_generated.connect(_on_enemy_generated)
		generation_status_label.text = "AI Status: Active"

	if game_manager:
		game_manager.score_changed.connect(_on_score_changed)
		game_manager.level_complete.connect(_on_level_complete)
		game_manager.game_over.connect(_on_game_over)
		_update_level_display()
		_update_story_display()

	_update_score_display()

func _update_health_display():
	if not player:
		return

	health_bar.value = float(player.health) / player.max_health * 100
	health_label.text = "HP: %d/%d" % [player.health, player.max_health]

func _update_enemy_count():
	if not enemy_spawner:
		return

	var enemy_count = enemy_spawner.enemies.size()
	enemy_count_label.text = "Enemies: %d" % enemy_count

func _on_player_damaged(damage: int):
	_update_health_display()
	show_damage_number(damage, Color.RED)

func _on_enemy_spawned(enemy: Node):
	_update_enemy_count()
	enemy.enemy_died.connect(_on_enemy_died)

func _on_enemy_died():
	_update_enemy_count()
	if game_manager:
		game_manager.add_score(100)  # Points for defeating enemy

func _on_enemy_generated(archetype: String, enemy_data: Dictionary):
	generation_status_label.text = "AI Generated: " + archetype.capitalize().replace("_", " ")
	await get_tree().create_timer(2.0).timeout
	generation_status_label.text = "AI Status: Active"

func _on_score_changed(new_score: int):
	score = new_score
	_update_score_display()

func _on_level_complete():
	_update_level_display()
	_update_story_display()

func _on_game_over():
	game_over_panel.visible = true
	game_over_label.text = "GAME OVER\n\nFinal Score: %d\nLevel Reached: %d\n\nPress R to restart" % [score, game_manager.current_level if game_manager else 1]

func _update_score_display():
	score_label.text = "Score: %d" % score

func _update_level_display():
	if game_manager:
		level_label.text = "Level: %d" % game_manager.current_level

func _update_story_display():
	if game_manager:
		story_label.text = game_manager.get_story_text()

func _input(event):
	if event is InputEventKey and event.pressed:
		if event.keycode == KEY_R and game_over_panel.visible:
			_restart_game()

func _restart_game():
	game_over_panel.visible = false
	score = 0
	if game_manager:
		game_manager.reset_game()
	
	# Clear all existing enemies
	var enemies = get_tree().get_nodes_in_group("enemies")
	for enemy in enemies:
		enemy.queue_free()
	
	# Respawn player
	if player:
		player.health = player.max_health
		player.position = Vector2(0, 0)
		player.modulate = Color.WHITE
	
	_update_health_display()
	_update_score_display()
	_update_level_display()
	_update_story_display()
	_update_enemy_count()

func _remove_label(label: Label):
	label.queue_free()

func show_damage_number(damage: int, color: Color = Color.RED):
	var label = Label.new()
	label.text = str(damage)
	label.modulate = color
	label.add_theme_font_size_override("font_size", 16)

	# Position at random location on screen
	var viewport_size = get_viewport().get_visible_rect().size
	label.position = Vector2(
		randf_range(100, viewport_size.x - 100),
		randf_range(100, viewport_size.y - 100)
	)

	damage_numbers.add_child(label)

	# Animate and remove
	var tween = create_tween()
	tween.tween_property(label, "position:y", label.position.y - 50, 1.0)
	tween.tween_property(label, "modulate:a", 0.0, 0.5)
	tween.tween_callback(_remove_label.bind(label))