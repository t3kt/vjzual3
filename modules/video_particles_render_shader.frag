uniform vec4 uColorRGBA;
uniform float uTextureDepth;
uniform sampler2DArray uTexture;

in Vertex {
	vec4 color;
	vec2 texCoord0;
	flat uint instanceID;
}vVerts;

// Output variable for the color
layout(location = 0) out vec4 fragColor[TD_NUM_COLOR_BUFFERS];
void main()
{
	TDCheckOrderIndTrans();
	int texId = int(vVerts.instanceID)%int(uTextureDepth);
	//vec4 colorMapColor = texture(uTexture, vec3(vVerts.texCoord0.st,texId));
	vec4 colorMapColor = vVerts.color;
	//colorMapColor.a *= vVerts.color.a;
	fragColor[0] = uColorRGBA * colorMapColor;
	// TD_NUM_COLOR_BUFFERS will be set to the number of color buffers
	// active in the render. By default we want to output zero to every
	// buffer except the first one.
	for (int i = 1; i < TD_NUM_COLOR_BUFFERS; i++)
	{
		fragColor[i] = vec4(0.0);
	}
}