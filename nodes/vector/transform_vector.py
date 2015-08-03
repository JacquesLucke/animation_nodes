import bpy
from ... base_types.node import AnimationNode

class TransformVector(bpy.types.Node, AnimationNode):
    bl_idname = "mn_TransformVector"
    bl_label = "Transform Vector"
    isDetermined = True

    inputNames = { "Vector" : "vector",
                   "Matrix" : "matrix" }

    outputNames = { "Vector" : "vector" }

    def create(self):
        self.inputs.new("mn_VectorSocket", "Vector")
        self.inputs.new("mn_MatrixSocket", "Matrix")
        self.outputs.new("mn_VectorSocket", "Vector")

    def getExecutionCode(self):
        return "$vector$ = %matrix% * mathutils.Vector(%vector%)"
        
    def getModuleList(self):
        return ["mathutils"]
