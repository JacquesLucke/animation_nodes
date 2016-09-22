import bpy
from bpy.props import *
from ... sockets.info import isList
from ... base_types import AnimationNode, UpdateAssignedListDataType

class ShuffleListNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ShuffleListNode"
    bl_label = "Shuffle List"

    assignedType = StringProperty(update = AnimationNode.updateSockets, default = "Float List")

    def create(self):
        listDataType = self.assignedType
        
        self.newInput(listDataType, "List", "list", dataIsModified = True)
        self.newInput("an_IntegerSocket", "Seed", "seed")
        self.newOutput(listDataType, "Shuffled List", "list")

        self.newSocketEffect(UpdateAssignedListDataType("assignedType", "LIST",
            [(self.inputs[0], "LIST"),
             (self.outputs[0], "LIST")]
        ))

    def getExecutionCode(self):
        return ("random.seed(seed)",
                "random.shuffle(list)")

    def getUsedModules(self):
        return ["random"]
