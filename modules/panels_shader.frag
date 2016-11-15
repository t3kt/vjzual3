uniform vec4 uColor;

uniform sampler2DArray  sColorMap;
uniform sampler2D sMaskMap;

in Vertex {
	vec4 color;
	vec3 camSpaceVert;
	vec3 texCoord0;
	vec3 texCoord1;
}vVert;

// Output variable for the color
layout(location = 0) out vec4 fragColor[TD_NUM_COLOR_BUFFERS];
void main()
{
	// This allows things such as order independent transparency
	// and Dual-Paraboloid rendering to work properly
	TDCheckDiscard();

	vec4 outcol = uColor;

	vec3 texCoord0 = vVert.texCoord0.stp;
	vec3 texCoord1 = vVert.texCoord1.stp;
	vec4 colorMapColor = texture(sColorMap, texCoord0.stp);
	vec4 maskColor = texture(sMaskMap, texCoord1.st);

	outcol *= colorMapColor * maskColor;


	// Apply fog, this does nothing if fog is disabled
	outcol = TDFog(outcol, vVert.camSpaceVert);

	// Alpha Calculation
	float alpha = uColor.a * vVert.color.a * colorMapColor.a * maskColor.a;

	// Dithering, does nothing if dithering is disabled
	outcol = TDDither(outcol);

	fragColor[0].rgb = outcol.rgb * alpha;
	fragColor[0].a = alpha;


	// TD_NUM_COLOR_BUFFERS will be set to the number of color buffers
	// active in the render. By default we want to output zero to every
	// buffer except the first one.
	for (int i = 1; i < TD_NUM_COLOR_BUFFERS; i++)
	{
		fragColor[i] = vec4(0.0);
	}
}
