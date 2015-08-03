import bpy
from ... base_types.node import AnimationNode

class TransformVector(bpy.types.Node, AnimationNode):
    bl_idname = "an_TransformVector"
    bl_label = "Transform Vector"
    isDetermined = True

    inputNames = { "Vector" : "vector",
                   "Matrix" : "matrix" }

    outputNames = { "Vector" : "vector" }

    def create(self):
        self.inputs.new("an_VectorSocket", "Vector")
        self.inputs.new("an_MatrixSocket", "Matrix")
        self.outputs.new("an_VectorSocket", "Vector")

    def getExecutionCode(self):
        return "$vector$ = %matrix% * mathutils.Vector(%vector%)"
        
    def getModuleList(self):
        return ["mathutils"]
