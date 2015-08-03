import bpy
from ... base_types.node import AnimationNode
from ... events import executionCodeChanged

axisItems = [("X", "X", ""), ("Y", "Y", ""), ("Z", "Z", "")]

class RotationMatrix(bpy.types.Node, AnimationNode):
    bl_idname = "an_RotationMatrix"
    bl_label = "Rotation Matrix"
    isDetermined = True

    inputNames = { "Angle" : "angle" }
    outputNames = { "Matrix" : "matrix" }

    axis = bpy.props.EnumProperty(items = axisItems, update = executionCodeChanged)

    def create(self):
        self.inputs.new("an_FloatSocket", "Angle")
        self.outputs.new("an_MatrixSocket", "Matrix")

    def draw_buttons(self, context, layout):
        layout.prop(self, "axis", expand = True)

    def getExecutionCode(self, outputUse):
        return "$matrix$ = mathutils.Matrix.Rotation(%angle%, 4, '"+ self.axis +"')"

    def getModuleList(self):
        return ["mathutils"]

    def duplicate(self, sourceNode):
        self.inputs[0].value = 0
