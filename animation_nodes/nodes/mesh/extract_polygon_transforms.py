import bpy
from bpy.props import *
from ... base_types import AnimationNode
from . c_utils import extractPolygonTransforms
from .. matrix.c_utils import getInvertedOrthogonalMatrices

sourceTypeItems = [
    ("MESH", "Mesh", "", "NONE", 0),
    ("VERTICES_AND_POLYGONS", "Vertices and Polygons", "", "NONE", 1)
]

class ExtractPolygonTransformsNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ExtractPolygonTransformsNode"
    bl_label = "Extract Polygon Transforms"
    errorHandlingType = "EXCEPTION"

    sourceType = EnumProperty(name = "Source Type", default = "MESH",
        update = AnimationNode.refresh, items = sourceTypeItems)

    def create(self):
        if self.sourceType == "MESH":
            self.newInput("Mesh", "Mesh", "mesh")
        elif self.sourceType == "VERTICES_AND_POLYGONS":
            self.newInput("Vector List", "Vertices", "vertices")
            self.newInput("Polygon Indices List", "Polygon Indices", "polygonIndices")

        self.newOutput("Matrix List", "Transforms", "transforms")
        self.newOutput("Matrix List", "Inverted Transforms", "invertedTransforms", hide = True)

    def drawAdvanced(self, layout):
        layout.prop(self, "sourceType", text = "Source")

    def getExecutionCode(self, required):
        if self.sourceType == "MESH":
            yield "transforms = self.getTransforms(mesh.vertices, mesh.polygons)"
        elif self.sourceType == "VERTICES_AND_POLYGONS":
            yield "self.validateMeshData(vertices, polygonIndices)"
            yield "transforms = self.getTransforms(vertices, polygonIndices)"

        if "invertedTransforms" in required:
            yield "invertedTransforms = self.invertTransforms(transforms)"

    def validateMeshData(self, vertices, polygons):
        if len(polygons) > 0 and polygons.getMaxIndex() >= len(vertices):
            self.raiseErrorMessage("Invalid polygon indices")

    def getTransforms(self, vertices, polygons):
        return extractPolygonTransforms(vertices, polygons, calcInverted = False)

    def invertTransforms(self, transforms):
        return getInvertedOrthogonalMatrices(transforms)