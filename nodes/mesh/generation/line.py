import bpy
from .... base_types.node import AnimationNode

class LineMeshNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_LineMeshNode"
    bl_label = "Line Mesh"

    def create(self):
        self.newInput("Vector", "Start", "start")
        self.newInput("Vector", "End", "end", value = [0, 0, 10])
        self.newInput("Integer", "Steps", "steps", value = 2, minValue = 2)
        self.newOutput("Vector List", "Vertices", "vertices")
        self.newOutput("Edge Indices List", "Edge Indices", "edgeIndices")

    def execute(self, start, end, steps):
        steps = max(steps, 2)
        divisor = steps - 1
        vertices = [start * (1 - i / divisor) + end * i / divisor for i in range(steps)]
        edges = [(i, i + 1) for i in range(steps - 1)]
        return vertices, edges
