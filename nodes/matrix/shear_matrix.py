import bpy
from bpy.props import *
from ... events import executionCodeChanged
from ... base_types.node import AnimationNode

planeItems = [("XY", "XY", ""), ("XZ", "XZ", ""), ("YZ", "YZ", "")]
other = {"XY": "z", "XZ": "y", "YZ": "x"}
coord = {"XY": "(0, 0, 1)", "XZ": "(0, 1, 0)", "YZ": "(1, 0, 0)"}

class ShearMatrixNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ShearMatrixNode"
    bl_label = "Shear Matrix"

    plane = EnumProperty(items = planeItems, update = executionCodeChanged)
    useThirdAsScale = BoolProperty(name = "Use Third as Scale", default = True, 
                    description = "Use Third Coordinate as Scale, if not, only use the 2 shear coordinates", 
                    update = executionCodeChanged)

    def create(self):
        self.inputs.new("an_VectorSocket", "Shear", "shear").value = [1, 1, 1]
        self.outputs.new("an_MatrixSocket", "Matrix", "matrix")

    def draw(self, layout):
        layout.prop(self, "plane", expand = True)
        layout.prop(self, "useThirdAsScale", 
                    text = "Use {} as Scale".format(other[self.plane].upper()) )

    def getExecutionCode(self):

        if self.useThirdAsScale:
            yield ("sca = mathutils.Matrix.Scale(shear.{}, 4, {})"
                .format(other[self.plane], coord[self.plane]) )
            yield ("mat = mathutils.Matrix.Shear('{}', 4, (shear.{}, shear.{}))"
                .format(self.plane, self.plane[0].lower(), self.plane[1].lower()) )
            yield "matrix = sca * mat"
        
        else: 
            yield ("matrix = mathutils.Matrix.Shear('{}', 4, (shear.{}, shear.{}))"
                .format(self.plane, self.plane[0].lower(), self.plane[1].lower()) )

    def getUsedModules(self):
        return ["mathutils"]
