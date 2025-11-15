extends Node2D

signal door_entered

@onready var area = $Area2D

func _ready():
	area.body_entered.connect(_on_body_entered)

func _on_body_entered(body):
	if body.name == "Player":
		door_entered.emit()
		print("Player entered door!")
