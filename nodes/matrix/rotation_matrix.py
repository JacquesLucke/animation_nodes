import bpy
from bpy.props import *
from ... base_types.node import AnimationNode
from ... events import executionCodeChanged

axisItems = [("X", "X", ""), ("Y", "Y", ""), ("Z", "Z", "")]

class RotationMatrix(bpy.types.Node, AnimationNode):
    bl_idname = "an_RotationMatrix"
    bl_label = "Rotation Matrix"
    isDetermined = True

    axis = EnumProperty(items = axisItems, update = executionCodeChanged)

    def create(self):
        self.inputs.new("an_FloatSocket", "Angle", "angle")
        self.outputs.new("an_MatrixSocket", "Matrix", "matrix")

    def draw(self, layout):
        layout.prop(self, "axis", expand = True)

    def getExecutionCode(self, outputUse):
        return "matrix = mathutils.Matrix.Rotation(angle, 4, '{}')".format(self.axis)

    def getModuleList(self):
        return ["mathutils"]

    def duplicate(self, sourceNode):
        self.inputs[0].value = 0
