import bpy
import numpy
from bpy.props import *
from ... utils.scene import getFPS
from ... base_types import AnimationNode
from ... algorithms.interpolations import Linear
from ... data_structures cimport DoubleList, FloatList, BaseFalloff
from . interpolate_list_falloff import createIndexBasedFalloff, createFalloffBasedFalloff
from .. sound.sound_spectrum import reductionFunctionItems, reductionFunctions, isValidRange

typeItems = [
    ("AVERAGE", "Average", "", "FORCE_TURBULENCE", 0),
    ("SPECTRUM", "Spectrum", "", "RNDCURVE", 1)
]

spectrumFalloffTypeItems = [
    ("INDEX_FREQUENCY", "Index Frequency", "NONE", 0),
    ("FALLOFF_FREQUENCY", "Falloff Frequency", "NONE", 1)
]

indexFrequencyExtensionItems = [
    ("LOOP", "Loop", "", "NONE", 0),
    ("MIRROR", "Mirror", "", "NONE", 1),
    ("EXTEND", "Extend Last", "NONE", 2)
]

class SoundFalloffNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_SoundFalloffNode"
    bl_label = "Sound Falloff"
    errorHandlingType = "EXCEPTION"

    __annotations__ = {}

    __annotations__["type"] = EnumProperty(name = "Type", default = "SPECTRUM",
        items = typeItems, update = AnimationNode.refresh)
    __annotations__["spectrumFalloffType"] = EnumProperty(name = "Spectrum Falloff Type",
        default = "INDEX_FREQUENCY", items = spectrumFalloffTypeItems, update = AnimationNode.refresh)
    __annotations__["indexFrequencyExtensionType"] = EnumProperty(name = "Index Frequency Extension",
        default = "LOOP", items = indexFrequencyExtensionItems, update = AnimationNode.refresh)

    __annotations__["fadeLowToZero"] = BoolProperty(name = "Fade Low Frequencies to Zero", 
        default = False)
    __annotations__["fadeHighToZero"] = BoolProperty(name = "Fade High Frequencies to Zero",
        default = False)

    __annotations__["reductionFunction"] = EnumProperty(name = "Reduction Function", default = "MAX",
        description = "The function used to sample frequency bins", items = reductionFunctionItems)
    __annotations__["smoothingSamples"] = IntProperty(name = "Smoothing Samples", default = 10, min = 0,
        description = ("The number of frames computed to smooth the output."
        " High value corresponds to more accurate results but with higher execution time"))
    __annotations__["kaiserBeta"] = FloatProperty(name = "Kaiser Beta", default = 6, min = 0,
        description = ("Beta parameter of the Kaiser window function."
        " High value corresponds to higher main-lobe leaking and lower side-lobe leaking"))

    def create(self):
        self.newInput("Sound", "Sound", "sound")
        self.newInput("Float", "Frame", "frame")
        self.newInput("Float", "Attack", "attack", value = 0.005, minValue = 0, maxValue = 1)
        self.newInput("Float", "Release", "release", value = 0.6, minValue = 0, maxValue = 1)
        self.newInput("Float", "Amplitude", "amplitude", value = 10)
        self.newInput("Float", "Low", "low", value = 0, minValue = 0, maxValue = 1, hide = True)
        self.newInput("Float", "High", "high", value = 1, minValue = 0, maxValue = 1, hide = True)

        if self.type == "AVERAGE":
            self.newInput("Float", "Scale", "scale", value = 1, minValue = 0)
        elif self.type == "SPECTRUM":
            self.newInput("Integer", "Count", "count", value = 20, minValue = 1)
            self.newInput("Interpolation", "Interpolation", "interpolation",
                defaultDrawType = "PROPERTY_ONLY", category = "EXPONENTIAL",
                easeIn = True, easeOut = False, hide = True)
            if self.spectrumFalloffType == "INDEX_FREQUENCY":
                self.newInput("Float", "Length", "length", value = 20, minValue = 1)
                self.newInput("Float", "Offset", "offset")
            elif self.spectrumFalloffType == "FALLOFF_FREQUENCY":
                self.newInput("Falloff", "Falloff", "falloff")
        
        self.newInput("Scene", "Scene", "scene", hide = True)
        self.newOutput("Falloff", "Falloff", "outFalloff")

    def draw(self, layout):
        col = layout.column()
        col.prop(self, "type", text = "")
        if self.type == "SPECTRUM":
            col.prop(self, "spectrumFalloffType", text = "")
            if self.spectrumFalloffType == "INDEX_FREQUENCY":
                col.prop(self, "indexFrequencyExtensionType", text = "")

    def drawAdvanced(self, layout):
        col = layout.column(align = True)
        col.label(text = "Fade to zero:")
        col.prop(self, "fadeLowToZero", text = "Low Frequencies")
        col.prop(self, "fadeHighToZero", text = "High Frequencies")

        col = layout.column()
        col.prop(self, "reductionFunction", text = "")
        col.prop(self, "smoothingSamples")
        col.prop(self, "kaiserBeta")

    def getExecutionFunctionName(self):
        if self.type == "AVERAGE": return "execute_Average_IndexOffset"
        if self.spectrumFalloffType == "INDEX_FREQUENCY":
            return "execute_Spectrum_IndexFrequency"
        elif self.spectrumFalloffType == "FALLOFF_FREQUENCY":
            return "execute_Spectrum_FalloffFrequency"

    def execute_Average_IndexOffset(self, sound, frame, attack, release, amplitude,
        low, high, scale, scene):
        if len(sound.soundSequences) == 0: self.raiseErrorMessage("Empty sound!")
        if not isValidRange(low, high): self.raiseErrorMessage("Invalid interval!")

        return Average_Index_SoundFalloff(sound, frame, scale, attack, release, amplitude,
            low, high, getFPS(scene), self.smoothingSamples, self.kaiserBeta,
            reductionFunctions[self.reductionFunction])

    def execute_Spectrum_IndexFrequency(self, sound, frame, attack, release, amplitude,
        low, high, count, interpolation, length, offset, scene):
        type = self.indexFrequencyExtensionType
        frequencies = self.getFrequenciesAtFrame(sound, frame, attack, release, amplitude,
            low, high, count, interpolation, scene)
        return createIndexBasedFalloff(type, frequencies, length, offset, Linear())

    def execute_Spectrum_FalloffFrequency(self, sound, frame, attack, release, amplitude,
        low, high, count, interpolation, falloff, scene):
        frequencies = self.getFrequenciesAtFrame(sound, frame, attack, release, amplitude,
            low, high, count, interpolation, scene)
        return createFalloffBasedFalloff(falloff, frequencies, Linear())

    def getFrequenciesAtFrame(self, sound, frame, attack, release, amplitude, low, high,
        count, interpolation, scene):
        if len(sound.soundSequences) == 0: self.raiseErrorMessage("Empty sound!")
        if not isValidRange(low, high): self.raiseErrorMessage("Invalid interval!")
        if count < 1: self.raiseErrorMessage("Invalid count!")

        spectrum = sound.computeTimeSmoothedSpectrum(frame / getFPS(scene),
            (frame + 1) / getFPS(scene), attack, release, self.smoothingSamples, self.kaiserBeta)
        maxFrequency = len(spectrum) - 1

        pins = interpolation.evaluateList(DoubleList.fromNumpyArray(numpy.linspace(
            low, high, num = count - self.fadeLowToZero - self.fadeHighToZero + 1)))

        bins = FloatList(count)
        reductionFunction = reductionFunctions[self.reductionFunction]
        for i in range(len(pins) - 1):
            x, y = int(pins[i] * maxFrequency), int(pins[i + 1] * maxFrequency)
            if x == y: y = x + 1
            bins[i + self.fadeLowToZero] = reductionFunction(spectrum[x:y]) * amplitude

        if self.fadeLowToZero: bins[0] = 0
        if self.fadeHighToZero: bins[len(bins) - 1] = 0
        return bins

