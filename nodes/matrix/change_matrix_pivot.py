import bpy
from bpy.props import *
from ... tree_info import keepNodeState
from ... events import executionCodeChanged
from ... algorithms.rotation import generateDirectionToRotationCode
from ... base_types.node import AnimationNode

pivotTypeItems = [
    ("MATRIX", "Pivot Matrix", "Change Pivot by Matrix like parent", "", 0),
    ("VECTOR", "Pivot Location", "Change Pivot Location", "", 3),
    ("LOC_ROT", "Center and Rotation", "Change Pivot by Center and Custom Rotation", "", 2),
    ("AXES", "Center and Axes Direction", "Change Pivot by Center and Custom Rotation Axes", "", 1) ]

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
        self.outputs.new("an_MatrixSocket", "Transform Matrix", "matrixOut")

    def draw(self, layout):
        layout.prop(self, "pivotType", text = "")

    @keepNodeState
    def generateSockets(self):
        self.inputs.clear()
        self.inputs.new("an_MatrixSocket", "Transform Matrix", "matrix")
        
        type = self.pivotType
        
        if type == "MATRIX":
            self.inputs.new("an_MatrixSocket", "Pivot Matrix (Parent)", "pivotMatrix")
        if type == "VECTOR":
            self.inputs.new("an_VectorSocket", "Pivot Location", "pivot")
        if type == "LOC_ROT":
            self.inputs.new("an_VectorSocket", "Pivot Center", "pivot")
            self.inputs.new("an_EulerSocket", "Rotation", "rotation")
        if type == "AXES":
            self.inputs.new("an_VectorSocket", "X Start (Center)", "start")
            self.inputs.new("an_VectorSocket", "X End", "end").value = [1, 0, 0]
            self.inputs.new("an_VectorSocket", "Z Direction (Normal)", "normal").value = [0, 0, 1]

    def getExecutionCode(self):
        type = self.pivotType

        if type == "VECTOR":
            yield "pivotMatrix = mathutils.Matrix.Translation(pivot) "
        if type == "LOC_ROT":
            yield "pivotMatrix = mathutils.Matrix.Translation(pivot) * rotation.to_matrix().to_4x4() "
        if type == "AXES":
            yield "guide = end - start"
            yield from generateDirectionToRotationCode("normal", "guide", "Z", "X", 
                                                        matrixOutputName = "rotMat")
            yield "pivotMatrix = mathutils.Matrix.Translation(start) * rotMat"
        
        yield "matrixOut = pivotMatrix * matrix * pivotMatrix.inverted()"
        
    def getUsedModules(self):
        return ["mathutils"]




