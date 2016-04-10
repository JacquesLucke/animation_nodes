import bpy
from bpy.props import *
from ... tree_info import keepNodeState
from ... events import executionCodeChanged
from ... algorithms.rotation import generateRotationMatrix
from ... base_types.node import AnimationNode

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
        executionCodeChanged()

    pivotType = EnumProperty(name = "Input Type", default = "MATRIX",
        items = pivotTypeItems, update = pivotTypeChanged)

    def create(self):
        self.width = 150
        self.generateSockets()
        self.newOutput("an_MatrixSocket", "Transform Matrix", "matrixOut")

    def draw(self, layout):
        layout.prop(self, "pivotType", text = "")

    @keepNodeState
    def generateSockets(self):
        self.inputs.clear()
        self.newInput("an_MatrixSocket", "Transform Matrix", "matrix")
        
        type = self.pivotType
        
        if type == "MATRIX":
            self.newInput("an_MatrixSocket", "Pivot Matrix (Parent)", "pivotMatrix")
        if type == "VECTOR":
            self.newInput("an_VectorSocket", "Pivot Location", "pivot")
        if type == "LOC_ROT":
            self.newInput("an_VectorSocket", "Pivot Center", "pivot")
            self.newInput("an_EulerSocket", "Rotation", "rotation")

        if type == "AXES_XXZ":
            self.newInput("an_VectorSocket", "X Start (Center)", "start")
            self.newInput("an_VectorSocket", "X End", "end").value = [1, 0, 0]
            self.newInput("an_VectorSocket", "Z Direction (Normal)", "normal").value = [0, 0, 1]

        if type == "AXES_XXZZ":
            self.newInput("an_VectorSocket", "X Start (Center)", "startX")
            self.newInput("an_VectorSocket", "X End", "endX").value = [1, 0, 0]
            self.newInput("an_VectorSocket", "Z Start", "startZ")
            self.newInput("an_VectorSocket", "Z End", "endZ").value = [0, 0, 1]

    def getExecutionCode(self):
        type = self.pivotType

        if type == "VECTOR":
            yield "pivotMatrix = mathutils.Matrix.Translation(pivot) "
        if type == "LOC_ROT":
            yield "pivotMatrix = mathutils.Matrix.Translation(pivot) * rotation.to_matrix().to_4x4() "

        if type == "AXES_XXZ":
            yield "matrixRotation = animation_nodes.algorithms.rotation.generateRotationMatrix(normal, end - start, 'Z', 'X')"
            yield "pivotMatrix = mathutils.Matrix.Translation(start) * matrixRotation.normalized()"

        if type == "AXES_XXZZ":
            yield "matrixRotation = (animation_nodes.algorithms.rotation.generateRotationMatrix(endZ - startZ, endX - startX, 'Z', 'X')).normalized()"
            yield "pivotMatrix = mathutils.Matrix.Translation(startX) * matrixRotation"

        yield "matrixOut = pivotMatrix * matrix * pivotMatrix.inverted()"
        
    def getUsedModules(self):
        return ["mathutils"]
