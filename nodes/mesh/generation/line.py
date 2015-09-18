import bpy
from .... base_types.node import AnimationNode

class LineMeshNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_LineMeshNode"
    bl_label = "Line Mesh"

    def create(self):
        self.inputs.new("an_VectorSocket", "Start", "start")
        self.inputs.new("an_VectorSocket", "End", "end").value = (0, 0, 10)
        self.inputs.new("an_IntegerSocket", "Steps", "steps").value = 2
        self.outputs.new("an_VectorListSocket", "Vertices", "vertices")
        self.outputs.new("an_EdgeIndicesListSocket", "Edge Indices", "edgeIndices")

    def execute(self, start, end, steps):
        divisor = steps - 1
        vertices = [start * (1 - i / divisor) + end * i / divisor for i in range(steps)]
        edges = [(i, i + 1) for i in range(steps - 1)]
        return vertices, edges
