extends CPUParticles2D

func _ready():
	# Subtle ambient dust particles - much lighter for performance
	emitting = false  # Disabled by default for performance - enable manually if needed
	amount = 8  # Reduced from 50
	lifetime = 4.0
	preprocess = 1.0
	speed_scale = 0.3

	# Emission - smaller area
	emission_shape = EMISSION_SHAPE_RECTANGLE
	emission_rect_extents = Vector2(200, 150)  # Reduced from 400x300

	# Movement - slower
	direction = Vector2(0, -1)
	spread = 45
	gravity = Vector2(0, -5)  # Much lighter gravity
	initial_velocity_min = 5.0
	initial_velocity_max = 15.0

	# Scale - smaller particles
	scale_amount_min = 0.5
	scale_amount_max = 1.5

	# Color (very subtle dust)
	color = Color(0.95, 0.95, 0.95, 0.1)
