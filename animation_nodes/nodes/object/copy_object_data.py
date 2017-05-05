import bpy
from ... base_types import AnimationNode
from ... utils.data_blocks import removeNotUsedDataBlock

class CopyObjectDataNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_CopyObjectDataNode"
    bl_label = "Copy Object Data"

    def create(self):
        self.newInput("Object", "From", "fromObject")
        self.newInput("Object", "To", "toObject")
        self.newOutput("Object", "To", "outObject")

    def execute(self, fromObject, toObject):
        if fromObject is None or toObject is None: return toObject
        if toObject.data == fromObject.data: return toObject

        if toObject.type == fromObject.type:
            oldData = toObject.data
            toObject.data = fromObject.data

            if oldData.users == 0 and oldData.an_data.removeOnZeroUsers:
                removeNotUsedDataBlock(oldData, toObject.type)

        return toObject
