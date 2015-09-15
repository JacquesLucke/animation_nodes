import bpy
from bpy.props import *
from mathutils import Vector
from ... tree_info import getNodesByType
from ... base_types.node import AnimationNode
from ... algorithms.interpolation import sampleInterpolation
from ... graphics.interpolation_preview import InterpolationPreview

interpolationByNode = {}

class DebugInterpolationNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_DebugInterpolationNode"
    bl_label = "Debug Interpolation"

    resolution = IntProperty(name = "Resolution", min = 5, default = 40)

    def create(self):
        self.width = 160
        self.inputs.new("an_InterpolationSocket", "Interpolation", "interpolation").defaultDrawType = "PROPERTY_ONLY"

    def drawAdvanced(self, layout):
        layout.prop(self, "resolution")

    def execute(self, interpolation):
        interpolationByNode[self.identifier] = interpolation

def drawInterpolationPreviews():
    nodes = getNodesByType("an_DebugInterpolationNode")
    for node in nodes:
        drawNodePreview(node)

def drawNodePreview(node):
    interpolation = interpolationByNode.get(node.identifier, None)
    if interpolation is None: return

    leftBottom = convertViewToRegion(node.location.x, node.location.y - node.dimensions.y)
    rightBottom = convertViewToRegion(node.location.x + node.dimensions.x, node.location.y - node.dimensions.y)
    width = rightBottom.x - leftBottom.x

    preview = InterpolationPreview(interpolation, leftBottom, width, node.resolution)
    preview.calculateBoundaries()
    preview.draw()


def convertViewToRegion(x, y):
    factor = getDpiFactor()
    x *= factor
    y *= factor
    return Vector(bpy.context.region.view2d.view_to_region(x, y, clip = False))

def getDpiFactor():
    systemPreferences = bpy.context.user_preferences.system
    retinaFactor = getattr(systemPreferences, "pixel_size", 1)
    return systemPreferences.dpi * retinaFactor / 72
