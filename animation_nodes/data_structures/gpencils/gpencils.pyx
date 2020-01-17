# cython: profile=True
import textwrap
from .. lists.base_lists cimport DoubleList, Vector3DList

class Layer:
    def __init__(self, layer = None, matrix_world = None):

        if layer is None: layer = None
        if matrix_world is None: matrix_world = None

        self.layer = layer
        self.matrix_world = matrix_world

    def __repr__(self):
        if self.layer is not None:
            return textwrap.dedent("""\
                Layer:
                    {}\
                """.format(self.layer.info))
        return textwrap.dedent("""\
                        Layer:
                            {}\
                        """.format("None"))

    def copy(self):
        return Layer(self.layer, self.matrix_world)

class Stroke:
    def __init__(self, vectors = None, strength = None, pressure = None,
        uv_rotation = None, line_width = None, draw_cyclic = None, start_cap_mode = None,
        end_cap_mode = None, material_index = None, display_mode = None, frame_number = None):

        if vectors is None: vectors = Vector3DList()
        if strength is None: strength = DoubleList()
        if pressure is None: pressure = DoubleList()
        if uv_rotation is None: uv_rotation = DoubleList()
        if line_width is None: line_width = 250
        if draw_cyclic is None: draw_cyclic = False
        if start_cap_mode is None: start_cap_mode = "ROUND"
        if end_cap_mode is None: end_cap_mode = "ROUND"
        if material_index is None: material_index = 0
        if display_mode is None: display_mode = "3DSPACE"
        if frame_number is None: frame_number = 1

        self.vectors = vectors
        self.strength = strength
        self.pressure = pressure
        self.uv_rotation = uv_rotation
        self.line_width = line_width
        self.draw_cyclic = draw_cyclic
        self.start_cap_mode = start_cap_mode
        self.end_cap_mode = end_cap_mode
        self.material_index = material_index
        self.display_mode = display_mode
        self.frame_number = frame_number

    def __repr__(self):
        return textwrap.dedent("""\
            Stroke:
                Points: {}
                Material Index: {}
                Display Mode: {}\
            """.format(len(self.vectors), self.material_index, self.display_mode))

    def copy(self):
        return Stroke(self.vectors, self.strength, self.pressure, self.uv_rotation,
        self.line_width, self.draw_cyclic, self.start_cap_mode, self.end_cap_mode,
        self.material_index, self.display_mode, self.frame_number)
