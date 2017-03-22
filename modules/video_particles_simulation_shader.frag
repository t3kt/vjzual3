// uniforms
uniform vec3 uLimitPos;
uniform vec3 uLimitNeg;
uniform vec4 uExternalForce;
uniform float uExternalVariance;
uniform vec4 uWind;
uniform float uWindVariance;
uniform float uLife;
uniform float uLifeVariance;
uniform float uFPS;
uniform float uDragM;
uniform float uMass;
uniform vec4 uTurbulence;
uniform float uTurbJitterM;
uniform vec4 uRotationM;
uniform vec4 uRotationInit;
uniform int uHit;
uniform vec4 uOriginBounds;

layout(location = 0) out vec4 oPosAndLife;
layout(location = 1) out vec4 oVelocity;
layout(location = 2) out vec4 oRotation;
layout(location = 3) out vec4 oLife;
layout(location = 4) out vec4 test;
layout(location = 5) out vec4 oOriginPos;

// 2D Input textures are:
#define POS_LIFE 0
#define VELOCITY 1
#define POS_NOISE 2
#define ROTATION 3
#define ROTATIONINIT 4
#define VARIANCE 5
#define SOURCE 6
#define LIFE 7
#define ALIFE 8
#define ORIGIN_POS 9

// 3D Input textures are:
#define TURBULENCE 10

float reMap(in float value, in float low1, in float high1, in float low2, in float high2){
	return float(low2 + (value - low1) * (high2 - low2) / (high1 - low1));
}

vec2 reMap(in vec2 value, in vec2 low1, in vec2 high1, in vec2 low2, in vec2 high2){
	return vec2(low2 + (value - low1) * (high2 - low2) / (high1 - low1));
}

vec3 reMap(in vec3 value, in vec3 low1, in vec3 high1, in vec3 low2, in vec3 high2){
	return vec3(low2 + (value - low1) * (high2 - low2) / (high1 - low1));
}

// new particle is born
void birthParticle(in vec4 noiseVals, in vec4 variance, out vec4 posLife, out vec4 life, out vec4 velocity, inout vec4 rotation, in vec4 uRotationInit, out vec4 originPos)
{
	vec4 sourcePos = texture(sTD2DInputs[SOURCE], vec2(noiseVals.x,0.25));
	vec4 sourceVelocity = texture(sTD2DInputs[SOURCE], vec2(noiseVals.x,0.75));
	// calculate life and variance
	life.rg = vec2(uLife + variance.b*uLifeVariance);
	life.b = 1.0;
	posLife.xyz = sourcePos.xyz;
	posLife.w = 1.0;
	velocity = vec4(vec3(sourceVelocity*0.01),0.0);
	rotation = texture(sTD2DInputs[ROTATIONINIT], vUV.st) * uRotationInit * 360.0;
	originPos.xy = reMap(sourcePos.xy, uOriginBounds.xy, uOriginBounds.zw, vec2(0.0), vec2(1.0));
}

// apply external forces such as gravity
vec3 externalForce(in vec4 variance)
{
	vec3 force = (uExternalForce.xyz + (abs(variance.r) * uExternalVariance) * sign(uExternalForce.xyz)) * uExternalForce.w/100.0;
	return force / uFPS;
}

// apply wind force
vec3 windForce(in vec4 variance, in vec4 velocity)
{
	vec3 force = (uWind.xyz + (abs(variance.g) * uWindVariance) * sign(uWind.xyz)) * uWind.w/100.0;
	bvec3 windLimit = lessThan(abs(velocity.xyz),abs(force));
	return force/uFPS * vec3(float(windLimit.x),float(windLimit.y),float(windLimit.z));
}

// apply turbulence
vec3 turbulence(in vec3 posMoveUV, in vec4 noiseValsNorm)
{
	vec3 turb = texture(sTD2DInputs[TURBULENCE], vUV.st).gba;
	turb += noiseValsNorm.xyz * uTurbJitterM;
	return turb.xyz * (uTurbulence.xyz * uTurbulence.w/uFPS);
}

// apply turbulence by Kinect

void main()
{
	vec4 posLife = texture(sTD2DInputs[POS_LIFE], vUV.st);
	vec4 velocity = texture(sTD2DInputs[VELOCITY], vUV.st);
	vec4 rotationInit = texture(sTD2DInputs[ROTATIONINIT], vUV.st);
	vec4 rotation = texture(sTD2DInputs[ROTATION], vUV.st);
	vec4 variance = texture(sTD2DInputs[VARIANCE], vUV.st);
	vec4 life = texture(sTD2DInputs[LIFE], vUV.st);
	float clampVal = uTD2DInfos[SOURCE].res.x;
	vec4 alife = texture(sTD2DInputs[ALIFE], vUV.st);
	vec4 noiseVals = texture(sTD2DInputs[POS_NOISE], vUV.st);
	vec4 noiseValsNorm = noiseVals - 0.5;
	vec4 originPos = texture(sTD2DInputs[ORIGIN_POS], vUV.st);

	noiseValsNorm *= 2.0;
	vec3 pos = vec3(0.0);
	vec3 force = vec3(0.0);
	
	if (life.g < 0.0 && life.b > 0.0)
	{
		// life.rgb = vec3(0.0);
		birthParticle(noiseVals, variance, posLife, life, velocity, rotation, uRotationInit, originPos);
	}


	// decide if we need to birth something
	 //if (alife.b < 0.5){
		// birthParticle(noiseVals, variance, posLife, life, velocity, rotation, uRotationInit, originPos);	
	//}
	// simulate
	else 
	{
		vec3 posMoveUV;
		posMoveUV = posLife.xyz / vec3(uLimitPos.x-uLimitNeg.x,uLimitPos.y-uLimitNeg.y,uLimitPos.z-uLimitNeg.z);
		posMoveUV += 1.0;
		posMoveUV *= 0.5;

		posLife.xyz += velocity.xyz;

		// apply external force
		velocity.xyz += externalForce(variance);

		// apply wind
		velocity.xyz += windForce(variance, velocity);
		
		// apply turbulence
		velocity.xyz += turbulence(posMoveUV, noiseValsNorm);

		// apply drag
		velocity *= uDragM;

		// apply rotation
		rotation.rg += (rotationInit.xy*uRotationM.xy) + (uRotationM.xy * velocity.xy);

		// is the point offscreen?
		if (posLife.x > uLimitPos.x || posLife.y > uLimitPos.y || posLife.z > uLimitPos.z || posLife.x < uLimitNeg.x || posLife.y < uLimitNeg.y || posLife.z < uLimitNeg.z)
		{
			if (uHit == 0) 
			{
				// posLife.w = 0.0;
				life.rgb = vec3(0.0);
				birthParticle(noiseVals, variance,  posLife, life, velocity, rotation, uRotationInit, originPos);
			}
			else
			{
				velocity *= -1.0;
			}
		}
		life.g -= 1.0/uFPS;
	}
	oPosAndLife = vec4(posLife.xyz,1.0);
	oVelocity = velocity;
	oRotation = rotation;
	oLife = life;
	oOriginPos = originPos;
	test = vec4(0.0,0.0,pos.z,0.0);
}
	
