// Sampling modes:
// - SAMPLE_MODE_CROSS: single line in each direction up/down/left/right
// - SAMPLE_MODE_GRID: full surrounding rectangle grid

// Scoring modes:
// - SCORE_R / SCORE_G / SCORE_B / SCORE_A
// - SCORE_LUMA

// Selection modes:
// - SELECTION_MODE_BEST - single target with best (maximum) score
// - SELECTION_MODE_WEIGHTED - combination of all targets weighted by score

// Number of steps in each direction (x/y)
uniform ivec2 numSteps;

// Sampling distance range (near x, near y, far x, far y)
uniform vec4 sampleRange;

// Near sampling distance (x/y)
#define sampleRangeMin sampleRange.xy

// Far sampling distance (x/y)
#define sampleRangeMax sampleRange.zw

// Range (min/max) of elligible target scores
uniform vec2 scoreRange;

// Settings for how target distance impacts pull weight
uniform vec4 distPullWeightSettings;

#define distPullNearWeight      distPullWeightSettings.x
#define distPullMidWeight       distPullWeightSettings.y
#define distPullMidWeightRatio  distPullWeightSettings.z
#define distPullFarWeight       distPullWeightSettings.w

#define sampleTex sTD2DInputs[0]

layout(location = 0) out vec4 offsetOut;

layout(location = 1) out vec4 targetOut;

struct Result {
	vec2 targetRelPos;
	float weight;
	#ifdef SELECTION_MODE_BEST
		float score;
	#endif
};


float map(float value, float inMin, float inMax, float outMin, float outMax);
vec2 map(vec2 value, vec2 inMin, vec2 inMax, vec2 outMin, vec2 outMax);
vec3 map(vec3 value, vec3 inMin, vec3 inMax, vec3 outMin, vec3 outMax);
vec4 map(vec4 value, vec4 inMin, vec4 inMax, vec4 outMin, vec4 outMax);
float czm_luminance(vec3 rgb);

//#ifdef SCORE_R
//	#define getScore(c) (c.r)
//#elif defined SCORE_G
//	#define getScore(c) (c.g)
//#elif defined SCORE_B
//	#define getScore(c) (c.b)
//#elif defined SCORE_A
//	#define getScore(c) (c.a)
//#elif defined SCORE_LUMA
//	#define getScore(c) czm_luminance(c.rgb)
//#else
//  #define getScore(c) (c.r)
//#endif

float getScore(vec4 c) {
	#ifdef SCORE_R
		return c.r;
	#elif defined SCORE_G
		return c.g;
	#elif defined SCORE_B
		return c.b;
	#elif defined SCORE_A
		return c.a;
	#elif defined SCORE_LUMA
		return czm_luminance(c.rgb);
	#else
	  return c.r;
	#endif
}

float getDistancePullWeight(float distRatio) {
	if (distRatio < distPullMidWeightRatio) {
		return map(distRatio, 0, distPullMidWeightRatio, distPullNearWeight, distPullMidWeight);
	} else {
		return map(distRatio, distPullMidWeightRatio, 1, distPullMidWeight, distPullFarWeight);
	}
}

void handleTarget(
		in vec2 uv,
		in vec2 relPos,
		in float sampleFraction,
		inout Result result) {
	vec4 color = texture(sampleTex, uv + relPos);
	float score = getScore(color);
	if (score < scoreRange.x || score > scoreRange.y) {
		return;
	}
	#ifdef SELECTION_MODE_WEIGHTED
		float weight = score * sampleFraction;
		result.targetRelPos += relPos * weight;
	#else // BEST (max)
		if (score > result.score) {
			result.targetRelPos = relPos;
			result.score = score;
		}
	#endif
}

#ifdef SAMPLE_MODE_GRID

void handleTargetGrid(
		in vec2 uv,
		in vec2 step,
		in float sampleFraction,
		inout Result result) {
	vec2 stepSign = sign(step);
	vec2 relPos = stepSign *
		map(abs(step),
			vec2(0), vec2(numSteps)-vec2(1),
			sampleRangeMin, sampleRangeMax);
	handleTarget(
		uv,
		relPos,
		sampleFraction,
		result);
}
#endif

Result produceResult() {
	vec2 uv = vUV.st;
	Result result;
	result.targetRelPos = vec2(0);
	#ifdef SELECTION_MODE_BEST
		result.score = 0;
	#endif

	float centerScore = getScore(texture(sampleTex, uv));
	if (centerScore > scoreRange.y) {
		#ifdef SELECTION_MODE_BEST
			result.score = centerScore;
		#endif
		return result;
	}

	#ifdef SAMPLE_MODE_CROSS
		float sampleFraction = 1 / ((float(numSteps.x)*2) + (float(numSteps.y)*2));



		// TODO!

	#else // GRID
		float sampleFraction = 1.0 / float(numSteps.x * numSteps.y);

		for (int x = 0; x < numSteps.x; x++) {
			for (int y = 0; y < numSteps.y; y++) {
				handleTargetGrid(uv, vec2(x, y), sampleFraction, result);
				handleTargetGrid(uv, vec2(-x, y), sampleFraction, result);
				handleTargetGrid(uv, vec2(x, -y), sampleFraction, result);
				handleTargetGrid(uv, vec2(-x, -y), sampleFraction, result);
			}
		}

	#endif

	// calculate the weight at the end so it only runs once
	result.weight = getDistancePullWeight(length(result.targetRelPos));

	return result;
}


void outputResult(Result result) {
	// normalize relpos to -1 to 1 range
	vec2 normalizedRelPos = sign(result.targetRelPos) * map(abs(result.targetRelPos), sampleRangeMin, sampleRangeMax, vec2(0), vec2(1));

	targetOut = vec4(map(normalizedRelPos, vec2(-1), vec2(1), vec2(0), vec2(1)), 0, result.weight);
//	if (result.weight <= 0) {
//		offsetOut = vec4(0.5, 0.5, 0, 0);
//	} else {
		offsetOut = vec4(
			map(-normalizedRelPos * result.weight, vec2(-1), vec2(1), vec2(0), vec2(1)),
			0, result.weight);
//	}
}

void main()
{
	Result result = produceResult();
	outputResult(result);
}
