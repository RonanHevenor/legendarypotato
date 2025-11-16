shader_type canvas_item;

uniform float pixel_size : hint_range(1.0, 32.0) = 4.0;

void fragment() {
	vec2 uv = UV;
	
	// Pixelate effect
	vec2 pixel_uv = floor(uv * float(textureSize(TEXTURE, 0)) / pixel_size) * pixel_size / float(textureSize(TEXTURE, 0));
	
	COLOR = texture(TEXTURE, pixel_uv);
}
