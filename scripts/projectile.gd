extends Area2D

@export var speed: float = 300.0
@export var damage: int = 15
@export var lifetime: float = 3.0

var direction: Vector2 = Vector2.RIGHT
var shooter: Node2D = null

func _ready():
	# Set collision layer for projectiles
	collision_layer = 128  # Projectiles layer
	collision_mask = 4 + 8  # Enemies + EnemyHurtBox

	$VisibleOnScreenNotifier2D.screen_exited.connect(queue_free)

	# Auto-destroy after lifetime
	await get_tree().create_timer(lifetime).timeout
	queue_free()

func _physics_process(delta):
	position += direction * speed * delta

func _on_body_entered(body):
	if body == shooter:
		return  # Don't hit shooter

	if body.has_method("take_damage"):
		body.take_damage(damage)
		queue_free()  # Destroy projectile on hit

func set_direction(new_direction: Vector2):
	direction = new_direction.normalized()

func set_shooter(new_shooter: Node2D):
	shooter = new_shooter