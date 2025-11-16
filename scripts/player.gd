extends CharacterBody2D

@export var speed = 100.0
@export var max_health: int = 100
@export var attack_damage: int = 20
@export var attack_range: float = 24.0

@onready var animated_sprite = $AnimatedSprite2D
@onready var hit_particles = $HitParticles

var health: int
var last_direction = "down"
var is_attacking: bool = false
var attack_cooldown: float = 0.0
var camera: Camera2D

signal player_damaged(damage: int)
signal player_died

func _ready():
	health = max_health

	# Get camera reference (might not be ready yet)
	if has_node("Camera2D"):
		camera = $Camera2D
	else:
		push_warning("Player: Camera2D node not found")

	# Set collision layers
	collision_layer = 2  # Player layer
	collision_mask = 1 + 3 + 4 + 8  # World + Enemy + EnemyHurtBox + Projectiles

func _physics_process(delta):
	attack_cooldown = max(0, attack_cooldown - delta)
	# Get input direction
	var input_dir = Input.get_vector("ui_left", "ui_right", "ui_up", "ui_down")

	# Set velocity
	velocity = input_dir * speed

	# Handle animations
	if input_dir != Vector2.ZERO:
		# Determine direction and play animation
		if abs(input_dir.x) > abs(input_dir.y):
			if input_dir.x > 0:
				last_direction = "right"
			else:
				last_direction = "left"
		else:
			if input_dir.y > 0:
				last_direction = "down"
			else:
				last_direction = "up"

		# Try to play walk animation
		var walk_anim = "walk_" + last_direction
		if animated_sprite and animated_sprite.sprite_frames and animated_sprite.sprite_frames.has_animation(walk_anim):
			animated_sprite.play(walk_anim)
	else:
		# Try to play idle animation
		var idle_anim = "idle_" + last_direction
		if animated_sprite and animated_sprite.sprite_frames and animated_sprite.sprite_frames.has_animation(idle_anim):
			animated_sprite.play(idle_anim)

	# Handle attack input
	if Input.is_action_just_pressed("attack") and attack_cooldown <= 0:
		_attack()

	# Debug: take damage with X key
	if Input.is_action_just_pressed("ui_cancel"):  # X key
		take_damage(25)

	# Move the player
	move_and_slide()

func _attack():
	if is_attacking:
		return

	is_attacking = true
	attack_cooldown = 0.5  # 0.5 second cooldown

	# Play attack animation - temporarily disabled
	# TODO: Fix animation system
	pass

	# Check for enemies in attack range
	var space_state = get_world_2d().direct_space_state
	var query = PhysicsRayQueryParameters2D.create(
		global_position,
		global_position + _get_attack_direction() * attack_range,
		collision_mask,
		[self]  # Exclude self
	)

	var result = space_state.intersect_ray(query)
	if result and result.collider.is_in_group("enemies"):
		result.collider.take_damage(attack_damage)
		# Screen shake on hit
		if camera and camera.has_method("shake"):
			camera.shake(3.0)

	await get_tree().create_timer(0.2).timeout
	is_attacking = false

func _get_attack_direction() -> Vector2:
	match last_direction:
		"up": return Vector2.UP
		"down": return Vector2.DOWN
		"left": return Vector2.LEFT
		"right": return Vector2.RIGHT
		_: return Vector2.DOWN

func take_damage(damage: int):
	health -= damage
	player_damaged.emit(damage)
	
	# Screen shake
	if camera and camera.has_method("shake"):
		camera.shake(5.0)
	
	# Particle effect
	if hit_particles:
		hit_particles.emitting = true

	if health <= 0:
		_die()
	else:
		# Visual feedback with shader flash
		modulate = Color.RED
		await get_tree().create_timer(0.1).timeout
		modulate = Color.WHITE

	# Debug: print health
	print("Player health: ", health)

func _die():
	player_died.emit()
	# Respawn after a delay
	await get_tree().create_timer(1.5).timeout
	respawn()
	print("Player respawned!")

func attack(target):
	# Called when colliding with enemy hurt box
	if target and target.has_method("take_damage"):
		target.take_damage(attack_damage)

func respawn():
	# Reset health to full
	health = max_health
	# Reset position to spawn point
	position = Vector2(0, 0)
	# Reset visual state
	modulate = Color.WHITE
	# Emit signal to update UI
	var game_manager = get_tree().get_first_node_in_group("game_manager")
	if game_manager:
		game_manager.health_changed.emit(health)
	print("Player health restored to: ", health)
