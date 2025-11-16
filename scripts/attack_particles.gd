extends CPUParticles2D

func _ready():
	emitting = false
	one_shot = true
	explosiveness = 0.8
	amount = 15
	lifetime = 0.3
	speed_scale = 2.5
	
	# Emission
	emission_shape = EMISSION_SHAPE_SPHERE
	emission_sphere_radius = 5.0
	
	# Movement
	spread = 45
	gravity = Vector2.ZERO
	initial_velocity_min = 100.0
	initial_velocity_max = 200.0
	
	# Scale
	scale_amount_min = 2.0
	scale_amount_max = 4.0
	
	# Color (white/yellow flash)
	color = Color(1.0, 1.0, 0.7, 1.0)

func emit_at_angle(angle_deg: float):
	rotation_degrees = angle_deg
	emitting = true
	# Auto-cleanup after lifetime
	await get_tree().create_timer(lifetime).timeout
	queue_free()
