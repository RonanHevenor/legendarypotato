extends CharacterBody2D

@export var speed = 100.0

@onready var animated_sprite = $AnimatedSprite2D

var last_direction = "down"

func _physics_process(delta):
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
				animated_sprite.play("walk_right")
			else:
				last_direction = "left"
				animated_sprite.play("walk_left")
		else:
			if input_dir.y > 0:
				last_direction = "down"
				animated_sprite.play("walk_down")
			else:
				last_direction = "up"
				animated_sprite.play("walk_up")
	else:
		# Play idle animation based on last direction
		animated_sprite.play("idle_" + last_direction)

	# Move the player
	move_and_slide()
