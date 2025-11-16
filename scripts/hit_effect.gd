extends CPUParticles2D

func _ready():
	emitting = false
	one_shot = true
	explosiveness = 1.0
	amount = 20
	lifetime = 0.5
	speed_scale = 2.0
	
	# Emission
	emission_shape = EMISSION_SHAPE_SPHERE
	emission_sphere_radius = 5.0
	
	# Movement
	direction = Vector2(0, -1)
	spread = 180
	gravity = Vector2(0, 200)
	initial_velocity_min = 50.0
	initial_velocity_max = 100.0
	
	# Scale
	scale_amount_min = 2.0
	scale_amount_max = 4.0
	
	# Color (blood red)
	color = Color(0.8, 0.1, 0.1, 1.0)

func emit_particles():
	emitting = true
	# Auto-cleanup after lifetime
	await get_tree().create_timer(lifetime).timeout
	queue_free()
