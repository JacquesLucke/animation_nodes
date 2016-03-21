import bpy
from bpy.props import *
from ... tree_info import keepNodeState
from ... events import executionCodeChanged
from ... base_types.node import AnimationNode

inputTypeItems = [
    ("MATRIX", "Pivot for Matrix", "Change pivot for Matrix operation"),
    ("VECTOR", "Pivot for Vector", "Change pivot for Vector operation"),
    ("ROTATION", "Pivot for Rotation", "Change pivot for Rotation operation"),
    ("MATRIX_LIST", "Pivot for Matrix List", "Change pivot for Matrix list operation"),
    ("VECTOR_LIST", "Pivot for Vector List", "Change pivot for Vector list operation"),
    ("ROTATION_LIST", "Pivot for Rotation List", "Change pivot for Rotation list operation") ]

names = {"MATRIX": "matrix", "VECTOR": "location", "ROTATION": "rotation",
         "MATRIX_LIST": "matrix", "VECTOR_LIST": "location", "ROTATION_LIST": "rotation"}
socketNames = {"MATRIX": "Matrix", "VECTOR": "Vector", "ROTATION": "Euler", 
               "MATRIX_LIST": "Matrix", "VECTOR_LIST": "Vector", "ROTATION_LIST": "Euler"}

class ChangePivotNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ChangePivotNode"
    bl_label = "Change Pivot"

    def inputTypeChanged(self, context):
        self.generateSockets()
        executionCodeChanged()

    inputType = EnumProperty(name = "Input Type", default = "MATRIX",
        items = inputTypeItems, update = inputTypeChanged)

    def create(self):
        self.width = 150
        self.inputType = "MATRIX"

    def draw(self, layout):
        layout.prop(self, "inputType", text = "")

    def getExecutionCode(self):
        type = self.inputType
        condition = "List = [" if "LIST" in type else " = "
        generator = " for {} in {}List]".format(names[type], names[type]) if "LIST" in type else ""
        
        if "MATRIX" in type: yield "matrix{} pivotMatrix * matrix * pivotMatrix.inverted(pivotMatrix){}".format(condition, generator)
        if "VECTOR" in type: yield "location{} pivotMatrix.inverted(pivotMatrix) * (pivotMatrix * location){}".format(condition, generator)
        if "ROTATION" in type: yield "rotation{} ( pivotMatrix * rotation.to_matrix().to_4x4() * pivotMatrix.inverted(pivotMatrix) ).to_euler(){}".format(condition, generator)

    def getUsedModules(self):
        return ["mathutils"]

    @keepNodeState
    def generateSockets(self):
        self.inputs.clear()
        self.outputs.clear()
        
        type = self.inputType
        condition = "List" if "LIST" in type else ""
        name = names[type]
        Name = name.capitalize() + " " + condition
        socket = "an_{}{}Socket".format(socketNames[type], condition)
        
        self.inputs.new("{}".format(socket), "{}".format(Name), "{}".format(name + condition))
        self.inputs.new("an_MatrixSocket", "Pivot Matrix", "pivotMatrix")
        self.outputs.new("{}".format(socket), "{}".format(Name), "{}".format(name + condition))
