// Vertex Shader

uniform int u_Count;
uniform mat4 u_ViewProjectionMatrix;

in vec3 pos;
flat out vec4 v_Color;

void main()
{
    float s = (float(gl_VertexID / 4) / u_Count) * 0.5;
    switch(gl_VertexID % 4)
    {
        // case 0 ignored because of the flat interpolation qualifier of v_Color.
        case 1:
            v_Color = vec4(1.0, s, s, 1.0);
            break;
        case 2:
            v_Color = vec4(s, 1.0, s, 1.0);
            break;
        case 3:
            v_Color = vec4(s, s, 1.0, 1.0);
            break;
    }
    gl_Position = u_ViewProjectionMatrix * vec4(pos, 1.0);
}

// Fragment Shader

flat in vec4 v_Color;
out vec4 fragColor;

void main()
{
    fragColor = v_Color;
}
