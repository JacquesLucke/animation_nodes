import bpy
from bpy.props import *
from ... base_types.node import AnimationNode
from ... sockets.info import toIdName, toBaseDataType
from ... tree_info import keepNodeLinks, getNodeByIdentifier

addTypeItems = [
    ("APPEND", "Append", "Add one element to the output list", "NONE", 0),
    ("EXTEND", "Extend", "Add a custom amount of elements to the output list", "NONE", 1) ]

class LoopGeneratorOutput(bpy.types.Node, AnimationNode):
    bl_idname = "an_LoopGeneratorOutput"
    bl_label = "Loop Generator Output"

    def dataTypeChanged(self, context):
        self.generateSockets()

    def nameChanged(self, context):
        self.label = self.outputName

    listDataType = StringProperty(update = dataTypeChanged)
    addType = EnumProperty(name = "Add Type", items = addTypeItems, update = dataTypeChanged)
    outputName = StringProperty(name = "Generator Name", update = nameChanged)
    loopInputIdentifier = StringProperty()

    def create(self):
        self.listDataType = "Vector List"
        self.outputName = "Generator Name"

    def draw(self, layout):
        node = self.loopInputNode
        if node:
            layout.label(node.subprogramName, icon = "GROUP_VERTEX")

    def drawAdvanced(self, layout):
        layout.prop(self, "outputName", text = "Name")
        layout.prop(self, "addType")
        self.functionOperator(layout, "chooseNewGeneratorType", text = "Change Type")

    def chooseNewGeneratorType(self):
        self.chooseSocketDataType("setListDataType", socketGroup = "LIST")

    def setListDataType(self, dataType):
        self.listDataType = dataType

    @keepNodeLinks
    def generateSockets(self):
        self.inputs.clear()

        socket = self.inputs.new("an_BooleanSocket", "Activate")
        socket.value = True
        socket.hide = True

        if self.addType == "APPEND": dataType = toBaseDataType(self.listDataType)
        elif self.addType == "EXTEND": dataType = self.listDataType
        socket = self.inputs.new(toIdName(dataType), dataType)
        socket.display.nameOnly = True

    @property
    def loopInputNode(self):
        try: return getNodeByIdentifier(self.loopInputIdentifier)
        except: return None
