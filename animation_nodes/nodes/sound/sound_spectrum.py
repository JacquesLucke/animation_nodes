import bpy
import numpy
from bpy.props import *
from math import log, ceil, expm1
from ... base_types import AnimationNode
from ... data_structures import DoubleList

samplingItems = [
    ("EXP", "Exponential", "", "", 0),
    ("CUSTOM", "Custom", "", "", 1),
    ("SINGLE", "Single", "", "", 2)
]
windowItems = [
    ("HANNING", "Hanning", "", "", 0),
    ("HAMMING", "Hamming", "", "", 1),
    ("BLACKMAN", "Blackman", "", "", 2),
    ("BARTLETT", "Bartlett", "", "", 3)
]
windowFunctions = {
    "HANNING": numpy.hanning, "HAMMING": numpy.hamming,
    "BLACKMAN": numpy.blackman, "BARTLETT": numpy.bartlett
}

class SoundSpectrumNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_SoundSpectrumNode"
    bl_label = "Sound Spectrum"

    smoothingSamples: IntProperty(name = "Smoothing Samples", default = 5)
    window: EnumProperty(name = "Window", default = "HANNING", items = windowItems)

    samplingMethod: EnumProperty(name = "Sampling Method", default = "EXP", items = samplingItems,
        update = AnimationNode.refresh)

    def create(self):
        self.newInput("Generic", "Buffer", "buffer")
        self.newInput("Float", "Frame", "frame")
        self.newInput("Float", "Attack", "attack", value = 0.005, minValue = 0, maxValue = 1)
        self.newInput("Float", "Release", "release", value = 0.6, minValue = 0, maxValue = 1)

        if self.samplingMethod == "EXP":
            self.newInput("Integer", "Count", "count", value = 20, minValue = 2)
            self.newInput("Float", "Low", "low", value = 0, minValue = 0, maxValue = 1)
            self.newInput("Float", "High", "high", value = 1, minValue = 0, maxValue = 1)
            self.newInput("Float", "K", "k", value = 5, minValue = 0.00001)
        elif self.samplingMethod == "CUSTOM":
            self.newInput("Float List", "Pins", "pins")
        elif self.samplingMethod == "SINGLE":
            self.newInput("Float", "Low", "low", value = 0, minValue = 0, maxValue = 1)
            self.newInput("Float", "High", "high", value = 0.1, minValue = 0, maxValue = 1)

        self.newInput("Scene", "Scene", "scene", hide = True)

        if self.samplingMethod in ("EXP", "CUSTOM"):
            self.newOutput("Float List", "Spectrum", "spectrum")
        else:
            self.newOutput("Float", "Spectrum", "spectrum")

    def draw(self, layout):
        layout.prop(self, "samplingMethod", text = "")

    def drawAdvanced(self, layout):
        layout.prop(self, "smoothingSamples")
        layout.prop(self, "window", text = "")

    def getExecutionFunctionName(self):
        if self.samplingMethod == "EXP": return "executeExponential"
        elif self.samplingMethod == "CUSTOM": return "executeCustom"
        elif self.samplingMethod == "SINGLE": return "executeSingle"

    def executeExponential(self, buffer, frame, attack, release, count, low, high, k, scene):
        if low >= high: return DoubleList.fromValue(0, length = count)
        nyquist, FFT = self.computeFFT(buffer, frame, scene.render.fps, 44100, attack, release)
        bars = DoubleList(count)
        scale = expm1(k) / (high - low)
        pins = [low + expm1(k * i / count) / scale for i in range(count + 1)]
        for i in range(count):
            x, y = int(pins[i] * nyquist), int(pins[i + 1] * nyquist)
            if x == y: y = x + 1
            bars[i] = numpy.mean(FFT[x:y])
        return bars

    def executeSingle(self, buffer, frame, attack, release, low, high, scene):
        if low >= high: return 0
        nyquist, FFT = self.computeFFT(buffer, frame, scene.render.fps, 44100, attack, release)
        return numpy.mean(FFT[int(low * nyquist):int(high * nyquist)])

    def executeCustom(self, buffer, frame, attack, release, pins, scene):
        if len(pins) < 3: return DoubleList.fromValue(0, length = len(pins) - 1)
        nyquist, FFT = self.computeFFT(buffer, frame, scene.render.fps, 44100, attack, release)
        bars = DoubleList(len(pins) - 1)
        for i in range(len(pins) - 1):
            x, y = int(pins[i] * nyquist), int(pins[i + 1] * nyquist)
            if x == y: y = x + 1
            bars[i] = numpy.mean(FFT[x:y])
        return bars

    def computeFFT(self, buffer, frame, fps, sampleRate, attack, release):
        FFT = None
        chunkSize = max(sampleRate // fps, 512)
        chunk = numpy.zeros(2**ceil(log(chunkSize, 2)))
        window = windowFunctions[self.window](chunkSize)
        for i in range(min(self.smoothingSamples, int(frame)), -1, -1):
            chunkStart = int((frame - i) * chunkSize)
            chunk[:chunkSize] = buffer[chunkStart:chunkStart + chunkSize] * window
            newFFT = numpy.abs(numpy.fft.rfft(chunk)) / chunkSize * 2
            if FFT is None:
                FFT = newFFT
            else:
                factor = numpy.array((attack, release))[(newFFT < FFT).astype(int)]
                FFT = FFT * factor + newFFT * (1 - factor)
        return len(FFT) - 1, FFT
