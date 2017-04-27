#define W_OFFSET uTD3DInfos[0].depth.z

vec4 getDelayTap(float length) {
	return texture(sTD3DInputs[0], vec3(vUV.st, length + W_OFFSET));
}

vec4 getTapResult(int i) {
	return getDelayTap(uTapVals[i][TAP_LENGTH]);
}

vec4 getZeroTap() {
    return texture(sTD3DInputs[0], vec3(vUV.st, W_OFFSET));
}
