import bpy
from bpy.props import *
from ... utils.names import toInterfaceName
from ... events import propertyChanged

from . wrapper import (
    PyNoise,
    noiseTypesList,
    perturbTypesList,
    fractalTypesList,
    cellularReturnTypesList,
    cellularDistanceFunctionsList
)

def pretty(identifier):
    return toInterfaceName(identifier).title()

noiseTypeItems = [(t, pretty(t), "") for t in noiseTypesList]
cellularReturnTypeItems = [(t, pretty(t), "") for t in cellularReturnTypesList]
distanceFunctionItems = [(t, pretty(t), "") for t in cellularDistanceFunctionsList]
perturbTypeItems = [(t, pretty(t), "") for t in perturbTypesList]
fractalTypeItems = [(t, pretty(t), "") for t in fractalTypesList]

class Noise3DNodeBase:
    def _runRefresh(self, context):
        self.updateNoiseSocketsHideStatus()
        propertyChanged()

    noiseType = EnumProperty(name = "Noise Type", default = "SIMPLEX",
        items = noiseTypeItems, update = _runRefresh)

    cellularReturnType = EnumProperty(name = "Cellular Return Type", default = "CELL_VALUE",
        items = cellularReturnTypeItems, update = _runRefresh)

    cellularLookupType = EnumProperty(name = "Cellular Lookup Type", default = "SIMPLEX",
        items = noiseTypeItems, update = _runRefresh)

    cellularDistanceFunction = EnumProperty(name = "Cellular Distance Function",
        default = "EUCLIDEAN", items = distanceFunctionItems,
        update = _runRefresh)

    perturbType = EnumProperty(name = "Perturb Type", default = "NONE",
        items = perturbTypeItems, update = _runRefresh)

    fractalType = EnumProperty(name = "Fractal Type", default = "FBM",
        items = fractalTypeItems, update = _runRefresh)

    def drawNoiseSettings(self, layout):
        layout.prop(self, "noiseType", text = "")
        if self.noiseType == "CELLULAR":
            layout.prop(self, "cellularReturnType", text = "")
            if self.cellularReturnType == "NOISE_LOOKUP":
                layout.prop(self, "cellularLookupType", text = "")

    def drawAdvancedNoiseSettings(self, layout):
        layout.prop(self, "fractalType")
        layout.prop(self, "perturbType")

        col = layout.column()
        col.active = self.noiseType == "CELLULAR" and "DISTANCE" in self.cellularReturnType
        col.prop(self, "cellularDistanceFunction", text = "Distance")

    def updateNoiseSocketsHideStatus(self):
        self.inputs["Jitter"].hide = self.noiseType != "CELLULAR"
        self.inputs["Lookup Frequency"].hide = self.noiseType != "CELLULAR"
        self.inputs["Octaves"].hide = self.noiseType in ("WHITE_NOISE", "CELLULAR")
        self.inputs["Perturb Frequency"].hide = self.perturbType == "NONE"
        self.inputs["Lookup Frequency"].hide = not (self.noiseType == "CELLULAR" and self.cellularReturnType == "NOISE_LOOKUP")

    def createSettingsInputs(self):
        self.newInput("Integer", "Seed", "seed")
        self.newInput("Float", "Frequency", "frequency", value = 0.1)
        self.newInput("Float", "Amplitude", "amplitude", value = 1)
        self.newInput("Vector", "Axis Scale", "axisScale", value = (1, 1, 1), hide = True)
        self.newInput("Vector", "Offset", "offset")
        self.newInput("Integer", "Octaves", "octaves", value = 3).setRange(1, 10)
        self.newInput("Float", "Jitter", "jitter", value = 0.45)
        self.newInput("Float", "Lookup Frequency", "lookupFrequency", value = 0.2)
        self.newInput("Float", "Perturb Frequency", "perturbFrequency", value = 0.1)
        self.updateNoiseSocketsHideStatus()

    def calculateNoise(self, vectors, seed, frequency, amplitude, axisScale, offset, octaves, jitter, lookupFrequency, perturbFrequency):
        noise = PyNoise()
        noise.setNoiseType(self.noiseType)
        noise.setFractalType(self.fractalType)
        noise.setPerturbType(self.perturbType)

        noise.setSeed(seed)
        noise.setFrequency(frequency)
        noise.setAxisScales(axisScale)
        noise.setOctaves(min(max(octaves, 1), 10))

        if self.perturbType != "NONE":
            noise.setPerturbFrequency(perturbFrequency)

        if self.noiseType == "CELLULAR":
            noise.setCellularReturnType(self.cellularReturnType)
            noise.setCellularNoiseLookupType(self.cellularLookupType)
            noise.setCellularDistanceFunction(self.cellularDistanceFunction)
            noise.setCellularJitter(jitter)
            noise.setCellularNoiseLookupFrequency(lookupFrequency)

        return noise.calculateList(vectors, amplitude, offset)
