extends CharacterBody2D

class_name Enemy

@export var max_health: int = 60
@export var speed: float = 60.0
@export var attack_damage: int = 10
@export var attack_range: float = 32.0
@export var detection_range: float = 128.0

@onready var animated_sprite = $AnimatedSprite2D
@onready var hit_particles = $HitParticles

var health: int
var player: Node2D = null
var is_attacking: bool = false
var attack_cooldown: float = 0.0
var last_direction = "down"
var camera: Camera2D

signal enemy_died
signal enemy_damaged(damage: int)

func _ready():
	health = max_health
	
	# Find player first
	player = get_tree().get_first_node_in_group("player")
	
	# Get camera reference from player
	if player and player.has_node("Camera2D"):
		camera = player.get_node("Camera2D")

	# Set collision layers
	collision_layer = 4  # Enemies layer
	collision_mask = 1 + 2  # World + Player
	if not player:
		push_error("No player found in group 'player'")

	# Ensure sprite is visible
	if animated_sprite:
		animated_sprite.visible = true
		animated_sprite.modulate = Color.WHITE
		print("Enemy sprite setup - has frames: ", animated_sprite.sprite_frames != null)
		if animated_sprite.sprite_frames and animated_sprite.sprite_frames.has_animation("idle_down"):
			animated_sprite.play("idle_down")
			print("Enemy playing idle_down animation")
		else:
			print("ERROR: Enemy sprite_frames not set or animation missing!")

func _physics_process(delta):
	if not player:
		return

	attack_cooldown = max(0, attack_cooldown - delta)

	var distance_to_player = global_position.distance_to(player.global_position)

	if distance_to_player <= attack_range and attack_cooldown <= 0:
		_attack_player()
	elif distance_to_player <= detection_range:
		_move_toward_player(delta)
	else:
		_idle()

func _move_toward_player(delta: float):
	var direction = (player.global_position - global_position).normalized()
	velocity = direction * speed
	move_and_slide()
	
	# Update animation based on movement direction
	if animated_sprite and animated_sprite.sprite_frames:
		if abs(direction.x) > abs(direction.y):
			if direction.x > 0:
				last_direction = "right"
			else:
				last_direction = "left"
		else:
			if direction.y > 0:
				last_direction = "down"
			else:
				last_direction = "up"
		
		var walk_anim = "walk_" + last_direction
		if animated_sprite.sprite_frames.has_animation(walk_anim):
			animated_sprite.play(walk_anim)

func _attack_player():
	if is_attacking or attack_cooldown > 0:
		return

	is_attacking = true
	attack_cooldown = 1.5

	await get_tree().create_timer(0.3).timeout
	if is_instance_valid(player) and global_position.distance_to(player.global_position) <= attack_range:
		player.take_damage(attack_damage)

	is_attacking = false

func _idle():
	velocity = Vector2.ZERO
	
	# Play idle animation
	if animated_sprite and animated_sprite.sprite_frames:
		var idle_anim = "idle_" + last_direction
		if animated_sprite.sprite_frames.has_animation(idle_anim):
			animated_sprite.play(idle_anim)

func take_damage(damage: int):
	health -= damage
	enemy_damaged.emit(damage)
	
	# Screen shake
	if camera and camera.has_method("shake"):
		camera.shake(2.0)
	
	# Particle effect
	if hit_particles:
		hit_particles.emitting = true

	if health <= 0:
		_die()
	else:
		# Flash red
		modulate = Color.RED
		await get_tree().create_timer(0.1).timeout
		modulate = Color.WHITE

func _die():
	enemy_died.emit()

	# Death animation
	modulate = Color(1, 0, 0, 0.5)
	var tween = create_tween()
	tween.tween_property(self, "modulate:a", 0.0, 0.3)
	tween.tween_property(self, "scale", Vector2.ZERO, 0.2)

	# Screen shake
	if camera and camera.has_method("shake"):
		camera.shake(4.0)

	# Wait for animation or timeout to prevent hanging
	await tween.finished
	queue_free()