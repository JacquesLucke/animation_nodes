import bpy
from bpy.props import *
from ... base_types import AnimationNode

from libc.string cimport memcpy
from ... data_structures cimport (
    FloatList,
    BoundedAction, UnboundedAction,
    PathActionChannel, PathIndexActionChannel,
    UnboundedActionEvaluator, BoundedActionEvaluator
)

modeItems = [
    ("SINGLE_PATH", "Single Path", "", "NONE", 0)
]

class ConstantActionNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ConstantActionNode"
    bl_label = "Constant Action"

    mode = EnumProperty(name = "Mode", default = "SINGLE_PATH",
        items = modeItems, update = AnimationNode.refresh)

    bounded = BoolProperty(name = "Bounded", default = False,
        update = AnimationNode.refresh)

    def create(self):
        if self.mode == "SINGLE_PATH":
            self.newInput("Text", "Path", "path")
            self.newInput("Float", "Value", "value")

        if self.bounded:
            self.newInput("Float", "Start", "start")
            self.newInput("Float", "End", "end", value = 50)

        self.newOutput("Action", "Action", "action")

    def draw(self, layout):
        layout.prop(self, "mode", text = "")
        layout.prop(self, "bounded")

    def getExecutionFunctionName(self):
        if self.bounded:
            if self.mode == "SINGLE_PATH":
                return "execute_SinglePath_Bounded"
        else:
            if self.mode == "SINGLE_PATH":
                return "execute_SinglePath_Unbounded"

    def execute_SinglePath_Unbounded(self, path, value):
        channel = PathActionChannel(path)
        return ConstantUnboundedAction(channel, value)

    def execute_SinglePath_Bounded(self, path, value, float start, float end):
        channel = PathActionChannel(path)
        return ConstantBoundedAction(channel, value, start, end)
