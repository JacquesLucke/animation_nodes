import bpy
from bpy.props import *
from ... events import treeChanged
from ... base_types.node import AnimationNode
from ... tree_info import getNodeByIdentifier

class LoopBreakNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_LoopBreakNode"
    bl_label = "Loop Break"

    loopInputIdentifier = StringProperty(update = treeChanged)

    def create(self):
        self.inputs.new("an_BooleanSocket", "Break", "breakLoop");
        self.inputs.new("an_BooleanSocket", "Break Before", "breakBefore")

    def draw(self, layout):
        node = self.loopInputNode
        if node: layout.label(node.subprogramName, icon = "GROUP_VERTEX")

    def edit(self):
        network = self.network
        loopInput = network.loopInputNode
        print(loopInput)
        if network.type != "Invalid": return
        if network.loopInAmount != 1: return
        loopInput = network.loopInputNode
        if self.loopInputIdentifier == loopInput.identifier: return
        self.loopInputIdentifier = loopInput.identifier

    @property
    def loopInputNode(self):
        try: return getNodeByIdentifier(self.loopInputIdentifier)
        except: return None
