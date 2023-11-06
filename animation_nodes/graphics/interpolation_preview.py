import gpu
import numpy
from . rectangle import Rectangle
from gpu_extras.batch import batch_for_shader

class InterpolationPreview:
    def __init__(self, interpolation, position, width, resolution):
        self.interpolation = interpolation
        self.position = position
        self.width = width
        self.normalHeight = width
        self.resolution = resolution
        self.padding = 5

        self.boundary = Rectangle()
        self.samples = interpolation.sample(amount = resolution)

    def calculateBoundaries(self):
        minSample = self.samples.getMinValue()
        maxSample = self.samples.getMaxValue()

        bottomOvershoot = abs(min(0, minSample) * self.normalHeight)
        topOvershoot = abs(max(0, maxSample - 1) * self.normalHeight)

        x1 = self.position.x
        x2 = x1 + self.width
        y1 = self.position.y
        y2 = y1 - self.normalHeight - bottomOvershoot - topOvershoot

        self.boundary.resetPosition(x1, y1, x2, y2)

        self.interpolationLeft = x1
        self.interpolationRight = x2
        self.interpolationTop = y1 - topOvershoot - self.padding
        self.interpolationBottom = y2 + bottomOvershoot + self.padding

    def getHeight(self):
        return self.boundary.height

    def draw(self, backgroundColor = (0.9, 0.9, 0.9, 0.6),
                   borderColor = (0.9, 0.76, 0.4, 1.0),
                   borderThickness = -1):
        self.boundary.draw(
            color = backgroundColor,
            borderColor = borderColor,
            borderThickness = borderThickness
        )
        self.drawInterpolationCurve()
        self.drawRangeLines()

    def drawInterpolationCurve(self):
        left, right = self.interpolationLeft, self.interpolationRight
        top, bottom = self.interpolationTop, self.interpolationBottom
        x = numpy.linspace(left, right, self.resolution)
        y = top + (self.samples.asNumpyArray() - 1) * (top - bottom)
        points = numpy.stack((x, y), axis = -1).astype(numpy.float32)
        shader = gpu.shader.from_builtin('UNIFORM_COLOR')
        batch = batch_for_shader(shader, 'LINE_STRIP', {"pos": points})

        shader.bind()
        shader.uniform_float("color", (0.2, 0.2, 0.2, 0.8))

        gpu.state.line_width_set(2)
        gpu.state.blend_set("ALPHA")
        batch.draw(shader)
        gpu.state.blend_set("NONE")
        gpu.state.line_width_set(1)

    def drawRangeLines(self):
        points = (
            (self.boundary.left, self.interpolationTop),
            (self.boundary.right, self.interpolationTop),
            (self.boundary.left, self.interpolationBottom),
            (self.boundary.right, self.interpolationBottom))
        shader = gpu.shader.from_builtin('UNIFORM_COLOR')
        batch = batch_for_shader(shader, 'LINES', {"pos": points})

        shader.bind()
        shader.uniform_float("color", (0.2, 0.2, 0.2, 0.5))

        gpu.state.line_width_set(1)
        gpu.state.blend_set("ALPHA")
        batch.draw(shader)
        gpu.state.blend_set("NONE")
