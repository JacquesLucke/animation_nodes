void main() {
  float s = (float(gl_VertexID / 4) / u_Count) * 0.5;
  switch (gl_VertexID % 4) {
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
  gl_Position = u_ViewProjectionMatrix * vec4(position, 1.0);
}
