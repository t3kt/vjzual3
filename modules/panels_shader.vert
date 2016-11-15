out Vertex {
	vec4 color;
	vec3 camSpaceVert;
	vec3 texCoord0;
	vec3 texCoord1;
}vVert;

void main()
{
	// First deform the vertex and normal
	// TDDeform always returns values in world space
	vec4 worldSpaceVert =TDDeform(P);
	vec4 camSpaceVert = uTDMat.cam * worldSpaceVert;
	gl_Position = TDCamToProj(camSpaceVert);

	// This is here to ensure we only execute lighting etc. code
	// when we need it. If picking is active we don't need this, so
	// this entire block of code will be ommited from the compile.
	// The TD_PICKING_ACTIVE define will be set automatically when
	// picking is active.
#ifndef TD_PICKING_ACTIVE

	{ // Avoid duplicate variable defs
		vec3 texcoord = TDInstanceTexCoord(uv[0]);
		vVert.texCoord0.stp = texcoord.stp;
		//vVert.texCoord0.p = texcoord.p + sColorMapPOffset;
	}
	{
		vVert.texCoord1.stp = uv[1];
	}
	vec3 camSpaceNorm = uTDMat.camForNormals * TDDeformNorm(N).xyz;
	vVert.camSpaceVert.xyz = camSpaceVert.xyz;
	vVert.color = TDInstanceColor(Cd);

#else // TD_PICKING_ACTIVE

	// This will automatically write out the nessessary values
	// for this shader to work with picking.
	// See the documentation if you want to write custom values for picking.
	TDWritePickingValues();

#endif // TD_PICKING_ACTIVE
}
