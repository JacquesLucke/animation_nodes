import bpy
from ... base_types.node import AnimationNode

class CopyObjectDataNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_CopyObjectDataNode"
    bl_label = "Copy Object Data"

    def create(self):
        self.inputs.new("an_ObjectSocket", "From", "fromObject")
        self.inputs.new("an_ObjectSocket", "To", "toObject")
        self.outputs.new("an_ObjectSocket", "To", "outObject")

    def execute(self, fromObject, toObject):
        if fromObject is None or toObject is None: return toObject
        if toObject.data == fromObject.data: return toObject
        if toObject.type == fromObject.type:
            toObject.data = fromObject.data
        return toObject
