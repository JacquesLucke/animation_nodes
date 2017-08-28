import bpy
from ... base_types import AnimationNode
from ... utils.attributes import getMultiAttibuteSetter
from ... data_structures cimport Action, ActionEvaluator, PathActionChannel, PathIndexActionChannel, FloatList

class ObjectActionOutputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ObjectActionOutputNode"
    bl_label = "Object Action Output"

    def create(self):
        self.newInput("Object List", "Objects", "objects")
        self.newInput("Action", "Action", "action")
        self.newInput("Float", "Frame", "frame")
        self.newOutput("Object List", "Objects", "objects")

    def execute(self, list objects, Action action, float frame):
        if action is None:
            return objects

        cdef list channels = self.getRelevantChannels(action)
        cdef tuple paths = tuple(channel.path for channel in channels)
        cdef ActionEvaluator evaluator = action.getEvaluator(channels)
        cdef FloatList values = FloatList(length = len(channels))
        setAttributes = getMultiAttibuteSetter(paths)

        # TODO: error handling (when the attributes don't exist)
        cdef Py_ssize_t i, j
        for i in range(len(objects)):
            object = objects[i]
            if object is None:
                continue

            evaluator.evaluate(frame - i, i, values.data)
            setAttributes(object, values)

        return objects

    def getRelevantChannels(self, Action action):
        cdef list channels = []
        for channel in action.channels:
            if isinstance(channel, (PathActionChannel, PathIndexActionChannel)):
                channels.append(channel)
        return channels
