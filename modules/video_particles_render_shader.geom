layout(points) in;
layout(triangle_strip, max_vertices = 4) out;

uniform float uFaceCam;

in Vertex
{
	vec4 color;
	vec4 pos;
	flat uint instanceID; 
	float scale;
	vec3 angle;
} vVert[];
 
out Vertex
{
	vec4 color;
	vec2 texCoord0;
	flat uint instanceID;
}vVerts;

mat4 rotationX( in float angle ) {
	return mat4(	1.0,		0,			0,			0,
			 		0, 	cos(angle),	-sin(angle),		0,
					0, 	sin(angle),	 cos(angle),		0,
					0, 			0,			  0, 		1);
}

mat4 rotationY( in float angle ) {
	return mat4(	cos(angle),		0,		sin(angle),	0,
			 				0,		1.0,			 0,	0,
					-sin(angle),	0,		cos(angle),	0,
							0, 		0,				0,	1);
}

mat4 rotationZ( in float angle ) {
	return mat4(	cos(angle),		-sin(angle),	0,	0,
			 		sin(angle),		cos(angle),		0,	0,
							0,				0,		1,	0,
							0,				0,		0,	1);
}

void main (void)
{

	// send the whole array over to the pixel shader

	float particle_size = vVert[0].scale;
	particle_size = vVert[0].scale;
	mat4 projMatrix = uTDMat.proj;
	vec4 P = vVert[0].pos;
	float uBillBoard = uFaceCam;
	vec4 rotPos = vec4(0.0);

	// a: left-bottom
	vec4 va = vec4(P.xy + vec2(-0.5, -0.5) * particle_size,P.zw);
	if (uBillBoard == 0.0){
		va = P + vec4(vec2(-0.5, -0.5) * particle_size,vec2(0.0)) * rotationX(vVert[0].angle.x) * rotationY(vVert[0].angle.y);
	}
	gl_Position = projMatrix * va;
	vVerts.texCoord0 = vec2(0.0, 0.0);
	vVerts.color = vVert[0].color;
	vVerts.instanceID = vVert[0].instanceID;
	EmitVertex();

	// b: left-top
	vec4 vb = vec4(P.xy + vec2(-0.5, 0.5) * particle_size,P.zw);
	if (uBillBoard == 0.0){
		vb = P + vec4(vec2(-0.5, 0.5) * particle_size,vec2(0.0)) * rotationX(vVert[0].angle.x) * rotationY(vVert[0].angle.y);
	}
	gl_Position = projMatrix * vb;
	vVerts.texCoord0 = vec2(0.0, 1.0);
	vVerts.color = vVert[0].color;
	vVerts.instanceID = vVert[0].instanceID;
	EmitVertex();

	// d: right-bottom
	vec4 vd = vec4(P.xy + vec2(0.5, -0.5) * particle_size,P.zw);
	if (uBillBoard == 0.0){
		vd = P + vec4(vec2(0.5, -0.5) * particle_size,vec2(0.0)) * rotationX(vVert[0].angle.x) * rotationY(vVert[0].angle.y);
	}
	gl_Position = projMatrix * vd;
	vVerts.texCoord0 = vec2(1.0, 0.0);
	vVerts.color = vVert[0].color;
	vVerts.instanceID = vVert[0].instanceID;
	EmitVertex();

	// c: right-top
	vec4 vc = vec4(P.xy + vec2(0.5, 0.5) * particle_size,P.zw);
	if (uBillBoard == 0.0){
		vc = P + vec4(vec2(0.5, 0.5) * particle_size,vec2(0.0)) * rotationX(vVert[0].angle.x) * rotationY(vVert[0].angle.y);
	}
	gl_Position = projMatrix * vc;
	vVerts.texCoord0 = vec2(1.0, 1.0);
	vVerts.color = vVert[0].color;
	vVerts.instanceID = vVert[0].instanceID;
	EmitVertex();

	EndPrimitive();
}