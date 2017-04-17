uniform vec4 uColor;

uniform sampler2DArray sColorMap;
uniform sampler2D sMaskMap;

in Vertex {
	vec4 color;
	vec3 worldSpacePos;
	vec3 worldSpaceNorm;
	vec3 texCoord0;
	vec3 texCoord1;
	flat int cameraIndex;
}vVert;

// Output variable for the color
layout(location = 0) out vec4 fragColor[TD_NUM_COLOR_BUFFERS];
void main()
{
	// This allows things such as order independent transparency
	// and Dual-Paraboloid rendering to work properly
	TDCheckDiscard();

	vec4 outcol = vec4(0.0, 0.0, 0.0, 0.0);

	vec3 texCoord0 = vVert.texCoord0.stp;
	vec4 colorMapColor = texture(sColorMap, texCoord0.stp);
	vec4 maskMapColor = texture(sMaskMap, vVert.texCoord1.st);
	colorMapColor.a *= maskMapColor.a;

	outcol = colorMapColor * uColor;


	// Apply fog, this does nothing if fog is disabled
	outcol = TDFog(outcol, vVert.worldSpacePos, vVert.cameraIndex);

	// Alpha Calculation
	float alpha = uColor.a * vVert.color.a * colorMapColor.a ;

	// Dithering, does nothing if dithering is disabled
	outcol = TDDither(outcol);

	outcol.rgb *= alpha;

	// Modern GL removed the implicit alpha test, so we need to apply
	// it manually here. This function does nothing if alpha test is disabled.
	TDAlphaTest(alpha);

	outcol.a = alpha;
	fragColor[0] = TDOutputSwizzle(outcol);


	// TD_NUM_COLOR_BUFFERS will be set to the number of color buffers
	// active in the render. By default we want to output zero to every
	// buffer except the first one.
	for (int i = 1; i < TD_NUM_COLOR_BUFFERS; i++)
	{
		fragColor[i] = vec4(0.0);
	}
}
