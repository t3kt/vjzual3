uniform vec4 tapAlphaA;
uniform vec4 tapAlphaB;
uniform int stepCompMode;
uniform int tapCount;
uniform int tapFilter0;
uniform int tapFilter1;
uniform int tapFilter2;
uniform int tapFilter3;
uniform int tapFilter4;
uniform int tapFilter5;
uniform int tapFilter6;
uniform int tapFilter7;

#define COMP_ADD 0
#define COMP_ATOP 1
#define COMP_AVERAGE 2
#define COMP_DIFFERENCE 3
#define COMP_INSIDE 4
#define COMP_MAXIMUM 5
#define COMP_MINIMUM 6
#define COMP_MULTIPLY 7
#define COMP_OUTSIDE 8
#define COMP_OVER 9
#define COMP_SCREEN 10
#define COMP_SUBTRACT 11
#define COMP_UNDER 12

#define FILT_NONE 0
#define FILT_RED 1
#define FILT_GREEN 2
#define FILT_BLUE 3
#define FILT_REDALPHA 4
#define FILT_GREENALPHA 5
#define FILT_BLUEALPHA 6
#define FILT_LUMAALPHA 7

vec4 applyFilter(vec4 color, int mode) {
    if (color.a <= 0.0) {
        return vec4(0.0);
    }
    if (mode <= 0) {
        return color;
    }
    switch (mode) {
    case FILT_RED:
        return color * vec4(1.0, 0.0, 0.0, 1.0);
    case FILT_GREEN:
        return color * vec4(0.0, 1.0, 0.0, 1.0);
    case FILT_BLUE:
        return color * vec4(0.0, 0.0, 1.0, 1.0);
    case FILT_LUMAALPHA:
        return vec4(color.rgb, czm_luminance(color.rgb));
    }
    if (mode >= FILT_REDALPHA && mode <= FILT_BLUEALPHA) {
        return vec4(color.rgb, color[mode - FILT_REDALPHA]);
    }
    return color;
}

bool[8] getTapStates() {
    return bool[8](
        tapCount >= 1,
        tapCount >= 2,
        tapCount >= 3,
        tapCount >= 4,
        tapCount >= 5,
        tapCount >= 6,
        tapCount >= 7,
        tapCount >= 8);
}

vec4 compositeTaps_add(vec4[8] colors, bool[8] states) {
    vec4 color = vec4(0.0);
    for (int i = 0; i < tapCount; i++) {
        if (states[i]) {
            color = color + colors[i];
        }
    }
    return color;
}

vec4 compositeTaps_atop(vec4[8] colors, bool[8] states) {
    vec4 color = vec4(0.0, 0.0, 0.0, 1.0);
    for (int i = 0; i < tapCount; i++) {
        if (states[i]) {
            color = (color.rgba * colors[i].a) + (colors[i].rgba * (1.0 - color.a));
        }
    }
    return color;
}

vec4 compositeTaps_difference(vec4[8] colors, bool[8] states) {
    vec4 color = vec4(0.0, 0.0, 0.0, 1.0);
    for (int i = 0; i < tapCount; i++) {
        if (states[i]) {
            color.rgb = abs(color.rgb - colors[i].rgb);
        }
    }
    return color;
}

vec4 compositeTaps_inside(vec4[8] colors, bool[8] states) {
    vec4 color = vec4(0.0, 0.0, 0.0, 1.0);
    for (int i = 0; i < tapCount; i++) {
        if (states[i]) {
            color = color * clamp(colors[i], 0.0, 1.0);
        }
    }
    return color;
}

vec4 compositeTaps_maximum(vec4[8] colors, bool[8] states) {
    vec4 color = vec4(0.0);
    for (int i = 0; i < tapCount; i++) {
        color = max(color, colors[i]);
    }
    return color;
}

vec4 compositeTaps_minimum(vec4[8] colors, bool[8] states) {
    vec4 color = vec4(1.0);
    for (int i = 0; i < tapCount; i++) {
        if (states[i]) {
            color = min(color, colors[i]);
        }
    }
    return color;
}

vec4 compositeTaps_multiply(vec4[8] colors, bool[8] states) {
    vec4 color = vec4(1.0);
    for (int i = 0; i < tapCount; i++) {
        if (states[i]) {
            color = color * colors[i];
        }
    }
    return color;
}

