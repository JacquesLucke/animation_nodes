import bpy
from bpy.props import *
from ... tree_info import keepNodeLinks
from ... tree_info import getNodesByType
from ... graphics.text_box import TextBox
from ... base_types.node import AnimationNode
from ... utils.timing import measureTime

dataByNode = {}

class DebugDrawerNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_DebugDrawerNode"
    bl_label = "Debug Drawer"

    fontSize = IntProperty(name = "Font Size", default = 100, min = 10, max = 1000)
    maxRows = IntProperty(name = "Max Rows", default = 15, min = 0)

    def create(self):
        self.width = 320
        self.inputs.new("an_GenericSocket", "Data", "data")

    def draw(self, layout):
        layout.prop(self, "fontSize")
        layout.prop(self, "maxRows")

    def edit(self):
        origin = self.inputs[0].dataOrigin
        targetIdName = getattr(origin, "bl_idname", "an_GenericSocket")
        if targetIdName != self.inputs[0].bl_idname:
            self.updateInputSocket(targetIdName)

    @keepNodeLinks
    def updateInputSocket(self, targetIdName):
        self.inputs.clear()
        self.inputs.new(targetIdName, "Data", "data")

    def execute(self, data):
        dataByNode[self.identifier] = self.inputs[0].toDebugString(data, self.maxRows)


def drawDebugTextBoxes():
    nodes = getNodesByType("an_DebugDrawerNode")
    nodesInCurrentTree = getattr(bpy.context.space_data.node_tree, "nodes", [])
    for node in nodes:
        if node.name in nodesInCurrentTree:
            drawDebugTextBox(node)

def drawDebugTextBox(node):
    data = dataByNode.get(node.identifier, None)
    if data is None: return

    region = bpy.context.region
    leftBottom = node.getRegionBottomLeft(region)
    rightBottom = node.getRegionBottomRight(region)
    width = rightBottom.x - leftBottom.x

    textBox = TextBox(data, leftBottom, width,
                      fontSize = width / node.dimensions.x * node.fontSize,
                      maxRows = node.maxRows)
    textBox.draw()
