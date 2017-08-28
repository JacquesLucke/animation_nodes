import bpy
from ... base_types import AnimationNode
from ... data_structures import PathActionChannel, PathIndexActionChannel
from ... utils.attributes import setattrRecursive

class ObjectActionOutputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ObjectActionOutputNode"
    bl_label = "Object Action Output"

    def create(self):
        self.newInput("Object", "Object", "object")
        self.newInput("Action", "Action", "action")
        self.newInput("Integer", "Index", "index")
        self.newInput("Float", "Frame", "frame")
        self.newOutput("Object", "Object", "object")

    def execute(self, object, action, index, frame):
        channels = list(action.channels)
        evaluator = action.getEvaluator(channels)
        for channel, value in zip(channels, evaluator.pyEvaluate(frame, index)):
            if isinstance(channel, PathIndexActionChannel):
                p = channel.path + "[{}]".format(channel.index)
                setattrRecursive(object, p, value)
            elif isinstance(channel, PathActionChannel):
                setattrRecursive(object, channel.path, value)
        return object
