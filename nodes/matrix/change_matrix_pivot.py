import bpy
from bpy.props import *
from ... tree_info import keepNodeState
from ... base_types.node import AnimationNode
from ... algorithms.rotation import generateRotationMatrix

pivotTypeItems = [
    ("MATRIX", "Pivot Matrix", "Change Pivot by Matrix like parent", "", 0),
    ("VECTOR", "Pivot Location", "Change Pivot Location", "", 1),
    ("LOC_ROT", "Center and Rotation", "Change Pivot by Center and Custom Rotation", "", 2),
    ("AXES_XXZ", "X Line, Z Direction", "Change Pivot by Center and Custom Rotation Axes", "", 3),
    ("AXES_XXZZ", "X Line, Z Line", "Change Pivot by Center and Custom Rotation Axes", "", 4) ]

class ChangeMatrixPivotNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ChangeMatrixPivotNode"
    bl_label = "Change Matrix Pivot"

    def pivotTypeChanged(self, context):
        self.generateSockets()

    pivotType = EnumProperty(name = "Input Type", default = "MATRIX",
        items = pivotTypeItems, update = pivotTypeChanged)

    def create(self):
        self.width = 150
        self.generateSockets()
        self.newOutput("Matrix", "Transform Matrix", "matrixOut")

    def draw(self, layout):
        layout.prop(self, "pivotType", text = "")

    @keepNodeState
    def generateSockets(self):
        self.inputs.clear()
        self.newInput("Matrix", "Transform Matrix", "matrix")

        type = self.pivotType

        if type == "MATRIX":
            self.newInput("Matrix", "Pivot Matrix (Parent)", "pivotMatrix")
        if type == "VECTOR":
            self.newInput("Vector", "Pivot Location", "pivot")
        if type == "LOC_ROT":
            self.newInput("Vector", "Pivot Center", "pivot")
            self.newInput("Euler", "Rotation", "rotation")

        if type == "AXES_XXZ":
            self.newInput("Vector", "X Start (Center)", "start")
            self.newInput("Vector", "X End", "end").value = [1, 0, 0]
            self.newInput("Vector", "Z Direction (Normal)", "normal").value = [0, 0, 1]

        if type == "AXES_XXZZ":
            self.newInput("Vector", "X Start (Center)", "startX")
            self.newInput("Vector", "X End", "endX").value = [1, 0, 0]
            self.newInput("Vector", "Z Start", "startZ")
            self.newInput("Vector", "Z End", "endZ").value = [0, 0, 1]

    def getExecutionCode(self):
        type = self.pivotType

        if type == "VECTOR":
            yield "pivotMatrix = Matrix.Translation(pivot) "
        if type == "LOC_ROT":
            yield "pivotMatrix = Matrix.Translation(pivot) * rotation.to_matrix().to_4x4() "

        if type == "AXES_XXZ":
            yield "matrixRotation = animation_nodes.algorithms.rotation.generateRotationMatrix(normal, end - start, 'Z', 'X')"
            yield "pivotMatrix = Matrix.Translation(start) * matrixRotation.normalized()"

        if type == "AXES_XXZZ":
            yield "matrixRotation = (animation_nodes.algorithms.rotation.generateRotationMatrix(endZ - startZ, endX - startX, 'Z', 'X')).normalized()"
            yield "pivotMatrix = Matrix.Translation(startX) * matrixRotation"

        yield "matrixOut = pivotMatrix * matrix * pivotMatrix.inverted()"
