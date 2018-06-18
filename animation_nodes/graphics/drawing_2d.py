import blf
from bgl import *

dpi = 72

def setTextDrawingDpi(new_dpi):
    global dpi
    dpi = new_dpi

def drawHorizontalLine(x, y, length, color = None, thickness = None):
    drawLine(x, y, x + length, y, color, thickness)

def drawVerticalLine(x, y, length, color = None, thickness = None):
    drawLine(x, y, x, y + length, color, thickness)

def drawLine(x1, y1, x2, y2, color = None, thickness = None):
    if thickness: glLineWidth(thickness)
    if color: glColor4f(*color)
    glEnable(GL_BLEND)
    glBegin(GL_LINES)
    glVertex2f(x1, y1)
    glVertex2f(x2, y2)
    glEnd()
    if thickness: glLineWidth(1)

def drawText(text, x, y, font = 0, align = "LEFT", verticalAlignment = "BASELINE", size = 12, color = (1, 1, 1, 1)):
    text = str(text)
    blf.size(font, size, int(dpi))
    #glColor4f(*color)

    if align == "LEFT" and verticalAlignment == "BASELINE":
        blf.position(font, x, y, 0)
    else:
        width, height = blf.dimensions(font, text)
        newX, newY = x, y
        if align == "RIGHT": newX -= width
        elif align == "CENTER": newX -= width / 2
        if verticalAlignment == "CENTER": newY -= blf.dimensions(font, "x")[1] * 0.75

        blf.position(font, newX, newY, 0)

    glUseProgram(program)
    blf.draw(font, text)

vertexShaderCode = """
    #version 330 core

    in vec3 position;
    uniform mat4 u_Model;
    uniform mat4 u_ViewProjection;

    void main() {
        gl_Position = u_ViewProjection * u_Model * vec4(position, 1.0);
    }
"""

fragmentShaderCode = """
    #version 330 core

    out vec4 color;
    uniform vec4 u_Color;

    void main() {
        color = u_Color;
        color = vec4(1, 0, 0, 1);
    }
"""


def compileShader(shader_type, code):
    shader_id = glCreateShader(shader_type)
    glShaderSource(shader_id, code)
    glCompileShader(shader_id)

    success = Buffer(GL_INT, 1)
    glGetShaderiv(shader_id, GL_COMPILE_STATUS, success)

    if success[0] == GL_FALSE:
        info = Buffer(GL_BYTE, 1000)
        length = Buffer(GL_INT, 1)
        glGetShaderInfoLog(shader_id, 999, length, info)
        message = "".join([chr(c) for c in info if c != 0])
        raise Exception(message)

    return shader_id

vertexShader = compileShader(GL_VERTEX_SHADER, vertexShaderCode)
fragmentShader = compileShader(GL_FRAGMENT_SHADER, fragmentShaderCode)

program = glCreateProgram()
glAttachShader(program, vertexShader)
glAttachShader(program, fragmentShader)
glLinkProgram(program)
glValidateProgram(program)


def drawPolygon(vertices, color):
    glColor4f(*color)
    glEnable(GL_BLEND)
    glBegin(GL_POLYGON)
    for x, y in vertices:
        glVertex2f(x, y)
    glEnd()
    glDisable(GL_BLEND)
