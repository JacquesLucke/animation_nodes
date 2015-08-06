import bpy
from bpy.props import *
from ... base_types.node import AnimationNode
from ... utils.nodes import getNotUsedSocketName
from ... utils.selection import getSortedSelectedObjectNames
from ... sockets.info import getBaseDataTypeItems, toIdName, toListIdName
from ... tree_info import getOriginSocket, getDirectOriginSocket

class CreateList(bpy.types.Node, AnimationNode):
    bl_idname = "an_CreateList"
    bl_label = "Create List"

    @property
    def inputNames(self):
        return { socket.identifier : "element_" + str(i) for i, socket in enumerate(self.inputs) }

    outputNames = { "List" : "list" }

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

    def draw_buttons(self, context, layout):
        self.callFunctionFromUI(layout, "newInputSocket",
            text = "New Input",
            description = "Create a new input socket",
            icon = "PLUS")

    def draw_buttons_ext(self, context, layout):
        col = layout.column(align = True)
        col.prop(self, "selectedType", text = "")
        self.callFunctionFromUI(col, "assignSelectedListType",
            text = "Assign",
            description = "Remove all sockets and set the selected socket type")

        layout.prop(self, "hideInputs")

        self.drawTypeSpecificButtonsExt(layout)

    def getExecutionCode(self):
        return "$list$ = [" + ", ".join(["%element_{}%".format(i) for i, socket in enumerate(self.inputs) if socket.dataType != "Empty"]) + "]"

    def edit(self):
        emptySocket = self.inputs["..."]
        directOrigin = getDirectOriginSocket(emptySocket)
        if directOrigin is None: return
        socket = self.newInputSocket()
        self.id_data.links.new(socket, directOrigin)
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
        self.outputs.new(self.listIdName, "List")

    def newInputSocket(self):
        socket = self.inputs.new(self.baseIdName, getNotUsedSocketName(self, "Element"))
        socket.nameSettings.display = True
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
            self.callFunctionFromUI(layout, "createInputsFromSelection", text = "From Selection", icon = "PLUS")

    def createInputsFromSelection(self):
        names = getSortedSelectedObjectNames()
        for name in names:
            socket = self.newInputSocket()
            socket.objectName = name
