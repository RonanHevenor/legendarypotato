extends CanvasLayer
## UI for generating AI characters in-game

@onready var line_edit = $Panel/VBoxContainer/LineEdit
@onready var generate_button = $Panel/VBoxContainer/HBoxContainer/GenerateButton
@onready var cancel_button = $Panel/VBoxContainer/HBoxContainer/CancelButton
@onready var progress_bar = $Panel/VBoxContainer/ProgressBar
@onready var status_label = $Panel/VBoxContainer/StatusLabel

var character_loader: Node
var is_generating: bool = false

func _ready():
	# Load the character loader
	var loader_script = load("res://scripts/ai_character_loader.gd")
	character_loader = loader_script.new()
	add_child(character_loader)

	# Connect progress signal
	character_loader.progress_updated.connect(_on_progress_updated)

	# Start hidden
	hide()

	# Hide progress bar initially
	progress_bar.hide()

	# Connect line edit to submit on Enter
	line_edit.text_submitted.connect(_on_text_submitted)


func _input(event):
	# Toggle UI with Tab key
	if event is InputEventKey and event.pressed and event.keycode == KEY_TAB:
		if visible:
			hide()
		else:
			show()
			line_edit.grab_focus()
		get_viewport().set_input_as_handled()


func _on_text_submitted(text: String):
	if not text.is_empty() and not is_generating:
		_start_generation(text)


func _on_generate_pressed():
	var description = line_edit.text.strip_edges()
	if description.is_empty():
		status_label.text = "Please enter a character description"
		return

	_start_generation(description)


func _on_cancel_pressed():
	if is_generating:
		status_label.text = "Cannot cancel while generating..."
	else:
		hide()


func _start_generation(description: String):
	if is_generating:
		return

	is_generating = true
	generate_button.disabled = true
	line_edit.editable = false
	progress_bar.value = 0
	progress_bar.show()
	status_label.text = "Generating '" + description + "'..."
	print("=== UI: Starting generation for: " + description + " ===")

	# Get the player node
	var player = get_tree().get_first_node_in_group("player")
	if not player:
		status_label.text = "Error: Player not found!"
		_reset_ui()
		return

	print("UI: Found player, calling generate_and_load...")

	# Generate character with progress updates
	var success = await character_loader.generate_and_load(description, player)

	print("=== UI: Done! Success = " + str(success) + " ===")

	if success:
		progress_bar.value = 100
		status_label.text = "SUCCESS! Character loaded!"
	else:
		status_label.text = "FAILED - Check Output console"

	await get_tree().create_timer(1.0).timeout
	_reset_ui()


func _on_generation_complete():
	status_label.text = "Character loaded! Press Tab to close"
	_reset_ui()


func _on_progress_updated(progress: int):
	progress_bar.value = progress
	status_label.text = "Generating... " + str(progress) + "%"


func _reset_ui():
	is_generating = false
	generate_button.disabled = false
	line_edit.editable = true
	progress_bar.hide()
	progress_bar.value = 0
