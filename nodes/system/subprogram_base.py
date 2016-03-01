from bpy.props import *
from ... import preferences
from ... events import networkChanged
from ... ui.node_colors import colorNetworks
from ... algorithms.random import getRandomColor

class SubprogramBaseNode:
    isSubprogramNode = True

    subprogramName = StringProperty(name = "Subprogram Name", default = "Subprogram",
        description = "Subprogram name to identify this group elsewhere",
        update = networkChanged)

    subprogramDescription = StringProperty(name = "Subprogram Description", default = "",
        description = "Short description about what this subprogram does",
        update = networkChanged)

    def networkColorChanged(self, context):
        colorNetworks()

    networkColor = FloatVectorProperty(name = "Network Color",
        default = [0.5, 0.5, 0.5], subtype = "COLOR",
        soft_min = 0.0, soft_max = 1.0,
        update = networkColorChanged)

    def randomizeNetworkColor(self):
        colors = preferences.nodeColors()
        value = colors.subprogramValue
        saturation = colors.subprogramSaturation
        self.networkColor = getRandomColor(value = value, saturation = saturation)
