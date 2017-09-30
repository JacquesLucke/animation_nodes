import bpy
from bpy.props import *
from ... base_types import AnimationNode
from ... data_structures import DelayAction

class DelayActionNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_DelayActionNode"
    bl_label = "Delay Action"

    relative = BoolProperty(name = "Relative", default = True)

    def create(self):
        self.newInput("Action", "Action", "inAction")
        self.newInput("Float", "Delay", "delay", value = 5)
        self.newOutput("Action", "Action", "outAction")

    def draw(self, layout):
        layout.prop(self, "relative")

    def execute(self, action, delay):
        if action is None:
            return None

        return DelayAction(action, delay, self.relative)
