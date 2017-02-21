import bpy
from bpy.props import *
from ... base_types import AnimationNode

axisItems = [
    ("X", "X", "", "", 0),
    ("Y", "Y", "", "", 1),
    ("Z", "Z", "", "", 2),
    ("ALL", "All", "", "", 3) ]

class RotationMatrixNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_RotationMatrixNode"
    bl_label = "Rotation Matrix"

    axis = EnumProperty(default = "X", items = axisItems,
        update = AnimationNode.refresh)

    def create(self):
        socketType = "Euler" if self.axis == "ALL" else "Float"
        self.newInput(socketType, "Angle", "angle")
        self.newOutput("Matrix", "Matrix", "matrix")

    def draw(self, layout):
        layout.prop(self, "axis", expand = True)

    def getExecutionCode(self):
        if len(self.axis) == 1:
            return "matrix = Matrix.Rotation(angle, 4, '{}')".format(self.axis)
        else:
            return "matrix = angle.to_matrix(); matrix.resize_4x4()"
