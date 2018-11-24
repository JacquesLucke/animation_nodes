import gpu
import blf
from bgl import *
from gpu_extras.batch import batch_for_shader

dpi = 72
shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')

def setTextDrawingDpi(new_dpi):
    global dpi
    dpi = new_dpi

def drawHorizontalLine(x, y, length, color = None, thickness = None):
    drawLine(x, y, x + length, y, color, thickness)

def drawVerticalLine(x, y, length, color = None, thickness = None):
    drawLine(x, y, x, y + length, color, thickness)

def drawLine(x1, y1, x2, y2, color = None, thickness = None):
    batch = batch_for_shader(shader, 'LINES', {"pos": ((x1, y1),(x2, y2))})

    shader.bind()
    if color: shader.uniform_float("color", color)

    if thickness: glLineWidth(abs(thickness))
    glEnable(GL_BLEND)
    batch.draw(shader)
    glDisable(GL_BLEND)
    if thickness: glLineWidth(1)

def drawText(text, x, y, font = 0, align = "LEFT", verticalAlignment = "BASELINE", size = 12, color = (1, 1, 1, 1)):
    text = str(text)
    blf.size(font, size, int(dpi))
    blf.color(font, *color)

    if align == "LEFT" and verticalAlignment == "BASELINE":
        blf.position(font, x, y, 0)
    else:
        width, height = blf.dimensions(font, text)
        newX, newY = x, y
        if align == "RIGHT": newX -= width
        elif align == "CENTER": newX -= width / 2
        if verticalAlignment == "CENTER": newY -= blf.dimensions(font, "x")[1] * 0.75

        blf.position(font, newX, newY, 0)

    blf.draw(font, text)

def drawPolygon(vertices, color):
    batch = batch_for_shader(shader, 'TRI_STRIP', {"pos": vertices[:2] + vertices[2:][::-1]})

    shader.bind()
    shader.uniform_float("color", color)

    glEnable(GL_BLEND)
    batch.draw(shader)
    glDisable(GL_BLEND)
