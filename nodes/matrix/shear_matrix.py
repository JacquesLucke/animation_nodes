import bpy
from bpy.props import *
from ... events import executionCodeChanged
from ... base_types.node import AnimationNode

planeItems = [("XY", "XY", ""), ("XZ", "XZ", ""), ("YZ", "YZ", "")]
thirdAxisName = {"XY": "z", "XZ": "y", "YZ": "x"}
thirdAxisTuple = {"XY": "(0, 0, 1)", "XZ": "(0, 1, 0)", "YZ": "(1, 0, 0)"}

class ShearMatrixNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ShearMatrixNode"
    bl_label = "Shear Matrix"

    plane = EnumProperty(items = planeItems, update = executionCodeChanged)
    useThirdAsScale = BoolProperty(name = "Use Third as Scale", default = True,
                    description = "Use Third Coordinate as Scale, if not, only use the 2 shear coordinates",
                    update = executionCodeChanged)

    def create(self):
        self.newInput("Vector", "Shear", "shear", value = [1, 1, 1])
        self.newOutput("Matrix", "Matrix", "matrix")

    def draw(self, layout):
        layout.prop(self, "plane", expand = True)
        layout.prop(self, "useThirdAsScale",
                    text = "Use {} as Scale".format(thirdAxisName[self.plane].upper()) )

    def getExecutionCode(self):
        plane = self.plane

        if self.useThirdAsScale:
            yield ("_scale = Matrix.Scale(shear.{}, 4, {})"
                                .format(thirdAxisName[plane], thirdAxisTuple[plane]) )
            yield ("_matrix = Matrix.Shear('{}', 4, (shear.{}, shear.{}))"
                                .format(plane, plane[0].lower(), plane[1].lower()) )
            yield "matrix = _scale * _matrix"

        else:
            yield ("matrix = Matrix.Shear('{}', 4, (shear.{}, shear.{}))"
                                .format(plane, plane[0].lower(), plane[1].lower()) )
