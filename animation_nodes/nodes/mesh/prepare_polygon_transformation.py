import bpy
from ... base_types import AnimationNode
from . c_utils import transformPolygons, separatePolygons, extractPolygonTransforms

class PreparePolygonTransformationNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_PreparePolygonTransformationNode"
    bl_label = "Prepare Polygon Transformation"
    errorHandlingType = "EXCEPTION"

    def create(self):
        self.newInput("Vector List", "Vertices", "inVertices")
        self.newInput("Polygon Indices List", "Polygon Indices", "inPolygonIndices")

        self.newOutput("Vector List", "Vertices", "outVertices")
        self.newOutput("Polygon Indices List", "Polygon Indices", "outPolygonIndices")
        self.newOutput("Matrix List", "Transformations")

    def execute(self, oldVertices, oldPolygonIndices):
        if len(oldPolygonIndices) != 0 and oldPolygonIndices.getMaxIndex() >= len(oldVertices):
            self.raiseErrorMessage("Invalid polygon indices")

        newVertices, newPolygons = separatePolygons(oldVertices, oldPolygonIndices)
        transforms, invertedTransforms = extractPolygonTransforms(newVertices, newPolygons, calcInverted = True)
        transformPolygons(newVertices, newPolygons, invertedTransforms)

        return newVertices, newPolygons, transforms
