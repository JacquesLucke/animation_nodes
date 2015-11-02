import bpy
from ... base_types.node import AnimationNode

class VectorAngle2DNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_VectorAngle2DNode"
    bl_label = "Vector 2D Angle"

    def create(self):
        self.inputs.new("an_VectorSocket", "A", "a")
        self.inputs.new("an_VectorSocket", "B", "b")
        self.inputs.new("an_MatrixSocket", "Matrix XY 2D Plane", "matrix")
        self.outputs.new("an_FloatSocket", "Angle", "angle")
                
    def getExecutionCode(self):
        return "angle = ((matrix.inverted() * a).to_2d()).angle_signed((matrix.inverted() * b).to_2d(), 0)"
