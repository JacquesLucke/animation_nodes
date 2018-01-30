import bpy
from bpy.props import *
from mathutils import Matrix
from ... base_types import AnimationNode, VectorizedSocket
from ... utils.attributes import getMultiAttibuteSetter

from ... data_structures cimport (
    Action, ActionEvaluator,
    PathActionChannel, PathIndexActionChannel,
    FloatList, VirtualMatrix4x4List
)

from ... math cimport (
    Vector3, Euler3, Matrix4, toPyMatrix4, multMatrix4,
    setTranslationRotationScaleMatrix
)

modeItems = [
    ("GENERIC", "Generic", "Evaluate raw action without additional work", "NONE", 0),
    ("TRANSFORMS", "Transforms", "Handle transform channels specifically", "NONE", 1)
]

class ObjectActionOutputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ObjectActionOutputNode"
    bl_label = "Object Action Output"

    mode = EnumProperty(name = "Mode", default = "GENERIC",
        items = modeItems, update = AnimationNode.refresh)

    useObjectList = VectorizedSocket.newProperty()
    useMatrixList = VectorizedSocket.newProperty()

    def create(self):
        self.newInput(VectorizedSocket("Object", "useObjectList",
            ("Object", "object", dict(defaultDrawType = "PROPERTY_ONLY")),
            ("Objects", "objects")))

        self.newInput("Action", "Action", "action")
        self.newInput("Float", "Frame", "frame")

        if self.mode == "TRANSFORMS":
            self.newInput(VectorizedSocket("Matrix", ["useMatrixList", "useObjectList"],
                ("Offset", "offset"), ("Offsets", "offsets")))

        if self.useObjectList:
            self.newInput("Integer", "Start Index", "index")
        else:
            self.newInput("Integer", "Index", "index")

        self.newOutput(VectorizedSocket("Object", "useObjectList",
            ("Object", "object"), ("Objects", "objects")))

    def draw(self, layout):
        layout.prop(self, "mode", text = "")

    def getExecutionFunctionName(self):
        if self.mode == "GENERIC":
            if self.useObjectList:
                return "execute_Generic_List"
            else:
                return "execute_Generic_Single"
        elif self.mode == "TRANSFORMS":
            if self.useObjectList:
                return "execute_Transforms_List"
            else:
                return "execute_Transforms_Single"

    def execute_Generic_Single(self, object, Action action, frame, index):
        self.execute_Generic_List([object], action, frame, index)
        return object

    def execute_Transforms_Single(self, object, Action action, float frame, offset, index):
        self.execute_Transforms_List([object], action, frame, offset, index)
        return object

    def execute_Generic_List(self, list objects, Action action, float frame, Py_ssize_t startIndex):
        if action is None:
            return objects

        self.execute_RawChannels(objects, action, list(action.getChannelSet()), frame, startIndex)
        return objects

    def execute_Transforms_List(self, list objects, Action action, float frame,
                                offsets, Py_ssize_t  startIndex):
        if action is None:
            return objects

        cdef list channels = PathIndexActionChannel.forArrays(
            ["location", "rotation_euler", "scale"], 3)

        cdef FloatList defaults = FloatList.fromValues([0, 0, 0, 0, 0, 0, 1, 1, 1])
        cdef ActionEvaluator evaluator = action.getEvaluator(channels, defaults)
        cdef FloatList values = FloatList(length = len(channels))

        cdef VirtualMatrix4x4List _offsets = VirtualMatrix4x4List.fromListOrElement(offsets, Matrix.Identity(4))

        cdef Matrix4 *offset
        cdef Vector3 *location
        cdef Vector3 *scale
        cdef Euler3 rotation
        cdef Matrix4 localMatrix, finalMatrix

        cdef Py_ssize_t i
        for i in range(len(objects)):
            object = objects[i]
            if object is None:
                continue

            evaluator.evaluate(frame, startIndex + i, values.data)
            offset = _offsets.get(i)

            location = <Vector3*>values.data
            scale = <Vector3*>(values.data + 6)
            rotation = Euler3(values.data[3], values.data[4], values.data[5], 0)

            setTranslationRotationScaleMatrix(&localMatrix, location, &rotation, scale)
            multMatrix4(&finalMatrix, offset, &localMatrix)
            object.matrix_world = toPyMatrix4(&finalMatrix)

        cdef list otherChannels = list(action.getChannelSet() - set(channels))
        self.execute_RawChannels(objects, action, otherChannels, frame, startIndex)

        return objects

    def execute_RawChannels(self, list objects, Action action, list channels,
                            float frame, Py_ssize_t startIndex):
        channels = self.getKnownChannels(channels)
        if len(channels) == 0:
            return

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

            evaluator.evaluate(frame, startIndex + i, values.data)
            setAttributes(object, values)

    def getKnownChannels(self, list allChannels):
        cdef list channels = []
        for channel in allChannels:
            if isinstance(channel, (PathActionChannel, PathIndexActionChannel)):
                channels.append(channel)
        return channels
