import bpy
from ... base_types.node import AnimationNode

class CopyObjectData(bpy.types.Node, AnimationNode):
    bl_idname = "an_CopyObjectData"
    bl_label = "Copy Object Data"

    def create(self):
        self.inputs.new("an_ObjectSocket", "From", "fromObject")
        self.inputs.new("an_ObjectSocket", "To", "toObject")
        self.outputs.new("an_ObjectSocket", "To", "outObject")

    def execute(self, fromObject, toObject):
        if fromObject is not None and toObject is not None:
            if toObject.data != fromObject.data:
                if toObject.type == fromObject.type:
                    toObject.data = fromObject.data
        return toObject
