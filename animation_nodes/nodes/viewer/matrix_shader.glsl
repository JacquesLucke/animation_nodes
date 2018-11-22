// Vertex Shader

uniform int count;
uniform mat4 viewProjectionMatrix;

in vec3 pos;
flat out vec4 color;

void main()
{
    float s = (float(gl_VertexID / 4) / count) * 0.5;
    switch(gl_VertexID % 4)
    {
        case 1:
            color = vec4(1, s, s, 1);
            break;
        case 2:
            color = vec4(s, 1, s, 1);
            break;
        case 3:
            color = vec4(s, s, 1, 1);
            break;
    }
    gl_Position = viewProjectionMatrix * vec4(pos, 1);
}

// Fragment Shader

flat in vec4 color;

void main()
{
    gl_FragColor = color;
}
