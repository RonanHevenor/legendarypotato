extends ColorRect

signal transition_finished

var is_transitioning = false

func _ready():
	color = Color.BLACK
	modulate.a = 0.0
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	visible = true  # Ensure it's visible when needed

func fade_in(duration: float = 0.5):
	if is_transitioning:
		return
	
	is_transitioning = true
	mouse_filter = Control.MOUSE_FILTER_STOP
	
	var tween = create_tween()
	tween.tween_property(self, "modulate:a", 1.0, duration)
	await tween.finished
	
	transition_finished.emit()
	is_transitioning = false

func fade_out(duration: float = 0.5):
	if is_transitioning:
		return
	
	is_transitioning = true
	
	var tween = create_tween()
	tween.tween_property(self, "modulate:a", 0.0, duration)
	await tween.finished
	
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	transition_finished.emit()
	is_transitioning = false

func fade_in_out(hold_duration: float = 0.5, fade_duration: float = 0.5):
	await fade_in(fade_duration)
	await get_tree().create_timer(hold_duration).timeout
	await fade_out(fade_duration)

# Flash effect for dramatic moments
func flash(color_override: Color = Color.WHITE, duration: float = 0.2):
	var original_color = color
	color = color_override
	modulate.a = 1.0
	
	var tween = create_tween()
	tween.tween_property(self, "modulate:a", 0.0, duration)
	await tween.finished
	
	color = original_color
