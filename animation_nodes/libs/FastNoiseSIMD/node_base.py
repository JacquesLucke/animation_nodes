import bpy
from bpy.props import *
from ... utils.names import toInterfaceName

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
        self.refresh()

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
            layout.prop(self, "cellularLookupType", text = "")
            layout.prop(self, "cellularDistanceFunction", text = "")
        layout.prop(self, "perturbType", text = "")
        if "FRACTAL" in self.noiseType:
            layout.prop(self, "fractalType", text = "")

    def createSettingsInputs(self):
        self.newInput("Integer", "Seed", "seed")
        self.newInput("Float", "Frequency", "frequency", value = 0.1)
        self.newInput("Vector", "Axis Scale", "axisScale", value = (1, 1, 1))
        self.newInput("Float", "Perturb Frequency", "perturbFrequency", value = 0.1)
        self.newInput("Integer", "Octaves", "octaves", value = 3).setRange(1, 10)
        if self.noiseType == "CELLULAR":
            self.newInput("Float", "Jitter", "jitter", value = 0.45)
            self.newInput("Float", "Lookup Frequency", "lookupFrequency", value = 0.2)

    def calculateNoise(self, vectors, settings):
        noise = PyNoise()
        noise.setSeed(settings[0])
        noise.setFrequency(settings[1])
        noise.setAxisScales(*settings[2])
        noise.setNoiseType(self.noiseType)
        noise.setPerturbFrequency(settings[3])
        noise.setFractalType(self.fractalType)
        noise.setFractalOctaves(min(max(settings[4], 1), 10))
        if self.noiseType == "CELLULAR":
            noise.setCellularReturnType(self.cellularReturnType)
            noise.setCellularJitter(settings[5])
            noise.setCellularNoiseLookupType(self.cellularLookupType)
            noise.setCellularNoiseLookupFrequency(settings[6])
            noise.setCellularDistanceFunction(self.cellularDistanceFunction)
        noise.setPerturbType(self.perturbType)
        return noise.calculateList(vectors)
