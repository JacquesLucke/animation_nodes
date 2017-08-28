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
        else:
            raise Exception("defaults has to be a number or a list of numbers")

        return self.getEvaluator_Full(channels, defaults)

    def __repr__(self):
        text = "Action with {} channels:\n".format(len(self.channels))
        for channel in sorted(self.channels, key = str):
            text += "    {}\n".format(channel)
        return text

cdef class BoundedAction(Action):
    cdef BoundedActionEvaluator getEvaluator_Limited(self, list channels):
        raise NotImplementedError()

    cpdef BoundedActionEvaluator getEvaluator_Full(self, list channels, FloatList defaults):
        if len(channels) != defaults.length:
            raise Exception("unequal channel and default amount")

        if all([channel in self.channels for channel in channels]):
            return self.getEvaluator_Limited(channels)
        else:
            return FilledBoundedActionEvaluator(self, channels, defaults)

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


# Action Evaluator Helpers
#########################################################

cdef class FilledUnboundedActionEvaluator(UnboundedActionEvaluator):
    cdef:
        FloatList evaluatorTarget
        FloatList defaults
        IntegerList defaultMapping
        IntegerList evaluatorMapping
        UnboundedActionEvaluator evaluator

    def __cinit__(self, UnboundedAction source, list channels, FloatList defaults):
        self.channelAmount = len(channels)

        cdef list evaluatorChannels = []
        self.defaultMapping = IntegerList()
        self.evaluatorMapping = IntegerList()

        cdef Py_ssize_t i, j
        for i, channel in enumerate(channels):
            if channel in source.channels:
                evaluatorChannels.append(channel)
                self.evaluatorMapping.append(i)
            else:
                self.defaultMapping.append(i)

        self.defaults = defaults
        self.evaluator = source.getEvaluator(evaluatorChannels)
        self.evaluatorTarget = FloatList(length = len(evaluatorChannels))

    cdef void evaluate(self, float frame, Py_ssize_t index, float *target):
        self.evaluator.evaluate(frame, index, self.evaluatorTarget.data)

        cdef Py_ssize_t i
        for i in range(self.evaluatorMapping.length):
            target[self.evaluatorMapping.data[i]] = self.evaluatorTarget.data[i]

        cdef Py_ssize_t j
        for i in range(self.defaultMapping.length):
            j = self.defaultMapping.data[i]
            target[j] = self.defaults.data[j]

cdef class FilledBoundedActionEvaluator(BoundedActionEvaluator):
    cdef:
        FloatList evaluatorTarget
        FloatList defaults
        IntegerList defaultMapping
        IntegerList evaluatorMapping
        BoundedActionEvaluator evaluator

    def __cinit__(self, BoundedAction source, list channels, FloatList defaults):
        self.channelAmount = len(channels)

        cdef list evaluatorChannels = []
        self.defaultMapping = IntegerList()
        self.evaluatorMapping = IntegerList()

        cdef Py_ssize_t i, j
        for i, channel in enumerate(channels):
            if channel in source.channels:
                evaluatorChannels.append(channel)
                self.evaluatorMapping.append(i)
            else:
                self.defaultMapping.append(i)

        self.defaults = defaults
        self.evaluator = source.getEvaluator(evaluatorChannels)
        self.evaluatorTarget = FloatList(length = len(evaluatorChannels))

    cdef void evaluate(self, float frame, Py_ssize_t index, float *target):
        self.evaluator.evaluate(frame, index, self.evaluatorTarget.data)

        cdef Py_ssize_t i
        for i in range(self.evaluatorMapping.length):
            target[self.evaluatorMapping.data[i]] = self.evaluatorTarget.data[i]

        cdef Py_ssize_t j
        for i in range(self.defaultMapping.length):
            j = self.defaultMapping.data[i]
            target[j] = self.defaults.data[j]

    cpdef float getStart(self, Py_ssize_t index):
        return self.evaluator.getStart(index)

    cpdef float getEnd(self, Py_ssize_t index):
        return self.evaluator.getEnd(index)

    cpdef float getLength(self, Py_ssize_t index):
        return self.evaluator.getLength(index)


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

cdef class PathIndexActionChannel(PathActionChannel):
    def __init__(self, str path, Py_ssize_t index):
        if index < 0:
            raise ValueError("Index must be >= 0")

        self.path = path
        self.index = index

    def __richcmp__(x, y, int op):
        if not isinstance(x, y.__class__):
            return NotImplemented

        if op == 2:
            return x.path == y.path and x.index == y.index
        elif op == 3:
            return x.path != y.path or x.index != y.index

    def __hash__(self):
        return hash((self.path, self.index))

    def __repr__(self):
        return "<Channel '{}'[{}]>".format(self.path, self.index)
