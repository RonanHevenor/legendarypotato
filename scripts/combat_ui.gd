extends CanvasLayer

@onready var health_bar: ProgressBar = $HealthBar
@onready var health_label: Label = $HealthBar/HealthLabel
@onready var enemy_count_label: Label = $EnemyCountLabel
@onready var score_label: Label = $ScoreLabel
@onready var level_label: Label = $LevelLabel
@onready var story_label: Label = $StoryLabel
@onready var generation_status_label: Label = $GenerationStatus
@onready var game_over_panel: Panel = $GameOverPanel
@onready var game_over_label: Label = $GameOverPanel/GameOverLabel
@onready var damage_numbers: Node2D = $DamageNumbers

var player: CharacterBody2D = null
var enemy_spawner: Node2D = null
var ai_generator: Node2D = null
var game_manager: Node = null
var score: int = 0

func _ready():
	# Use call_deferred to ensure all nodes are ready
	call_deferred("_initialize_ui")

func _initialize_ui():
	player = get_tree().get_first_node_in_group("player")
	enemy_spawner = get_tree().get_first_node_in_group("enemy_spawner")
	ai_generator = get_tree().get_first_node_in_group("ai_generator")
	game_manager = get_tree().get_first_node_in_group("game_manager")

	print("CombatUI initialization - player: ", player != null, " enemy_spawner: ", enemy_spawner != null, " game_manager: ", game_manager != null)

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

	# Color the health bar based on health percentage
	var health_percent = float(player.health) / player.max_health
	if health_percent > 0.6:
		health_bar.modulate = Color.GREEN
	elif health_percent > 0.3:
		health_bar.modulate = Color.YELLOW
	else:
		health_bar.modulate = Color.RED

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
	label.add_theme_font_size_override("font_size", 24)
	
	# Add outline for better visibility
	label.add_theme_color_override("font_outline_color", Color.BLACK)
	label.add_theme_constant_override("outline_size", 4)

	# Position at random location on screen
	var viewport_size = get_viewport().get_visible_rect().size
	label.position = Vector2(
		randf_range(100, viewport_size.x - 100),
		randf_range(100, viewport_size.y - 100)
	)

	damage_numbers.add_child(label)

	# Improved animation with pop effect
	var tween = create_tween()
	tween.set_parallel(true)
	tween.tween_property(label, "scale", Vector2(1.5, 1.5), 0.1)
	tween.tween_property(label, "position:y", label.position.y - 80, 1.0)
	tween.chain()
	tween.tween_property(label, "scale", Vector2(1.0, 1.0), 0.2)
	tween.set_parallel(true)
	tween.tween_property(label, "modulate:a", 0.0, 0.5)
	tween.chain()
	tween.tween_callback(_remove_label.bind(label))