import bpy
from ... base_types.node import AnimationNode

class VectorFromValue(bpy.types.Node, AnimationNode):
    bl_idname = "mn_VectorFromValue"
    bl_label = "Vector from Value"

    inputNames = { "Value" : "value" }
    outputNames = { "Vector" : "vector" }

    def create(self):
        self.inputs.new("mn_FloatSocket", "Value")
        self.outputs.new("mn_VectorSocket", "Vector")

    def getExecutionCode(self):
        return "$vector$ = mathutils.Vector((%value%, %value%, %value%))"

    def getModuleList(self):
        return ["mathutils"]
