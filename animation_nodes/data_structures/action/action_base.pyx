from .. lists.base_lists cimport FloatList

ctypedef fused set_or_list:
    set
    list

cdef class Action:
    cdef set getChannelSet(self):
        raise NotImplementedError()

    def getChannels(self):
        return self.getChannelSet()

    @classmethod
    def checkChannels(cls, set_or_list channels):
        if any((not isinstance(channel, ActionChannel) for channel in channels)):
            raise Exception("Invalid channels")

    def getEvaluator(self, channels, defaults = None):
        if isinstance(channels, ActionChannel):
            channels = [channels]
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

    def drawPreview(self, Py_ssize_t index, rectangle, float recBeginFrame, float recEndFrame):
        raise NotImplementedError()

cdef class ActionChannel:
    def __richcmp__(x, y, int op):
        raise NotImplementedError()

    def __hash__(self):
        raise NotImplementedError()
