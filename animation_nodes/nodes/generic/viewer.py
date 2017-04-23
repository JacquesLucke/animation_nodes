import bpy
from bpy.props import *
from functools import lru_cache
from ... base_types import AnimationNode
from ... draw_handler import drawHandler
from ... graphics.text_box import TextBox

drawTextByIdentifier = {}

class ViewerNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ViewerNode"
    bl_label = "Viewer"

    maxRows = IntProperty(name = "Max Rows", default = 150, min = 0,
        description = "Max amount of lines visible in the floating text box.")
    fontSize = IntProperty(name = "Font Size", default = 12, min = 1, max = 1000)

    def create(self):
        self.newInput("Generic", "None", "data")

    def drawAdvanced(self, layout):
        col = layout.column(align = True)
        col.prop(self, "fontSize")
        col.prop(self, "maxRows")

    def execute(self, data):
        if handleDataAsList(data):
            self.handleListData(data)
        else:
            self.handleNonListData(data)

    def handleNonListData(self, data):
        function = getHandleNonListFunction(type(data))
        self.setViewData(*function(data))

    def handleListData(self, data):
        self.setViewData(type(data).__name__, "List")

    def setViewData(self, nodeText, drawText, minWidth = None):
        self.inputs[0].name = nodeText
        drawTextByIdentifier[self.identifier] = drawText

        if minWidth is not None:
            self.width = max(self.width, minWidth)

    def delete(self):
        if self.identifier in drawTextByIdentifier:
            del drawTextByIdentifier[self.identifier]


def handleDataAsList(data):
    if data is None:
        return False
    elif isinstance(data, str):
        return False
    elif hasattr(data, "__iter__") and hasattr(data, "__len__"):
        return True
    else:
        return False


# Non List Helpers
########################################

@lru_cache(maxsize = 1024)
def getHandleNonListFunction(cls):
    from mathutils import Vector, Matrix, Euler, Quaternion
    if cls is str:
        return handleNonList_String
    elif cls is float:
        return handleNonList_Float
    elif cls is int:
        return handleNonList_Integer
    elif cls is Vector:
        return handleNonList_Vector
    elif cls is Euler:
        return handleNonList_Euler
    elif cls is Matrix:
        return handleNonList_Matrix
    else:
        return handleNonList_Generic

def handleNonList_Generic(data):
    text = str(data)
    if len(text) < 20 and "\n" not in text:
        return text, ""
    else:
        return "Type: " + type(data).__name__, str(data)

def handleNonList_String(text):
    if len(text) < 20 and "\n" not in text:
        return text, ""
    else:
        return "Text Length: " + str(len(text)), text

def handleNonList_Float(number):
    return str(round(number, 5)), ""

def handleNonList_Integer(number):
    return str(number), ""

def handleNonList_Vector(vector):
    return str(vector), "", 260

def handleNonList_Euler(euler):
    return str(euler), "", 340

def handleNonList_Matrix(matrix):
    return "Type: {}x{} Matrix".format(len(matrix.row), len(matrix.col)), str(matrix), 330


# Drawing
##################################

@drawHandler("SpaceNodeEditor", "WINDOW")
def drawTextBoxes():
    tree = bpy.context.getActiveAnimationNodeTree()
    if tree is None:
        return

    for node in tree.nodes:
        if node.bl_idname == "an_ViewerNode" and not node.hide:
            drawTextBoxForNode(node)

def drawTextBoxForNode(node):
    text = drawTextByIdentifier.get(node.identifier, "")
    if text == "":
        return

    region = bpy.context.region
    leftBottom = node.getRegionBottomLeft(region)
    rightBottom = node.getRegionBottomRight(region)
    width = rightBottom.x - leftBottom.x

    textBox = TextBox(text, leftBottom, width,
                      fontSize = node.fontSize / node.dimensions.x * width,
                      maxRows = node.maxRows)
    textBox.draw()
