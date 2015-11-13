import bpy
from bpy.props import *
from ... sockets.info import isList
from ... utils import pretty_strings
from ... tree_info import keepNodeLinks
from ... utils.timing import measureTime
from ... tree_info import getNodesByType
from ... graphics.text_box import TextBox
from ... base_types.node import AnimationNode

dataByNode = {}

class DebugDrawerNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_DebugDrawerNode"
    bl_label = "Debug Drawer"

    fontSize = IntProperty(name = "Font Size", default = 100, min = 10, max = 1000)
    maxRows = IntProperty(name = "Max Rows", default = 150, min = 0)
    maxListElements = IntProperty(name = "Max List Elements", default = 15, min = 0)
    oneElementPerLine = BoolProperty(name = "One Element per Line", default = True)

    def create(self):
        self.width = 320
        self.inputs.new("an_GenericSocket", "Data", "data")

    def draw(self, layout):
        layout.prop(self, "fontSize")
        layout.prop(self, "maxRows")
        layout.prop(self, "maxListElements")
        layout.prop(self, "oneElementPerLine")

    def edit(self):
        origin = self.inputs[0].dataOrigin
        targetIdName = getattr(origin, "bl_idname", "an_GenericSocket")
        if targetIdName != self.inputs[0].bl_idname:
            self.updateInputSocket(targetIdName)

    @keepNodeLinks
    def updateInputSocket(self, targetIdName):
        self.inputs.clear()
        self.inputs.new(targetIdName, "Data", "data")

    def getExecutionCode(self):
        dataType = self.inputs[0].dataType
        yield "conversionFunction = self.getCurrentToStringFunction()"
        if isList(dataType): yield "self.store_GenericList(data, conversionFunction)"
        else: yield "self.store_Generic(data)"

    def store_Generic(self, data):
        self.debugText = str(data)

    def store_GenericList(self, data, elementToStringFunction = str):
        useSlicedList = len(data) > self.maxListElements
        elements = data[:self.maxListElements]

        text = "List Length: {}\n\n".format(len(data))

        separator = "\n" if self.oneElementPerLine else ", "
        text += separator.join(elementToStringFunction(e) for e in elements)
        if useSlicedList: text += separator + "..."

        self.debugText = text

    @property
    def debugText(self):
        return dataByNode[self.identifier]

    @debugText.setter
    def debugText(self, text):
        dataByNode[self.identifier] = text

    def getCurrentToStringFunction(self):
        dataType = self.inputs[0].dataType
        if dataType == "Vector List": return pretty_strings.formatVector
        if dataType == "Euler List": return pretty_strings.formatEuler
        if dataType == "Float List": return pretty_strings.formatFloat
        if dataType == "Quaternion List": return pretty_strings.formatQuaternion
        return str

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
