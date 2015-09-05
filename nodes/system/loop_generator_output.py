import bpy
from bpy.props import *
from ... events import treeChanged
from . utils import subprogramInterfaceChanged
from ... base_types.node import AnimationNode
from ... sockets.info import toIdName, toBaseDataType
from ... tree_info import keepNodeLinks, getNodeByIdentifier

addTypeItems = [
    ("APPEND", "Append", "Add one element to the output list", "NONE", 0),
    ("EXTEND", "Extend", "Add a custom amount of elements to the output list", "NONE", 1) ]

class LoopGeneratorOutputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_LoopGeneratorOutputNode"
    bl_label = "Loop Generator Output"

    def dataTypeChanged(self, context):
        self.outputName = self.listDataType
        self.generateSockets()
        subprogramInterfaceChanged()

    def nameChanged(self, context):
        self.label = self.outputName
        subprogramInterfaceChanged()

    def loopInputIdentifierChanged(self, context):
        subprogramInterfaceChanged()
        treeChanged()

    listDataType = StringProperty(update = dataTypeChanged)
    addType = EnumProperty(name = "Add Type", items = addTypeItems, update = dataTypeChanged)

    outputName = StringProperty(name = "Generator Name", update = nameChanged)
    loopInputIdentifier = StringProperty(update = loopInputIdentifierChanged)
    removed = BoolProperty(default = False)
    sortIndex = IntProperty(default = 0)

    def create(self):
        self.listDataType = "Vector List"
        self.sortIndex = id(self)

    def draw(self, layout):
        node = self.loopInputNode
        if node: layout.label(node.subprogramName, icon = "GROUP_VERTEX")

    def drawAdvanced(self, layout):
        layout.prop(self, "outputName", text = "Name")
        layout.prop(self, "addType")
        self.invokeSocketTypeChooser(layout, "setListDataType", socketGroup = "LIST", text = "Change Type", icon = "TRIA_RIGHT")

    def edit(self):
        network = self.network
        if network.type != "Invalid": return
        if network.loopInAmount != 1: return
        loopInput = network.loopInputNode
        if self.loopInputIdentifier == loopInput.identifier: return
        self.loopInputIdentifier = loopInput.identifier

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
        socket.defaultDrawType = "TEXT_ONLY"

    def delete(self):
        self.removed = True
        subprogramInterfaceChanged()

    def duplicate(self, source):
        subprogramInterfaceChanged()

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
