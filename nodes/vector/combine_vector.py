import bpy
from ... base_types.node import AnimationNode

class CombineVector(bpy.types.Node, AnimationNode):
    bl_idname = "mn_CombineVector"
    bl_label = "Combine Vector"
    isDetermined = True

    inputNames = { "X" : "x",
                   "Y" : "y",
                   "Z" : "z" }

    outputNames = { "Vector" : "vector" }

    def create(self):
        self.inputs.new("mn_FloatSocket", "X")
        self.inputs.new("mn_FloatSocket", "Y")
        self.inputs.new("mn_FloatSocket", "Z")
        self.outputs.new("mn_VectorSocket", "Vector")

    def getExecutionCode(self):
        return "$vector$ = mathutils.Vector((%x%, %y%, %z%))"
        
    def getModuleList(self):
        return ["mathutils"]
