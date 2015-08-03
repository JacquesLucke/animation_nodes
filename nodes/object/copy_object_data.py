import bpy
from ... base_types.node import AnimationNode

class CopyObjectData(bpy.types.Node, AnimationNode):
    bl_idname = "an_CopyObjectData"
    bl_label = "Copy Object Data"

    inputNames = { "From" : "fromObject",
                   "To" : "toObject" }

    outputNames = { "To" : "toObject" }

    def create(self):
        self.inputs.new("an_ObjectSocket", "From")
        self.inputs.new("an_ObjectSocket", "To")
        self.outputs.new("an_ObjectSocket", "To")

    def execute(self, fromObject, toObject):
        if fromObject is not None and toObject is not None:
            if toObject.data != fromObject.data:
                if toObject.type == fromObject.type:
                    toObject.data = fromObject.data
        return toObject
