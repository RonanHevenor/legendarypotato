shader_type canvas_item;

uniform float glow_intensity : hint_range(0.0, 2.0) = 1.0;
uniform vec4 glow_color : source_color = vec4(1.0, 1.0, 0.0, 1.0);

void fragment() {
	vec4 col = texture(TEXTURE, UV);
	vec3 glow = glow_color.rgb * glow_intensity;
	COLOR.rgb = col.rgb + glow * col.a;
	COLOR.a = col.a;
}
