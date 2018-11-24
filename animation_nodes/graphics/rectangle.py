import gpu
from bgl import *
from mathutils import Vector
from gpu_extras.batch import batch_for_shader

shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')

class Rectangle:
    def __init__(self, x1 = 0, y1 = 0, x2 = 0, y2 = 0):
        self.resetPosition(x1, y1, x2, y2)

    @classmethod
    def fromRegionDimensions(cls, region):
        return cls(0, 0, region.width, region.height)

    def resetPosition(self, x1 = 0, y1 = 0, x2 = 0, y2 = 0):
        self.x1 = float(x1)
        self.y1 =  float(y1)
        self.x2 =  float(x2)
        self.y2 =  float(y2)

    def copy(self):
        return Rectangle(self.x1, self.y1, self.x2, self.y2)

    @property
    def width(self):
        return abs(self.x1 - self.x2)

    @property
    def height(self):
        return abs(self.y1 - self.y2)

    @property
    def left(self):
        return min(self.x1, self.x2)

    @property
    def right(self):
        return max(self.x1, self.x2)

    @property
    def top(self):
        return max(self.y1, self.y2)

    @property
    def bottom(self):
        return min(self.y1, self.y2)

    @property
    def center(self):
        return Vector((self.centerX, self.centerY))

    @property
    def centerX(self):
        return (self.x1 + self.x2) / 2

    @property
    def centerY(self):
        return (self.y1 + self.y2) / 2

    def getInsetRectangle(self, amount):
        return Rectangle(self.left + amount, self.top - amount, self.right - amount, self.bottom + amount)

    def contains(self, point):
        return self.left <= point[0] <= self.right and self.bottom <= point[1] <= self.top

    def draw(self, color = (0.8, 0.8, 0.8, 1.0), borderColor = (0.1, 0.1, 0.1, 1.0), borderThickness = 0):
        locations = (
            (self.x1, self.y1),
            (self.x2, self.y1),
            (self.x1, self.y2),
            (self.x2, self.y2))
        batch = batch_for_shader(shader, 'TRI_STRIP', {"pos": locations})

        shader.bind()
        shader.uniform_float("color", color)

        glEnable(GL_BLEND)
        batch.draw(shader)
        glDisable(GL_BLEND)

        if borderThickness == 0: return

        offset = borderThickness // 2
        bWidth = offset * 2 if borderThickness > 0 else 0
        borderLocations = (
            (self.x1 - bWidth, self.y1 + offset), (self.x2 + bWidth, self.y1 + offset),
            (self.x2 + offset, self.y1 + bWidth), (self.x2 + offset, self.y2 - bWidth),
            (self.x2 + bWidth, self.y2 - offset), (self.x1 - bWidth, self.y2 - offset),
            (self.x1 - offset, self.y2 - bWidth), (self.x1 - offset, self.y1 + bWidth))
        batch = batch_for_shader(shader, 'LINES',{"pos": borderLocations})

        shader.bind()
        shader.uniform_float("color", borderColor)

        glEnable(GL_BLEND)
        glLineWidth(abs(borderThickness))
        batch.draw(shader)
        glDisable(GL_BLEND)

    def __repr__(self):
        return "({}, {}) - ({}, {})".format(self.x1, self.y1, self.x2, self.y2)