vec4 compositeTaps_outside(vec4[8] colors, bool[8] states) {
    vec4 color = vec4(0.0, 0.0, 0.0, 1.0);
    for (int i = 0; i < tapCount; i++) {
        if (states[i]) {
            color = color * (1.0 - colors[i].a);
        }
    }
    return color;
}

vec4 compositeTaps_over(vec4[8] colors, bool[8] states) {
    vec4 color = vec4(0.0);
    for (int i = 0; i < tapCount; i++) {
        if (states[i]) {
            color = (colors[i] * (1.0 - color.a)) + color;
        }
    }
    return color;
}

vec4 compositeTaps_screen(vec4[8] colors, bool[8] states) {
    vec4 color = vec4(0.0);
    for (int i = 0; i < tapCount; i++) {
        if (states[i]) {
            color = 1.0 - ((1.0 - color) * (1.0 - colors[i]));
        }
    }
    return color;
}

vec4 compositeTaps_subtract(vec4[8] colors, bool[8] states) {
    vec4 color = vec4(1.0);
    for (int i = 0; i < tapCount; i++) {
        if (states[i]) {
            color = color - colors[i];
        }
    }
    return color;
}

vec4 compositeTaps_under(vec4[8] colors, bool[8] states) {
    vec4 color = vec4(1.0);
    for (int i = 0; i < tapCount; i++) {
        if (states[i]) {
            color = (color * (1.0 - colors[i].a)) + colors[i];
        }
    }
    return color;
}

vec4 compositeTaps(vec4[8] colors, bool[8] states) {
	vec4 color = vec4(0.0);
	switch (stepCompMode) {
	case COMP_ADD:
	    return compositeTaps_add(colors, states);
    case COMP_ATOP:
	    return compositeTaps_atop(colors, states);
    case COMP_AVERAGE:
	    return compositeTaps_add(colors, states) / tapCount;
    case COMP_DIFFERENCE:
	    return compositeTaps_difference(colors, states);
    case COMP_INSIDE:
	    return compositeTaps_inside(colors, states);
    case COMP_MAXIMUM:
	    return compositeTaps_maximum(colors, states);
    case COMP_MINIMUM:
	    return compositeTaps_minimum(colors, states);
    case COMP_MULTIPLY:
	    return compositeTaps_multiply(colors, states);
    case COMP_OUTSIDE:
	    return compositeTaps_outside(colors, states);
    case COMP_OVER:
	    return compositeTaps_over(colors, states);
    case COMP_SCREEN:
	    return compositeTaps_screen(colors, states);
    case COMP_SUBTRACT:
	    return compositeTaps_subtract(colors, states);
    case COMP_UNDER:
	    return compositeTaps_under(colors, states);
	}
    return color;
}

vec4 getTapA(int i);
vec4 getTapB(int i);
vec4 getZeroTap();

vec4[8] getTaps(bool[8] states) {
    vec4[8] colors;
    int[4] filtersA = int[4](tapFilter0, tapFilter1, tapFilter2, tapFilter3);
    int[4] filtersB = int[4](tapFilter4, tapFilter5, tapFilter6, tapFilter7);
    for (int i = 0; i < 4; i++) {
        if (tapCount >= i && states[i]) {
            colors[i] = applyFilter(getTapA(i) * vec4(1.0, 1.0, 1.0, tapAlphaA[i]), filtersA[i]);
        } else {
            colors[i] = vec4(0.0);
        }
    }
    for (int i = 4; i < 8; i++) {
        if (tapCount >= i && states[i]) {
            int j = i - 4;
            colors[i] = applyFilter(getTapB(j) * vec4(1.0, 1.0, 1.0, tapAlphaB[j]), filtersB[j]);
        } else {
            colors[i] = vec4(0.0);
        }
    }
    return colors;
}

out vec4 fragColor;
void main()
{
    if (tapCount > 0) {
        bool[8] states = getTapStates();
        vec4[8] tapColors = getTaps(states);
        fragColor = compositeTaps(tapColors, states);
    } else {
        fragColor = getZeroTap();
    }
}
