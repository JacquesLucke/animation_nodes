from . action_utilities import (
    FilledBoundedActionEvaluator, FilledUnboundedActionEvaluator
)

from . action_utilities cimport (
    BoundedActionProvider, UnboundedActionProvider,
    BoundedActionProviderEvaluator, UnboundedActionProviderEvaluator
)

ctypedef fused set_or_list:
    set
    list


# Actions
#########################################################

cdef class Action:
    @classmethod
    def checkChannels(cls, set_or_list channels):
        if any((not isinstance(channel, ActionChannel) for channel in channels)):
            raise Exception("Invalid channels")

    def getEvaluator(self, channels, defaults = None):
        if isinstance(channels, ActionChannel):
            channels = [channels]
        elif isinstance(channels, list):
            if len(channels) > 0 and not isinstance(channels[0], ActionChannel):
                channels = ActionChannel.initList(channels)
        else:
            channels = list(channels)
        self.checkChannels(channels)

        if defaults is None:
            defaults = FloatList.fromValue(0, length = len(channels))
        elif isinstance(defaults, (int, float)):
            defaults = FloatList.fromValue(defaults, length = len(channels))
        elif not isinstance(defaults, FloatList):
            defaults = FloatList.fromValues(defaults)
        elif isinstance(defaults, FloatList):
            pass
        else:
            raise Exception("defaults has to be a number or a list of numbers")

        return self.getEvaluator_Full(channels, defaults)

    def __repr__(self):
        bounded = isinstance(self, BoundedAction)
        typeString = "Bounded" if bounded else "Unbounded"
        text = "{} Action with {} channels:\n".format(typeString, len(self.channels))
        for channel in sorted(self.channels, key = str):
            text += "    {}\n".format(channel)
        return text

cdef class BoundedAction(Action):
    cdef BoundedActionEvaluator getEvaluator_Limited(self, list channels):
        defaults = FloatList.fromValue(0, length = len(channels))
        return self.getEvaluator_Full(channels, defaults)

    cpdef BoundedActionEvaluator getEvaluator_Full(self, list channels, FloatList defaults):
        if len(channels) != defaults.length:
            raise Exception("unequal channel and default amount")

        if all([channel in self.channels for channel in channels]):
            return self.getEvaluator_Limited(channels)
        else:
            return FilledBoundedActionEvaluator(self, channels, defaults)

    def getProviderEvaluator(self, BoundedActionProvider provider, list channels):
        return BoundedActionProviderEvaluator(provider, channels)

cdef class UnboundedAction(Action):
    cdef UnboundedActionEvaluator getEvaluator_Limited(self, list channels):
        raise NotImplementedError()

    cpdef UnboundedActionEvaluator getEvaluator_Full(self, list channels, FloatList defaults):
        if len(channels) != defaults.length:
            raise Exception("unequal channel and default amount")

        if all([channel in self.channels for channel in channels]):
            return self.getEvaluator_Limited(channels)
        else:
            return FilledUnboundedActionEvaluator(self, channels, defaults)


# Action Evaluators
#########################################################

cdef class ActionEvaluator:
    def pyEvaluate(self, float frame, Py_ssize_t index = 0):
        cdef FloatList values = FloatList(length = self.channelAmount)
        self.evaluate(frame, index, values.data)
        return values

    cdef void evaluate(self, float frame, Py_ssize_t index, float *target):
        raise NotImplementedError()

    def __repr__(self):
        if self.channelAmount == 1:
            return "<ActionEvaluator for {} channel>".format(self.channelAmount)
        else:
            return "<ActionEvaluator for {} channels>".format(self.channelAmount)

cdef class UnboundedActionEvaluator(ActionEvaluator):
    pass

cdef class BoundedActionEvaluator(ActionEvaluator):
    cdef void evaluateBounded(self, float t, Py_ssize_t index, float *target):
        cdef float frame = t * self.getLength(index) + self.getStart(index)
        self.evaluate(frame, index, target)

    cpdef float getStart(self, Py_ssize_t index):
        return self.getEnd(index) - self.getLength(index)

    cpdef float getEnd(self, Py_ssize_t index):
        return self.getStart(index) + self.getLength(index)

    cpdef float getLength(self, Py_ssize_t index):
        return self.getEnd(index) - self.getStart(index)


# Action Channel
#########################################################

cdef class ActionChannel:
    def __richcmp__(x, y, int op):
        raise NotImplementedError()

    def __hash__(self):
        raise NotImplementedError()

    @classmethod
    def initList(cls, list values):
        cdef list channels = []
        for value in values:
            if isinstance(value, str):
                channels.append(PathActionChannel(value))
            elif isinstance(value, tuple):
                path = value[0]
                for index in value[1:]:
                    channels.append(PathIndexActionChannel(path, index))
            else:
                raise Exception("cannot create channels from given data")
        return channels

cdef class PathActionChannel(ActionChannel):
    def __init__(self, str path):
        self.path = path

    def __richcmp__(x, y, int op):
        if not isinstance(x, y.__class__):
            return NotImplemented

        if op == 2:
            return x.path == y.path
        elif op == 3:
            return x.path != y.path

    def __hash__(self):
        return hash(self.path)

    def __repr__(self):
        return "<Channel '{}'>".format(self.path)

cdef class PathIndexActionChannel(ActionChannel):
    def __init__(self, str property, Py_ssize_t index):
        if index < 0:
            raise ValueError("Index must be >= 0")

        self.property = property
        self.index = index

    @property
    def path(self):
        return "{}[{}]".format(self.property, self.index)

    def __richcmp__(x, y, int op):
        if not isinstance(x, y.__class__):
            return NotImplemented

        if op == 2:
            return x.property == y.property and x.index == y.index
        elif op == 3:
            return x.property != y.property or x.index != y.index

    def __hash__(self):
        return hash((self.property, self.index))

    def __repr__(self):
        return "<Channel '{}'[{}]>".format(self.property, self.index)
