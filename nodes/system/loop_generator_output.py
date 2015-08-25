import bpy
from bpy.props import *
from ... events import treeChanged
from . utils import updateCallerNodes
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
        updateCallerNodes()

    def nameChanged(self, context):
        self.label = self.outputName
        updateCallerNodes()

    def loopInputIdentifierChanged(self, context):
        updateCallerNodes()
        treeChanged()

    listDataType = StringProperty(update = dataTypeChanged)
    addType = EnumProperty(name = "Add Type", items = addTypeItems, update = dataTypeChanged)

    outputName = StringProperty(name = "Generator Name", update = nameChanged)
    loopInputIdentifier = StringProperty(update = loopInputIdentifierChanged)
    removed = BoolProperty(default = False)
    sortIndex = IntProperty(default = 0)

    def create(self):
        self.listDataType = "Vector List"
        self.outputName = "Generator Name"
        self.sortIndex = id(self)

    def draw(self, layout):
        node = self.loopInputNode
        if node: layout.label(node.subprogramName, icon = "GROUP_VERTEX")

    def drawAdvanced(self, layout):
        layout.prop(self, "outputName", text = "Name")
        layout.prop(self, "addType")
        self.functionOperator(layout, "chooseNewGeneratorType", text = "Change Type", icon = "TRIA_RIGHT")

    def chooseNewGeneratorType(self):
        self.chooseSocketDataType("setListDataType", socketGroup = "LIST")

    def setListDataType(self, dataType):
        self.listDataType = dataType

    @keepNodeLinks
    def generateSockets(self):
        self.inputs.clear()

        socket = self.inputs.new("an_BooleanSocket", "Enabled", "enabled")
        socket.value = True
        socket.hide = True

        if self.addType == "APPEND": dataType = toBaseDataType(self.listDataType)
        elif self.addType == "EXTEND": dataType = self.listDataType
        socket = self.inputs.new(toIdName(dataType), dataType, "input")
        socket.display.nameOnly = True

    def delete(self):
        self.removed = True
        updateCallerNodes()

    @property
    def loopInputNode(self):
        try: return getNodeByIdentifier(self.loopInputIdentifier)
        except: return None

    @property
    def enabledSocket(self):
        return self.inputs[0]

    @property
    def addSocket(self):
        return self.inputs[1]
