import bpy
from ... base_types.node import AnimationNode

class mn_EdgesOfPolygons(bpy.types.Node, AnimationNode):
    bl_idname = "mn_EdgesOfPolygons"
    bl_label = "Edges of Polygons"

    inputNames = { "Polygons" : "polygons" }
    outputNames = { "Edges" : "Edges" }

    def create(self):
        self.inputs.new("mn_PolygonIndicesListSocket", "Polygons")
        self.outputs.new("mn_EdgeIndicesListSocket", "Edges")

    def execute(self, polygons):
        edges = []
        for polygon in polygons:
            for i, index in enumerate(polygon):
                startIndex = polygon[i - 1]
                edge = (startIndex, index) if index > startIndex else (index, startIndex)
                edges.append(edge)
        return list(set(edges))
