import bpy
from ... base_types import AnimationNode
from . c_utils import extractPolygonTransforms

class ExtractPolygonTransformsNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ExtractPolygonTransformsNode"
    bl_label = "Extract Polygon Transforms"
    errorHandlingType = "EXCEPTION"

    def create(self):
        self.newInput("Vector List", "Vertices", "vertices")
        self.newInput("Polygon Indices List", "Polygon Indices", "polygonIndices")

        self.newOutput("Matrix List", "Transforms", "transforms")
        self.newOutput("Matrix List", "Inverted Transforms", "invertedTransforms")

    def execute(self, vertices, polygons):
        if len(polygons) == 0 or polygons.getMaxIndex() < len(vertices):
            return extractPolygonTransforms(vertices, polygons, calcInverted = True)
        else:
            self.raiseErrorMessage("Invalid polygon indices")
