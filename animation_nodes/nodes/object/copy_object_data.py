import bpy
from bpy.props import *
from ... events import propertyChanged
from ... utils.data_blocks import removeNotUsedDataBlock
from ... base_types import AnimationNode, VectorizedSocket

class CopyObjectDataNode(AnimationNode, bpy.types.Node):
    bl_idname = "an_CopyObjectDataNode"
    bl_label = "Copy Object Data"
    codeEffects = [VectorizedSocket.CodeEffect]

    deepCopy : BoolProperty(name = "Deep Copy", default = False, update = propertyChanged,
        description = "Make the data independent of the source by copying it")

    useFromList: VectorizedSocket.newProperty()
    useToList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput(VectorizedSocket("Object", ["useFromList", "useToList"],
            ("From", "fromObject"), ("From", "fromObjects")))

        self.newInput(VectorizedSocket("Object", "useToList",
            ("To", "toObject"), ("To", "toObjects"),
            codeProperties = dict(allowListExtension = False)))

        self.newOutput(VectorizedSocket("Object", "useToList",
            ("To", "outObject"), ("To", "outObjects")))

    def draw(self, layout):
        layout.prop(self, "deepCopy")

    def getExecutionCode(self, required):
        return "outObject = self.copyObjectData(fromObject, toObject)"

    def copyObjectData(self, fromObject, toObject):
        if fromObject is None or toObject is None: return toObject
        if not self.deepCopy and toObject.data == fromObject.data: return toObject

        if toObject.type == fromObject.type:
            oldData = toObject.data
            if self.deepCopy:
                toObject.data = fromObject.data.copy()
                toObject.data.an_data.removeOnZeroUsers = True
            else:
                toObject.data = fromObject.data

            if oldData.users == 0 and oldData.an_data.removeOnZeroUsers:
                removeNotUsedDataBlock(oldData, toObject.type)

        return toObject
