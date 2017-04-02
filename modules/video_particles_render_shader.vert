uniform vec4 uAmbientColor;
uniform vec4 uDiffuseColor;
uniform vec3 uSpecularColor;
uniform float uShininess;
uniform float uShadowStrength;
uniform vec3 uShadowColor;
uniform vec3 uParticleSize;
uniform vec2 uParticleSizeVariance;
uniform vec2 uLifeFade;
uniform float uFaceCam;
uniform vec3 uLimitNeg;
uniform vec3 uLimitPos;
uniform float depthOffset;

out Vertex {
	vec4 color;
	vec4 pos;
	flat uint instanceID;
	float scale;
	vec3 angle;
}vVert;

in float objIndex;
uniform int uParticlesPerInstance;
uniform vec4 uMapSize; // contains (1 / w, 1/h, w, h)
uniform sampler2D sPosition;
uniform sampler2D size;
uniform sampler2D sLife;
uniform sampler2D rotation;
uniform sampler2D sOriginPos;
uniform sampler3D sColorMap;


float reMap(in float value, in float low1, in float high1, in float low2, in float high2){
	return float(low2 + (value - low1) * (high2 - low2) / (high1 - low1));
}

vec3 reMap(in vec3 value, in vec3 low1, in vec3 high1, in vec3 low2, in vec3 high2){
	return vec3(low2 + (value - low1) * (high2 - low2) / (high1 - low1));
}

void main()
{
	int partIndex = (uParticlesPerInstance * gl_InstanceID) + int(objIndex);
	vVert.instanceID = uint(partIndex);

	int rowX = partIndex % int(uMapSize.z);
	int rowY = partIndex / int(uMapSize.z);

	vec2 posUV = vec2((float(rowX) + 0.5) * uMapSize.x,
						(float(rowY) + 0.5) * uMapSize.y);

	vec4 positionOffset = texture(sPosition, posUV);
	if (positionOffset.w <= 0.0)
	{
		gl_Position = vec4(-1.0);
		return;
	}

	float scale = texture(size, posUV).r;
	vVert.scale = uParticleSizeVariance.x + scale * (uParticleSizeVariance.y - uParticleSizeVariance.x);
	vVert.angle = texture(rotation, posUV).rgb;

	vec4 tempPos = vec4(P,0.0);
	vec4 position = vec4(tempPos.xyz + positionOffset.xyz, 1.0);
	gl_Position = uTDMat.worldCam * position;
	vVert.pos = gl_Position;
	
	// This is here to ensure we only execute lighting etc. code
	// when we need it. If picking is active we don't need this, so
	// this entire block of code will be ommited from the compile.
	// The TD_PICKING_ACTIVE define will be set automatically when
	// picking is active.
#ifndef TD_PICKING_ACTIVE

	vec4 life = texture(sLife, posUV);
	vec4 color = TDInstanceColor(Cd);
	vec3 colorUV = vec3(texture(sOriginPos, posUV).xy, reMap(position.z, uLimitNeg.z, uLimitPos.z, 0.0, 1.0));
	colorUV.z += depthOffset;
	color *= texture(sColorMap, colorUV);

	// apply fadein and fadeout
	float fadeIn = reMap(min(life.r-life.g,uLifeFade.x),0.0,uLifeFade.x,0.0,1.0);
	float fadeOut = reMap(min(life.g,uLifeFade.y),uLifeFade.y,0.0,0.0,1.0);
	float fade = fadeIn - fadeOut;

	color.a = mix(0.0,1.0,fade);
	vVert.color = color;

#else // TD_PICKING_ACTIVE

	// This will automatically write out the nessesarily values
	// for this shader to work with picking.
	// See the documentation if you want to write custom values for picking.
	TDWritePickingValues();

#endif // TD_PICKING_ACTIVE
}