cdef class Average_Index_SoundFalloff(BaseFalloff):
    cdef:
        int fps, smoothingSamples
        object sound, reductionFunction
        float frame, scale, attack, release, amplitude, low, high, kaiserBeta

    def __cinit__(self, object sound, float frame, float scale,
        float attack, float release, float amplitude, float low, float high,
        int fps, int smoothingSamples, float kaiserBeta, object reductionFunction):
        self.sound = sound
        self.frame = frame
        self.scale = scale
        self.attack = attack
        self.release = release
        self.amplitude = amplitude
        self.low = low
        self.high = high
        self.fps = fps
        self.smoothingSamples = smoothingSamples
        self.kaiserBeta = kaiserBeta
        self.reductionFunction = reductionFunction
        self.dataType = "NONE"
        self.clamped = False

    cdef float evaluate(self, void *object, Py_ssize_t index):
        spectrum = self.sound.computeTimeSmoothedSpectrum(
            (self.frame - index * self.scale) / self.fps,
            (self.frame + 1 - index * self.scale) / self.fps,
            self.attack, self.release, self.smoothingSamples, self.kaiserBeta)
        cdef int maxFrequency = len(spectrum) - 1

        return self.reductionFunction(
            spectrum[int(self.low * maxFrequency):int(self.high * maxFrequency)]) * self.amplitude
