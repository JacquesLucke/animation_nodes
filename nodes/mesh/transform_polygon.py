import bpy
from bpy.props import *
from ... events import executionCodeChanged
from ... base_types.node import AnimationNode

class TransformPolygonNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_TransformPolygonNode"
    bl_label = "Transform Polygon"

    useCenter = BoolProperty(name = "Use Center", default = True,
        description = "Use the polygon center as origin", update = executionCodeChanged)

    def create(self):
        self.inputs.new("an_PolygonSocket", "Polygon", "polygon").dataIsModified = True
        self.inputs.new("an_MatrixSocket", "Matrix", "matrix")
        self.outputs.new("an_PolygonSocket", "Polygon", "polygon")

    def draw(self, layout):
        layout.prop(self, "useCenter")

    def getExecutionCode(self):
        matrixName = "matrix"
        if self.useCenter:
            yield "offsetMatrix = mathutils.Matrix.Translation(polygon.center)"
            yield "transformMatrix = offsetMatrix * matrix * offsetMatrix.inverted()"
            matrixName = "transformMatrix"

        yield "polygon.vertices = [{} * vertex for vertex in polygon.vertices]".format(matrixName)

    def getUsedModules(self):
        return ["mathutils"]
