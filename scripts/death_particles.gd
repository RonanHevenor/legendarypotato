extends CPUParticles2D

func _ready():
	emitting = false
	one_shot = true
	explosiveness = 1.0
	amount = 30
	lifetime = 1.0
	speed_scale = 1.5
	
	# Emission
	emission_shape = EMISSION_SHAPE_SPHERE
	emission_sphere_radius = 8.0
	
	# Movement
	direction = Vector2(0, -1)
	spread = 180
	gravity = Vector2(0, 150)
	initial_velocity_min = 80.0
	initial_velocity_max = 150.0
	
	# Scale
	scale_amount_min = 3.0
	scale_amount_max = 6.0
	
	# Color (grey/smoke)
	color = Color(0.5, 0.5, 0.5, 0.8)
	
func emit_particles():
	emitting = true
	await get_tree().create_timer(lifetime).timeout
	queue_free()
