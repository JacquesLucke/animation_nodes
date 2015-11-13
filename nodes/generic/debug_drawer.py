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

    maxRows = IntProperty(name = "Max Rows", default = 150, min = 0)
    fontSize = IntProperty(name = "Font Size", default = 100, min = 10, max = 1000)
    maxListElements = IntProperty(name = "Max List Elements", default = 15, min = 0)
    oneElementPerLine = BoolProperty(name = "One Element per Line", default = True)
    showIndices = BoolProperty(name = "Show Indices", default = True)

    def create(self):
        self.width = 320
        self.inputs.new("an_GenericSocket", "Data", "data")

    def draw(self, layout):
        layout.prop(self, "fontSize")
        if isList(self.dataType):
            layout.prop(self, "maxListElements")
            layout.prop(self, "oneElementPerLine")
            if self.oneElementPerLine:
                layout.prop(self, "showIndices")

    def drawAdvanced(self, layout):
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

    def getExecutionCode(self):
        if isList(self.dataType):
            yield "conversionFunction = self.getCurrentToStringFunction()"
            yield "self.store_GenericList(data, conversionFunction)"
        else:
            yield "self.store_Generic(data)"

    def store_Generic(self, data):
        self.debugText = str(data)

    def store_GenericList(self, data, elementToStringFunction = str):
        useSlicedList = len(data) > self.maxListElements
        elements = data[:self.maxListElements]

        text = "List Length: {}\n\n".format(len(data))

        separator = "\n" if self.oneElementPerLine else ", "
        indicesWidth = len(str(len(elements))) + 2
        if self.showIndices: text += separator.join("{}: ".format(i).rjust(indicesWidth) + elementToStringFunction(e) for i, e in enumerate(elements))
        else: text += separator.join(elementToStringFunction(e) for e in elements)
        if useSlicedList: text += separator + "..."

        self.debugText = text

    @property
    def debugText(self):
        return dataByNode[self.identifier]

    @debugText.setter
    def debugText(self, text):
        dataByNode[self.identifier] = text

    @property
    def dataType(self):
        return self.inputs[0].dataType

    def getCurrentToStringFunction(self):
        dataType = self.dataType
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
