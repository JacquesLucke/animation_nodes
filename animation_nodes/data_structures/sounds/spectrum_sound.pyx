import bpy
from . utils cimport findStartAndEndFrame

cdef class SpectrumSound(Sound):

    def __cinit__(self, FloatList samples not None, int samplesPerFrame, int startFrame):
        if samplesPerFrame <= 0:
            raise ValueError("samplesPerFrame has to be positive")
        if len(samples) % samplesPerFrame != 0:
            raise ValueError("the amount of samples as to be a multiple of samplesPerFrame")

        self.type = "SPECTRUM"
        self.samples = samples
        self.samplesPerFrame = samplesPerFrame
        self.startFrame = startFrame
        self.endFrame = startFrame + len(samples) / samplesPerFrame - 1
        self.zeroList = FloatList.fromValues([0]) * self.samplesPerFrame

    @classmethod
    def fromSequences(cls, list sequences not None, int index):
        return createAverageSound(sequences, index)

    cpdef FloatList evaluate(self, float frame):
        return self.evaluateInt(<int>frame)

    cdef FloatList evaluateInt(self, int frame):
        if self.startFrame <= frame <= self.endFrame:
            frame -= self.startFrame
            return self.samples[frame * self.samplesPerFrame:(frame + 1) * self.samplesPerFrame]
        return self.zeroList.copy()

    cpdef float evaluateFrequency(self, float frame, float frequency):
        return 0

def createAverageSound(list sequences not None, int index):
    checkSpectrumSoundInput(sequences, index)
    return createValidSpectrumSound(sequences, index)

cdef checkSpectrumSoundInput(list sequences, int index):
    if len(sequences) == 0:
        raise ValueError("at least one sequence required")
    for sequence in sequences:
        if not isinstance(getattr(sequence, "sound", None), bpy.types.Sound):
            raise TypeError("at least one sequence has no sound")
        if index >= len(sequence.sound.bakedData.spectrum):
            raise IndexError("at least one sequence does not have the given bake index")

cdef createValidSpectrumSound(list sequences, int index):
    cdef int startFrame, endFrame, frequencyAmount
    cdef FloatList mixedSamples
    startFrame, endFrame = findStartAndEndFrame(sequences)
    frequencyAmount = getMaxFrequencyAmount(sequences, index)
    mixedSamples = mixSequenceSamplesInRange(sequences, index, startFrame, endFrame, frequencyAmount)
    return SpectrumSound(mixedSamples, frequencyAmount, startFrame)

cdef mixSequenceSamplesInRange(list sequences, int index, int rangeStart, int rangeEnd, int frequencyAmount):
    cdef FloatList mixedSamples = FloatList(length = frequencyAmount * (rangeEnd - rangeStart))
    cdef FloatList samples
    cdef int sequenceFrequencyAmount
    mixedSamples.fill(0)

    cdef int frame, finalStartFrame, finalEndFrame, sequenceStart, i
    for sequence in sequences:
        sound = sequence.sound
        samples = getSpectrumSoundSamples(sound, index)
        sequenceFrequencyAmount = sound.bakedData.spectrum[index].frequencyAmount

        sequenceStart = sequence.frame_start
        finalStartFrame = max(rangeStart, sequence.frame_final_start)
        finalEndFrame = min(rangeEnd, sequence.frame_final_end, len(samples) + sequenceStart)

        if sequenceFrequencyAmount == frequencyAmount:
            for frame in range(finalStartFrame, finalEndFrame):
                for i in range(frequencyAmount):
                    mixedSamples.data[(frame - rangeStart) * frequencyAmount + i] += samples.data[(frame - sequenceStart) * frequencyAmount + i]
        else:
            for frame in range(finalStartFrame, finalEndFrame):
                pass

    return mixedSamples

cdef dict cachedSpectrumSounds = dict()
cdef getSpectrumSoundSamples(sound, index):
    cdef str identifier = sound.bakedData.spectrum[index].identifier
    if identifier not in cachedSpectrumSounds:
        cachedSpectrumSounds[identifier] = sound.bakedData.spectrum[index].getSamples()
    return cachedSpectrumSounds[identifier]

cdef getMaxFrequencyAmount(list sequences, int index):
    return max(sequence.sound.bakedData.spectrum[index].frequencyAmount
               for sequence in sequences)
