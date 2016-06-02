import bpy
from bpy.props import *
from ... tree_info import keepNodeState
from ... base_types.node import AnimationNode

pivotTypeItems = [
    ("CENTER", "Center", "Use the center of the polygon as pivot", "NONE", 0),
    ("WORLD_ORIGIN", "World", "Use the (0, 0, 0) vector as pivot for all polygons", "NONE", 1),
    ("CUSTOM", "Custom", "Use a custom vector as pivot", "NONE", 2) ]

class TransformPolygonNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_TransformPolygonNode"
    bl_label = "Transform Polygon"

    def pivotTypeChanged(self, context):
        self.generateSockets()

    pivotType = EnumProperty(name = "Pivot Type", default = "CENTER",
        items = pivotTypeItems, update = pivotTypeChanged)

    def create(self):
        self.generateSockets()
        self.newOutput("Polygon", "Polygon", "polygon")

    def draw(self, layout):
        layout.prop(self, "pivotType", text = "Pivot")

    @keepNodeState
    def generateSockets(self):
        self.inputs.clear()
        self.newInput("Polygon", "Polygon", "polygon").dataIsModified = True
        self.newInput("Matrix", "Matrix", "matrix")

        if self.pivotType == "CUSTOM":
            self.newInput("Vector", "Pivot", "pivot")

    def getExecutionCode(self):
        matrixName = "matrix"

        if self.pivotType in ("CENTER", "CUSTOM"):
            pivotName = "polygon.center" if self.pivotType == "CENTER" else "pivot"
            yield "offsetMatrix = Matrix.Translation({})".format(pivotName)
            yield "transformMatrix = offsetMatrix * matrix * offsetMatrix.inverted()"
            matrixName = "transformMatrix"

        yield "polygon.vertexLocations = [{} * location for location in polygon.vertexLocations]".format(matrixName)
