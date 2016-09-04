import bpy
from bpy.props import *
from ... sockets.info import isList
from ... tree_info import keepNodeLinks
from ... base_types import AnimationNode

class ShuffleListNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ShuffleListNode"
    bl_label = "Shuffle List"

    def assignedTypeChanged(self, context):
        self.generateSockets()

    assignedType = StringProperty(update = assignedTypeChanged)

    def create(self):
        self.assignedType = "Object List"

    def getExecutionCode(self):
        return ("random.seed(seed)",
                "random.shuffle(list)")

    def getUsedModules(self):
        return ["random"]

    def edit(self):
        listDataType = self.getWantedDataType()
        self.assignType(listDataType)

    def getWantedDataType(self):
        listInput = self.inputs[0].dataOrigin
        listOutputs = self.outputs[0].dataTargets

        if listInput is not None: return listInput.dataType
        if len(listOutputs) == 1: return listOutputs[0].dataType
        return self.inputs[0].dataType

    def assignType(self, listDataType):
        if not isList(listDataType): return
        if listDataType == self.assignedType: return
        self.assignedType = listDataType

    @keepNodeLinks
    def generateSockets(self):
        self.inputs.clear()
        self.outputs.clear()

        listDataType = self.assignedType
        self.newInput(listDataType, "List", "list", dataIsModified = True)
        self.newInput("an_IntegerSocket", "Seed", "seed")
        self.newOutput(listDataType, "Shuffled List", "list")
