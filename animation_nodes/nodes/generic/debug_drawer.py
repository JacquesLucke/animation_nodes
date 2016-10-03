import bpy
import itertools
from bpy.props import *
from ... utils import pretty_strings
from ... draw_handler import drawHandler
from ... graphics.text_box import TextBox
from ... base_types import AnimationNode, AutoSelectDataType

dataByNode = {}

class DebugDrawerNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_DebugDrawerNode"
    bl_label = "Debug Drawer"
    bl_width_default = 270
    options = {"NO_TIMING"}

    maxRows = IntProperty(name = "Max Rows", default = 150, min = 0)
    fontSize = IntProperty(name = "Font Size", default = 12, min = 1, max = 1000)
    maxListStartElements = IntProperty(name = "Max List Start Elements", default = 15, min = 0)
    maxListEndElements = IntProperty(name = "Max List End Elements", default = 0, min = 0)
    oneElementPerLine = BoolProperty(name = "One Element per Line", default = True)

    errorMessage = StringProperty()

    def create(self):
        self.newInput("Generic", "Data", "data")
        self.newInput("Boolean", "Condition", "condition", hide = True)

    def draw(self, layout):
        if self.errorMessage != "":
            layout.label(self.errorMessage, icon = "ERROR")

    def drawAdvanced(self, layout):
        layout.prop(self, "fontSize")
        layout.prop(self, "maxRows")

        col = layout.column(align = True)
        col.prop(self, "oneElementPerLine")
        row = col.row(align = True)
        row.prop(self, "maxListStartElements", text = "Begin")
        row.prop(self, "maxListEndElements", text = "End")

    def getExecutionCode(self):
        if "Condition" in self.inputs:
            yield "if condition:"
        else: yield "if True:"

        yield "    self.errorMessage = ''"
        yield "    if hasattr(data, '__iter__'):"
        yield "        conversionFunction = self.getCurrentToStringFunction()"
        yield "        self.store_GenericList(data, conversionFunction)"
        yield "    else:"
        yield "        self.store_Generic(data)"

    def store_Generic(self, data):
        self.debugText = str(data)

    def store_GenericList(self, data, toString = str):
        length = len(data)
        text = "List Length: {}\n\n".format(length)

        useSlicedList = length > self.maxListStartElements + self.maxListEndElements
        separator = "\n" if self.oneElementPerLine else ", "
        indicesWidth = len(str(length)) + 2

        if useSlicedList:
            startElements = data[:self.maxListStartElements]
            endElements = data[-self.maxListEndElements:] if self.maxListEndElements > 0 else []

            text += separator.join(self.formatElements(startElements, 0, indicesWidth, toString))
            text += separator + "..."
            if len(endElements) > 0: text += "\n"
            text += separator.join(self.formatElements(endElements, length - len(endElements), indicesWidth, toString))
        else:
            elements = data
            text += separator.join(self.formatElements(elements, 0, indicesWidth, toString))

        self.debugText = text

    def formatElements(self, elements, startIndex, indicesWidth, toString):
        if self.oneElementPerLine:
            for index, element in zip(itertools.count(startIndex), elements):
                yield "{}: ".format(index).rjust(indicesWidth) + toString(element)
        else:
            for element in elements:
                yield toString(element)

    @property
    def debugText(self):
        return dataByNode[self.identifier]

    @debugText.setter
    def debugText(self, text):
        dataByNode[self.identifier] = text

    def getCurrentToStringFunction(self):
        dataType = self.inputs[0].getCurrentDataType()
        if dataType == "Vector List": return pretty_strings.formatVector
        if dataType == "Euler List": return pretty_strings.formatEuler
        if dataType == "Float List": return pretty_strings.formatFloat
        if dataType == "Quaternion List": return pretty_strings.formatQuaternion
        return str


@drawHandler("SpaceNodeEditor", "WINDOW")
def drawDebugTextBoxes():
    tree = bpy.context.space_data.node_tree
    if tree is None: return
    if tree.bl_idname != "an_AnimationNodeTree": return

    for node in tree.nodes:
        if node.bl_idname == "an_DebugDrawerNode" and not node.hide and node.errorMessage == "":
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
