import bpy
from bpy.props import *
from ... sockets.info import getCopyFunction
from ... algorithms.lists import mask as maskList
from ... base_types import AnimationNode, ListTypeSelectorSocket

class MaskListNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_MaskListNode"
    bl_label = "Mask List"

    errorMessage = StringProperty()

    assignedType = ListTypeSelectorSocket.newProperty(default = "Integer List")

    def create(self):
        prop = ("assignedType", "LIST")
        self.newInput(ListTypeSelectorSocket(
            "List", "inList", "LIST", prop))
        self.newInput("Boolean List", "Mask", "mask")
        self.newOutput(ListTypeSelectorSocket(
            "List", "outList", "LIST", prop))

    def draw(self, layout):
        if self.errorMessage != "":
            layout.label(self.errorMessage, icon = "ERROR")

    def execute(self, inList, mask):
        self.errorMessage = ""
        if len(inList) == len(mask):
            return maskList(self.assignedType, inList, mask)
        else:
            self.errorMessage = "lists have different length"
            return getCopyFunction(self.assignedType)(inList)
