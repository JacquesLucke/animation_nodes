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
    nodesInCurrentTree = getattr(bpy.context.space_data.node_tree, "nodes", [])
    for node in nodes:
        if node.name in nodesInCurrentTree:
            drawNodePreview(node)

def drawNodePreview(node):
    interpolation = interpolationByNode.get(node.identifier, None)
    if interpolation is None: return

    region = bpy.context.region
    leftBottom = node.getRegionBottomLeft(region)
    rightBottom = node.getRegionBottomRight(region)
    width = rightBottom.x - leftBottom.x

    preview = InterpolationPreview(interpolation, leftBottom, width, node.resolution)
    preview.calculateBoundaries()
    preview.draw()
