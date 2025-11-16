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
	player = get_tree().get_first_node_in_group("player")
	if not player:
		push_warning("Enemy: No player found in group 'player' at _ready.")
	else:
		print("Enemy linked to player:", player.name)
	
	if player and player.has_node("Camera2D"):
		camera = player.get_node("Camera2D")

	# Setup visuals
	collision_layer = 3
	collision_mask = 1 + 2
	if animated_sprite:
		animated_sprite.visible = true
		animated_sprite.modulate = Color.WHITE
		if animated_sprite.sprite_frames and animated_sprite.sprite_frames.has_animation("idle_down"):
			animated_sprite.play("idle_down")

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
	move_and_collide(velocity*delta)
	if animated_sprite and animated_sprite.sprite_frames:
		if abs(direction.x) > abs(direction.y):
			last_direction = "right" if direction.x > 0 else "left"
		else:
			last_direction = "down" if direction.y > 0 else "up"
		var walk_anim = "walk_" + last_direction
		if animated_sprite.sprite_frames.has_animation(walk_anim):
			animated_sprite.play(walk_anim)

func _attack_player():
	if is_attacking or attack_cooldown > 0:
		return
	is_attacking = true
	attack_cooldown = 1.5

	var dist = 0.0
	if is_instance_valid(player):
		dist = global_position.distance_to(player.global_position)
	print("[DEBUG] Enemy attempting attack. Dist=", dist, " cooldown=", attack_cooldown)
	
	# Simulate attack window; apply damage if in range
	await get_tree().create_timer(0.3).timeout
	if is_instance_valid(player) and dist <= attack_range:
		player.take_damage(attack_damage)
		print("[DEBUG] Enemy hit player for", attack_damage)
	else:
		print("[DEBUG] Enemy attack; but player out of range: dist=", dist)

	is_attacking = false

func _idle():
	velocity = Vector2.ZERO
	if animated_sprite and animated_sprite.sprite_frames:
		var idle_anim = "idle_" + last_direction
		if animated_sprite.sprite_frames.has_animation(idle_anim):
			animated_sprite.play(idle_anim)

func take_damage(damage: int):
	health -= damage
	emit_signal("enemy_damaged", damage)
	if camera and camera.has_method("shake"):
		camera.shake(2.0)
	if hit_particles:
		hit_particles.emitting = true
	if health <= 0:
		_die()
	else:
		modulate = Color.RED
		await get_tree().create_timer(0.1).timeout
		modulate = Color.WHITE
	print("Player health after hit? not tracked here; enemy health=", health)

func _die():
	emit_signal("enemy_died")
	# Death animation
	modulate = Color(1, 0, 0, 0.5)
	var tween = create_tween()
	tween.tween_property(self, "modulate:a", 0.0, 0.3)
	tween.tween_property(self, "scale", Vector2.ZERO, 0.2)
	if camera and camera.has_method("shake"):
		camera.shake(4.0)
	await tween.finished
	queue_free()
