extends Camera2D

var shake_amount = 0.0
var shake_decay = 5.0

func _ready():
	pass

func _process(delta):
	if shake_amount > 0:
		shake_amount = max(shake_amount - shake_decay * delta, 0)
		if shake_amount > 0.01:  # Only apply shake if significant
			offset = Vector2(
				randf_range(-shake_amount, shake_amount),
				randf_range(-shake_amount, shake_amount)
			)
		else:
			offset = Vector2.ZERO
			shake_amount = 0  # Reset to prevent tiny values
	else:
		offset = Vector2.ZERO

func shake(amount: float):
	shake_amount = amount

func trauma_shake(trauma: float):
	# Trauma is 0-1, converts to shake amount
	shake_amount = trauma * 10.0
