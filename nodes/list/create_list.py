import bpy
from bpy.props import *
from ... base_types.node import AnimationNode
from ... utils.selection import getSortedSelectedObjectNames
from ... sockets.info import getBaseDataTypeItems, toIdName, toListIdName

class CreateList(bpy.types.Node, AnimationNode):
    bl_idname = "an_CreateList"
    bl_label = "Create List"

    def assignedTypeChanged(self, context):
        baseDataType = self.assignedType
        self.baseIdName = toIdName(baseDataType)
        self.listIdName = toListIdName(self.baseIdName)
        self.recreateSockets()

    selectedType = EnumProperty(name = "Type", items = getBaseDataTypeItems)
    assignedType = StringProperty(update = assignedTypeChanged)
    baseIdName = StringProperty()
    listIdName = StringProperty()

    def hideStatusChanged(self, context):
        for socket in self.inputs:
            socket.hide = self.hideInputs

    hideInputs = BoolProperty(name = "Hide Inputs", default = False, update = hideStatusChanged)

    def create(self):
        self.selectedType = "Float"
        self.assignedType = "Float"

    def draw(self, layout):
        self.functionOperator(layout, "newInputSocket",
            text = "New Input",
            description = "Create a new input socket",
            icon = "PLUS")

    def drawAdvanced(self, layout):
        col = layout.column(align = True)
        col.prop(self, "selectedType", text = "")
        self.functionOperator(col, "assignSelectedListType",
            text = "Assign",
            description = "Remove all sockets and set the selected socket type")

        layout.prop(self, "hideInputs")

        self.drawTypeSpecificButtonsExt(layout)

    @property
    def inputNames(self):
        return { socket.identifier : "element_" + str(i) for i, socket in enumerate(self.inputs) }

    def getExecutionCode(self):
        return "outList = [" + ", ".join(["element_" + str(i) for i, socket in enumerate(self.inputs) if socket.dataType != "Empty"]) + "]"

    def edit(self):
        emptySocket = self.inputs["..."]
        origin = emptySocket.directOriginSocket
        if origin is None: return
        socket = self.newInputSocket()
        socket.linkWith(origin)
        emptySocket.removeConnectedLinks()

    def assignSelectedListType(self):
        self.assignedType = self.selectedType

    def assignListType(self, idName, inputAmount = 2):
        self.assignedType = idName
        self.recreateSockets(inputAmount)

    def recreateSockets(self, inputAmount = 2):
        self.inputs.clear()
        self.outputs.clear()

        self.inputs.new("an_EmptySocket", "...").passiveType = self.listIdName
        for i in range(inputAmount):
            self.newInputSocket()
        self.outputs.new(self.listIdName, "List", "outList")

    def newInputSocket(self):
        socket = self.inputs.new(self.baseIdName, "Element")
        socket.displayCustomName = True
        socket.customName = "Element"
        socket.removeable = True
        socket.moveable = True
        if hasattr(socket, "showName"):
            socket.showName = False
        socket.moveUp()
        return socket


    # type specific stuff
    #############################

    def drawTypeSpecificButtonsExt(self, layout):
        if self.assignedType == "Object":
            self.functionOperator(layout, "createInputsFromSelection", text = "From Selection", icon = "PLUS")

    def createInputsFromSelection(self):
        names = getSortedSelectedObjectNames()
        for name in names:
            socket = self.newInputSocket()
            socket.objectName = name
