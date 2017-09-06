import bpy
from ... base_types import AnimationNode
from . c_utils import transformPolygons

class TransformPolygonsNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_TransformPolygonsNode"
    bl_label = "Transform Polygons"
    errorHandlingType = "EXCEPTION"

    def create(self):
        self.newInput("Vector List", "Vertices", "vertices", dataIsModified = True)
        self.newInput("Polygon Indices List", "Polygon Indices", "polygonIndices")
        self.newInput("Matrix List", "Matrices", "matrices")

        self.newOutput("Vector List", "Vertices", "vertices")
        self.newOutput("Polygon Indices List", "Polygon Indices", "polygonIndices")

    def execute(self, vertices, polygons, matrices):
        if len(polygons) != 0 and polygons.getMaxIndex() >= len(vertices):
            self.raiseErrorMessage("Invalid polygon indices")
        if len(polygons) != len(matrices):
            self.raiseErrorMessage("Different amount of polygons and matrices")

        transformPolygons(vertices, polygons, matrices)
        return vertices, polygons
