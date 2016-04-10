import bpy
from ... base_types.node import AnimationNode
from ... data_structures.splines.poly_spline import PolySpline

class SplinesFromEdgesNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_SplinesFromEdgesNode"
    bl_label = "Splines from Edges"

    def create(self):
        self.newInput("an_VectorListSocket", "Vertices", "vertices").dataIsModified = True
        self.newInput("an_EdgeIndicesListSocket", "Edge Indices", "edgeIndices")
        self.newOutput("an_SplineListSocket", "Splines", "splines")

    def execute(self, vertices, edgeIndices):
        splines = []
        for index1, index2 in edgeIndices:
            spline = PolySpline.fromLocations([vertices[index1], vertices[index2]])
            splines.append(spline)
        return splines
