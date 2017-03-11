import bpy

cdef class AverageSound(Sound):
    def __cinit__(self, FloatList samples, int startFrame):
        self.type = "AVERAGE"
        self.samples = samples
        self.startFrame = startFrame
        self.endFrame = startFrame + len(samples) - 1

    @classmethod
    def fromSequences(cls, list sequences, int index):
        return createAverageSound(sequences, index)

    cpdef float evaluate(self, float frame):
        cdef int intFrame = <int>frame
        cdef float before = self.evaluateInt(intFrame)
        cdef float after = self.evaluateInt(intFrame + 1)
        cdef float influence = frame - intFrame
        return before * (1 - influence) + after * influence

    cdef float evaluateInt(self, int frame):
        if self.startFrame <= frame <= self.endFrame:
            return self.samples.data[frame - self.startFrame]
        return 0

def createAverageSound(list sequences, int index):
    if not canMakeAverageSound(sequences, index):
        raise Exception("cannot make AverageSound")

    return createValidAverageSound(sequences, index)

cdef canMakeAverageSound(list sequences, int index):
    if len(sequences) == 0: return False
    for sequence in sequences:
        if sequence is None:
            return False
        if not isinstance(getattr(sequence, "sound", None), bpy.types.Sound):
            return False
        if index >= len(sequence.sound.averageData):
            return False
    return True

cdef createValidAverageSound(list sequences, int index):
    cdef int startFrame, endFrame
    cdef FloatList mixedSamples
    startFrame, endFrame = findStartAndEndFrame(sequences)
    mixedSamples = addSequenceSamplesInRange(sequences, index, startFrame, endFrame)
    return AverageSound(mixedSamples, startFrame)

cdef FloatList addSequenceSamplesInRange(list sequences, int index, int rangeStart, int rangeEnd):
    cdef FloatList mixedSamples = FloatList(length = rangeEnd - rangeStart)
    cdef FloatList samples
    mixedSamples.fill(0)

    cdef int frame, finalStartFrame, finalEndFrame, sequenceStart
    for sequence in sequences:
        samples = getAverageSoundSamples(sequence.sound, index)
        sequenceStart = sequence.frame_start
        finalStartFrame = max(rangeStart, sequence.frame_final_start)
        finalEndFrame = min(rangeEnd, sequence.frame_final_end, len(samples) + sequenceStart)

        for frame in range(finalStartFrame, finalEndFrame):
            mixedSamples.data[frame - rangeStart] += samples.data[frame - sequenceStart]

    return mixedSamples

cdef dict cachedAverageSounds = dict()
cdef getAverageSoundSamples(sound, index):
    cdef str identifier = sound.averageData[index].identifier
    if identifier not in cachedAverageSounds:
        cachedAverageSounds[identifier] = sound.averageData[index].getSamples()
    return cachedAverageSounds[identifier]

cdef findStartAndEndFrame(sequences):
    startFrame = min(sequence.frame_final_start for sequence in sequences)
    endFrame = max(sequence.frame_final_end for sequence in sequences)
    return startFrame, endFrame
