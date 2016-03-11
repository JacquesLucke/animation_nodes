import blf
from bgl import *

dpi = 72

def set_text_drawing_dpi(new_dpi):
    global dpi
    dpi = new_dpi

def draw_horizontal_line(x, y, length, color, width):
    draw_line(x, y, x + length, y, color, width)

def draw_vertical_line(x, y, length, color, width):
    draw_line(x, y, x, y + length, color, width)

def draw_line(x1, y1, x2, y2, color, width):
    glLineWidth(width)
    glColor4f(*color)
    glEnable(GL_BLEND)
    glBegin(GL_LINES)
    glVertex2f(x1, y1)
    glVertex2f(x2, y2)
    glEnd()
    glLineWidth(1)

def draw_boolean(state, x, y, size = 12, alpha = 1):
    if state:
        draw_text("ON", x, y, align = "LEFT", size = size,
                  color = (0.8, 1, 0.8, alpha))
    else:
        draw_text("OFF", x, y, align = "LEFT", size = size,
                  color = (1, 0.8, 0.8, alpha))

def draw_text(text, x, y, align = "LEFT", size = 12, color = (1, 1, 1, 1)):
    font = 0
    blf.size(font, size, int(dpi))
    glColor4f(*color)

    if align == "LEFT":
        blf.position(font, x, y, 0)
    else:
        width, height = blf.dimensions(font, text)
        if align == "RIGHT":
            blf.position(font, x - width, y, 0)

    blf.draw(font, text)
