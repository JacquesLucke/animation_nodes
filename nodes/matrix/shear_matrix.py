import bpy
from bpy.props import *
from ... tree_info import keepNodeState
from ... base_types import AnimationNode

planeItems = [
    ("XY", "XY", "", "NONE", 0),
    ("XZ", "XZ", "", "NONE", 1),
    ("YZ", "YZ", "", "NONE", 2)]

class ShearMatrixNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ShearMatrixNode"
    bl_label = "Shear Matrix"

    def planeChanged(self, context):
        self.recreateInputs()

    plane = EnumProperty(items = planeItems, update = planeChanged)

    def create(self):
        self.recreateInputs()
        self.newOutput("Matrix", "Matrix", "matrix")

    @keepNodeState
    def recreateInputs(self):
        self.inputs.clear()
        if self.plane == "XY":
            self.newInput("Float", "Angle X", "angleA")
            self.newInput("Float", "Angle Y", "angleB")
        elif self.plane == "XZ":
            self.newInput("Float", "Angle X", "angleA")
            self.newInput("Float", "Angle Z", "angleB")
        elif self.plane == "YZ":
            self.newInput("Float", "Angle Y", "angleA")
            self.newInput("Float", "Angle Z", "angleB")

    def draw(self, layout):
        layout.prop(self, "plane", expand = True)

    def getExecutionCode(self):
        yield "limit = math.pi / 2 - 0.00001"
        yield "_angleA = math.tan(min(max(angleA, -limit), limit))"
        yield "_angleB = math.tan(min(max(angleB, -limit), limit))"
        yield "matrix = Matrix.Shear('{}', 4, (_angleA, _angleB))".format(self.plane)

    def getUsedModules(self):
        return ["math"]
