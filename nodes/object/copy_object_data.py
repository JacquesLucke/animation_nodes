import bpy
from ... base_types.node import AnimationNode

class CopyObjectData(bpy.types.Node, AnimationNode):
    bl_idname = "mn_CopyObjectData"
    bl_label = "Copy Object Data"

    inputNames = { "From" : "fromObject",
                   "To" : "toObject" }

    outputNames = { "To" : "toObject" }

    def create(self):
        self.inputs.new("mn_ObjectSocket", "From")
        self.inputs.new("mn_ObjectSocket", "To")
        self.outputs.new("mn_ObjectSocket", "To")

    def execute(self, fromObject, toObject):
        if fromObject is not None and toObject is not None:
            if toObject.data != fromObject.data:
                if toObject.type == fromObject.type:
                    toObject.data = fromObject.data
        return toObject
