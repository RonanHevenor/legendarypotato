shader_type canvas_item;

uniform vec2 scroll_speed = vec2(0.02, 0.01);
uniform vec4 tint_color : source_color = vec4(0.1, 0.1, 0.2, 1.0);
uniform float darkness : hint_range(0.0, 1.0) = 0.3;

void fragment() {
	vec2 uv = UV + scroll_speed * TIME;
	vec4 color = texture(TEXTURE, uv);
	
	// Apply tint and darken
	color.rgb = mix(color.rgb, tint_color.rgb, darkness);
	
	COLOR = color;
}
