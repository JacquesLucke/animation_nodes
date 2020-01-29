# cython: profile=True
import textwrap
from .. lists.base_lists cimport DoubleList, Vector3DList

class Layer:
    def __init__(self, layerName = None,
                       frames = None,
                       frameNumbers = None,
                       blendMode = None,
                       opacity = None,
                       passIndex = None):

        if layerName is None: layerName = "AN-Layer"
        if frames is None: frames = []
        if frameNumbers is None: frameNumbers = DoubleList()
        if blendMode is None: blendMode = "REGULAR"
        if opacity is None: opacity = 1
        if passIndex is None: passIndex = 0

        self.frames = frames
        self.layerName = layerName
        self.frameNumbers = frameNumbers
        self.blendMode = blendMode
        self.opacity = opacity
        self.passIndex = passIndex

    def __repr__(self):
        return textwrap.dedent(
        f"""AN Layer Object:
        Layer Name: {self.layerName}
        Frames: {len(self.frames)}
        Frame Numbers: {self.frameNumbers}
        Blend Mode: {self.blendMode}
        Opacity: {self.opacity}
        Pass Index: {self.passIndex}""")

    def copy(self):
        return Layer(self.layerName, self.frames, self.frameNumbers, self.blendMode, self.opacity, self.passIndex)

class Frame:
    def __init__(self, strokes = None, frameIndex = None, frameNumber = None):

        if strokes is None: strokes = []
        if frameIndex is None: frameIndex = 0
        if frameNumber is None: frameNumber = 0

        self.strokes = strokes
        self.frameIndex = frameIndex
        self.frameNumber = frameNumber

    def __repr__(self):
        return textwrap.dedent(
        f"""AN Frame Object:
        Strokes: {len(self.strokes)}
        Frame Index: {self.frameIndex}
        Frame Number: {self.frameNumber}""")

    def copy(self):
        return Frame(self.strokes, self.frameIndex, self.frameNumber)

class Stroke:
    def __init__(self, vertices = None, strength = None, pressure = None,
        uv_rotation = None, line_width = None, draw_cyclic = None, start_cap_mode = None,
        end_cap_mode = None, material_index = None, display_mode = None):

        if vertices is None: vertices = Vector3DList()
        if strength is None: strength = DoubleList()
        if pressure is None: pressure = DoubleList()
        if uv_rotation is None: uv_rotation = DoubleList()
        if line_width is None: line_width = 250
        if draw_cyclic is None: draw_cyclic = False
        if start_cap_mode is None: start_cap_mode = "ROUND"
        if end_cap_mode is None: end_cap_mode = "ROUND"
        if material_index is None: material_index = 0
        if display_mode is None: display_mode = "SCREEN"

        self.vertices = vertices
        self.strength = strength
        self.pressure = pressure
        self.uv_rotation = uv_rotation
        self.line_width = line_width
        self.draw_cyclic = draw_cyclic
        self.start_cap_mode = start_cap_mode
        self.end_cap_mode = end_cap_mode
        self.material_index = material_index
        self.display_mode = display_mode

    def __repr__(self):
        return textwrap.dedent(
            f"""AN Stroke Object:
            Points: {len(self.vertices)}
            Material Index: {self.material_index}
            Display Mode: {self.display_mode}""")

    def copy(self):
        return Stroke(self.vertices, self.strength, self.pressure, self.uv_rotation,
        self.line_width, self.draw_cyclic, self.start_cap_mode, self.end_cap_mode,
        self.material_index, self.display_mode)
