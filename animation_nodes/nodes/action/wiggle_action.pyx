import bpy
from bpy.props import *
from ... base_types import AnimationNode
from ... algorithms.perlin_noise cimport perlinNoise1D
from ... events import propertyChanged
from ... data_structures cimport (
    UnboundedAction,
    UnboundedActionEvaluator,
    FloatList,
    PathActionChannel,
    PathIndexActionChannel
)

actionChannelTypeItems = [
    ("PATH", "Path", "", "NONE", 0),
    ("PATH_INDEX", "Path Index", "", "NONE", 1)
]

class ActionChannelProperty(bpy.types.PropertyGroup):
    bl_idname = "an_ActionChannelProperty"

    __annotations__ = {}
    __annotations__["channelType"] = EnumProperty(name = "Channel Type", default = "PATH",
        items = actionChannelTypeItems, update = propertyChanged)
    __annotations__["channelPath"] = StringProperty(name = "Channel Path")
    __annotations__["channelIndex"] = IntProperty(name = "Channel Index", min = 0)

    def draw(self, layout, node, index):
        col = layout.column(align = True)
        row = col.row(align = True)
        row.prop(self, "channelType", text = "")
        node.invokeFunction(row, "removeChannel", icon = "X", data = index)
        row = col.row(align = True)
        row.prop(self, "channelPath", text = "")
        if self.channelType == "PATH_INDEX":
            row.prop(self, "channelIndex", text = "")

    def getChannel(self):
        if self.channelType == "PATH":
            return PathActionChannel(self.channelPath)
        elif self.channelType == "PATH_INDEX":
            return PathIndexActionChannel(self.channelPath, self.channelIndex)

class ActionChannelsNodeBase:
    __annotations__ = {}
    __annotations__["channels"] = CollectionProperty(type = ActionChannelProperty)

    def drawChannels(self, layout):
        for i, channel in enumerate(self.channels):
            channel.draw(layout, self, i)

        self.invokeFunction(layout, "addChannel", text = "Add", icon = "PLUS")

    def addChannel(self):
        self.channels.add()

    def removeChannel(self, strIndex):
        self.channels.remove(int(strIndex))

    def getChannels(self):
        return [item.getChannel() for item in self.channels]

    def getFirstInvalidChannel(self):
        for channelItem in self.channels:
            channel = channelItem.getChannel()
            if isinstance(channel, PathActionChannel):
                if not channel.path.isidentifier():
                    return channel.path
            elif isinstance(channel, PathIndexActionChannel):
                if not channel.property.isidentifier():
                    return channel.property
        return None

class WiggleActionNode(AnimationNode, bpy.types.Node, ActionChannelsNodeBase):
    bl_idname = "an_WiggleActionNode"
    bl_label = "Wiggle Action"
    errorHandlingType = "EXCEPTION"

    def create(self):
        self.newInput("Integer", "Seed", "seed")
        self.newInput("Float", "Amplitude", "amplitude", value = 3)
        self.newOutput("Action", "Action", "action")

    def draw(self, layout):
        self.drawChannels(layout)

    def execute(self, seed, amplitude):
        self.validateChannels()
        channels = self.getChannels()
        return WiggleAction(amplitude, channels, seed)

    def validateChannels(self):
        invalidPath = self.getFirstInvalidChannel()
        if invalidPath is None: return
        self.raiseErrorMessage(repr(invalidPath) + " is not a valid channel!")

cdef class WiggleAction(UnboundedAction):
    cdef float amplitude
    cdef set channels
    cdef Py_ssize_t seed

    def __cinit__(self, float amplitude, list channels, Py_ssize_t seed):
        self.amplitude = amplitude
        self.seed = seed
        self.channels = set(channels)
        self.checkChannels(channels)

    cdef set getChannelSet(self):
        return self.channels

    cdef UnboundedActionEvaluator getEvaluator_Limited(self, list channels):
        cdef FloatList factors
        factors = FloatList.fromValue(self.amplitude, length = len(channels))
        return WiggleActionEvaluator(factors, self.seed)

cdef class WiggleActionEvaluator(UnboundedActionEvaluator):
    cdef FloatList factors
    cdef Py_ssize_t seed

    def __cinit__(self, FloatList factors, Py_ssize_t seed):
        self.factors = factors
        self.seed = seed
        self.channelAmount = len(factors)

    cdef void evaluate(self, float frame, Py_ssize_t index, float *target):
        cdef Py_ssize_t i
        for i in range(self.factors.length):
            target[i] = self.factors.data[i] * perlinNoise1D((frame + 23424) / 20 + index * 123124 + i * 43543 + self.seed * 3452, 0.5, 3)
