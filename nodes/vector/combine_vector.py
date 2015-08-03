import bpy
from ... base_types.node import AnimationNode

class CombineVector(bpy.types.Node, AnimationNode):
    bl_idname = "an_CombineVector"
    bl_label = "Combine Vector"
    isDetermined = True

    inputNames = { "X" : "x",
                   "Y" : "y",
                   "Z" : "z" }

    outputNames = { "Vector" : "vector" }

    def create(self):
        self.inputs.new("an_FloatSocket", "X")
        self.inputs.new("an_FloatSocket", "Y")
        self.inputs.new("an_FloatSocket", "Z")
        self.outputs.new("an_VectorSocket", "Vector")

    def getExecutionCode(self):
        return "$vector$ = mathutils.Vector((%x%, %y%, %z%))"
        
    def getModuleList(self):
        return ["mathutils"]
