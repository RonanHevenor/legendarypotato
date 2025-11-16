shader_type canvas_item;

uniform float aberration_amount : hint_range(0.0, 0.01) = 0.002;

void fragment() {
	vec2 uv = UV;
	
	// Sample RGB channels at different offsets
	float r = texture(TEXTURE, uv + vec2(aberration_amount, 0.0)).r;
	float g = texture(TEXTURE, uv).g;
	float b = texture(TEXTURE, uv - vec2(aberration_amount, 0.0)).b;
	float a = texture(TEXTURE, uv).a;
	
	COLOR = vec4(r, g, b, a);
}
