import bpy
from .... base_types.node import AnimationNode
from .... algorithms.mesh_generation.basic_shapes import lineVertices

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
        vertices = lineVertices(start, end, steps)
        edges = [(i, i + 1) for i in range(steps - 1)]
        return vertices, edges
