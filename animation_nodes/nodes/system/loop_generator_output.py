import bpy
import random
from bpy.props import *
from ... events import treeChanged
from ... sockets.info import toBaseDataType
from ... base_types import AnimationNode
from . subprogram_sockets import subprogramInterfaceChanged
from ... tree_info import keepNodeLinks, getNodeByIdentifier

addTypeItems = [
    ("APPEND", "Append", "Add one element to the output list", "NONE", 0),
    ("EXTEND", "Extend", "Add a custom amount of elements to the output list", "NONE", 1) ]

class LoopGeneratorOutputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_LoopGeneratorOutputNode"
    bl_label = "Loop Generator Output"
    dynamicLabelType = "ALWAYS"

    def dataTypeChanged(self, context):
        self.outputName = self.listDataType
        self.generateSockets()
        subprogramInterfaceChanged()

    def nameChanged(self, context):
        subprogramInterfaceChanged()

    def loopInputIdentifierChanged(self, context):
        subprogramInterfaceChanged()
        treeChanged()

    listDataType = StringProperty(update = dataTypeChanged)
    addType = EnumProperty(name = "Add Type", items = addTypeItems, update = dataTypeChanged)

    outputName = StringProperty(name = "Generator Name", update = nameChanged)
    loopInputIdentifier = StringProperty(update = loopInputIdentifierChanged)
    sortIndex = IntProperty(default = 0)

    def setup(self):
        self.listDataType = "Vector List"
        self.sortIndex = getRandomInt()

    def draw(self, layout):
        node = self.loopInputNode
        if node: layout.label(node.subprogramName, icon = "GROUP_VERTEX")

    def drawAdvanced(self, layout):
        layout.prop(self, "outputName", text = "Name")
        layout.prop(self, "addType")
        self.invokeSocketTypeChooser(layout, "setListDataType",
            socketGroup = "LIST", text = "Change Type", icon = "TRIA_RIGHT")

    def drawLabel(self):
        return self.outputName

    def edit(self):
        network = self.network
        if network.type != "Invalid": return
        if network.loopInAmount != 1: return
        loopInput = network.getLoopInputNode()
        if self.loopInputIdentifier == loopInput.identifier: return
        self.loopInputIdentifier = loopInput.identifier

    def setListDataType(self, dataType):
        self.listDataType = dataType

    @keepNodeLinks
    def generateSockets(self):
        self.clearSockets()

        if self.addType == "APPEND": dataType = toBaseDataType(self.listDataType)
        elif self.addType == "EXTEND": dataType = self.listDataType

        self.newInput(dataType, dataType, "input", defaultDrawType = "TEXT_ONLY")
        self.newInput("Boolean", "Condition", "condition", value = True, hide = True)

    def delete(self):
        subprogramInterfaceChanged()

    def duplicate(self, source):
        self.sortIndex = getRandomInt()
        subprogramInterfaceChanged()

    def getTemplateCode(self):
        yield "self.loopInputIdentifier = #MISSING----------"
        yield "self.outputName = {}".format(repr(self.outputName))
        yield "self.listDataType = '{}'".format(self.listDataType)
        yield "self.addType = '{}'".format(self.addType)

    @property
    def loopInputNode(self):
        try: return getNodeByIdentifier(self.loopInputIdentifier)
        except: return None

    @property
    def conditionSocket(self):
        try: return self.inputs["Condition"]
        except: return self.inputs["Enabled"]

    @property
    def addSocket(self):
        for socket in self.inputs:
            if socket.name not in ("Condition", "Enabled"):
                return socket

def getRandomInt():
    random.seed()
    return int(random.random() * 10000) + 100
