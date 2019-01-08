import bpy
import numpy
from bpy.props import *
from ... data_structures import DoubleList
from ... base_types import AnimationNode, VectorizedSocket

reductionItems = [
    ("MEAN", "Mean", "", "", 0),
    ("MAX", "Max", "", "", 1)
]
reductionFunctions = {
    "MEAN" : numpy.mean,
    "MAX" : numpy.max
}

class SoundIntensityNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_SoundIntensityNode"
    bl_label = "Sound Intensity"

    smoothingSamples: IntProperty(name = "Smoothing Samples", default = 5, min = 0)
    reductionFunction: EnumProperty(name = "Reduction Function", default = "MAX",
        items = reductionItems)

    useFloatList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput("Sound", "Sound", "sound")
        self.newInput(VectorizedSocket("Float", "useFloatList",
            ("Frame", "frame"), ("Frames", "frame")))
        self.newInput("Float", "Attack", "attack", value = 0.005, minValue = 0, maxValue = 1)
        self.newInput("Float", "Release", "release", value = 0.6, minValue = 0, maxValue = 1)
        self.newInput("Scene", "Scene", "scene", hide = True)

        self.newOutput(VectorizedSocket("Float", "useFloatList",
            ("Intensity", "intensity"), ("Intensities", "intensities")))

    def drawAdvanced(self, layout):
        layout.prop(self, "reductionFunction", text = "")
        layout.prop(self, "smoothingSamples")

    def getExecutionFunctionName(self):
        if self.useFloatList: return "executeMultiple"
        else: return "executeSingle"

    def executeSingle(self, sound, frame, attack, release, scene):
        fps = scene.render.fps
        return sound.computeTimeSmoothedIntensity(frame / fps, (frame + 1) / fps,
            attack, release, self.smoothingSamples, reductionFunctions[self.reductionFunction])

    def executeMultiple(self, sound, frames, attack, release, scene):
        fps = scene.render.fps
        intensities = DoubleList(len(frames))
        for i, frame in enumerate(frames):
            intensities[i] = sound.computeTimeSmoothedIntensity(frame / fps, (frame + 1) / fps,
                attack, release, self.smoothingSamples, reductionFunctions[self.reductionFunction])
        return intensities
