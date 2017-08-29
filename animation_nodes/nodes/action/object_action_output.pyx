import bpy
from bpy.props import *
from mathutils import Matrix
from ... base_types import AnimationNode, VectorizedSocket
from ... utils.attributes import getMultiAttibuteSetter
from ... data_structures cimport Action, ActionEvaluator, PathActionChannel, PathIndexActionChannel, FloatList, VirtualDoubleList, VirtualMatrix4x4List
from ... math cimport Vector3, Euler3, Matrix4, setTranslationRotationScaleMatrix, toPyMatrix4, multMatrix4

modeItems = [
    ("GENERIC", "Generic", "Evaluate raw action without additional work", "NONE", 0),
    ("TRANSFORMS", "Transforms", "Handle transform channels specifically", "NONE", 1)
]

class ObjectActionOutputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ObjectActionOutputNode"
    bl_label = "Object Action Output"

    mode = EnumProperty(name = "Mode", default = "GENERIC",
        items = modeItems, update = AnimationNode.refresh)

    useFrameList = VectorizedSocket.newProperty()
    useMatrixList = VectorizedSocket.newProperty()

    def create(self):
        self.newInput("Object List", "Objects", "objects")
        self.newInput("Action", "Action", "action")
        self.newInput(VectorizedSocket("Float", "useFrameList",
            ("Frame", "frame"), ("Frames", "frames")))
        if self.mode == "TRANSFORMS":
            self.newInput(VectorizedSocket("Matrix", "useMatrixList",
                ("Offset", "offset"), ("Offsets", "offsets")))
        self.newOutput("Object List", "Objects", "objects")

    def draw(self, layout):
        layout.prop(self, "mode", text = "")

    def getExecutionFunctionName(self):
        if self.mode == "GENERIC":
            return "execute_Generic"
        elif self.mode == "TRANSFORMS":
            return "execute_Transforms"

    def execute_Generic(self, list objects, Action action, frames):
        if action is None:
            return objects

        cdef VirtualDoubleList _frames = VirtualDoubleList.fromListOrElement(frames, 0)
        self.execute_RawChannels(objects, action, list(action.channels), _frames)

        return objects

    def execute_Transforms(self, list objects, Action action, frames, offsets):
        if action is None:
            return objects

        cdef list channels = PathIndexActionChannel.initList([
            ("location", 0, 1, 2),
            ("rotation_euler", 0, 1, 2),
            ("scale", 0, 1, 2)])

        cdef FloatList defaults = FloatList.fromValues([0, 0, 0, 0, 0, 0, 1, 1, 1])
        cdef ActionEvaluator evaluator = action.getEvaluator(channels, defaults)
        cdef FloatList values = FloatList(length = len(channels))

        cdef VirtualDoubleList _frames = VirtualDoubleList.fromListOrElement(frames, 0)
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

            evaluator.evaluate(<float>_frames.get(i), i, values.data)
            offset = _offsets.get(i)

            location = <Vector3*>values.data
            scale = <Vector3*>(values.data + 6)
            rotation = Euler3(values.data[3], values.data[4], values.data[5], 0)

            setTranslationRotationScaleMatrix(&localMatrix, location, &rotation, scale)
            multMatrix4(&finalMatrix, offset, &localMatrix)
            object.matrix_world = toPyMatrix4(&finalMatrix)

        cdef list otherChannels = list(action.channels - set(channels))
        self.execute_RawChannels(objects, action, otherChannels, _frames)

        return objects

    def execute_RawChannels(self, list objects, Action action, list channels, VirtualDoubleList frames):
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

            evaluator.evaluate(<float>frames.get(i), i, values.data)
            setAttributes(object, values)

    def getKnownChannels(self, list allChannels):
        cdef list channels = []
        for channel in allChannels:
            if isinstance(channel, (PathActionChannel, PathIndexActionChannel)):
                channels.append(channel)
        return channels
