shader_type canvas_item;

uniform float vignette_intensity : hint_range(0.0, 1.0) = 0.3;
uniform float vignette_opacity : hint_range(0.0, 1.0) = 0.5;

void fragment() {
	vec4 color = texture(TEXTURE, UV);
	
	// Calculate distance from center
	vec2 center = vec2(0.5, 0.5);
	float dist = distance(UV, center);
	
	// Create vignette effect
	float vignette = 1.0 - smoothstep(1.0 - vignette_intensity, 1.0, dist);
	
	// Apply vignette
	color.rgb = mix(color.rgb, color.rgb * vignette, vignette_opacity);
	
	COLOR = color;
}
