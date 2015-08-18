import bpy
from bpy.props import *
from ... base_types.node import AnimationNode
from ... tree_info import getDirectOriginSocket
from ... sockets.info import getBaseDataTypeItems, toListIdName

class CombineLists(bpy.types.Node, AnimationNode):
    bl_idname = "an_combine_lists_node"
    bl_label = "Combine Lists"

    @property
    def inputNames(self):
        return { socket.identifier : "list_" + str(i) for i, socket in enumerate(self.inputs) }

    outputNames = { "List" : "list" }

    def assignedTypeChanged(self, context):
        self.listIdName = toListIdName(self.assignedType)
        self.recreateSockets()

    selectedType = EnumProperty(name = "Type", items = getBaseDataTypeItems)
    assignedType = StringProperty(update = assignedTypeChanged)

    listIdName = StringProperty()

    def create(self):
        self.selectedType = "Float"
        self.assignedType = "Float"

    def draw(self, layout):
        self.callFunctionFromUI(layout, "newInputSocket",
            text = "New Input",
            description = "Create a new input socket",
            icon = "PLUS")

    def draw_buttons_ext(self, context, layout):
        layout.prop(self, "selectedType")
        self.callFunctionFromUI(layout, "assignSelectedListType",
            text = "Assign",
            description = "Remove all sockets and set the selected socket type")

    def getExecutionCode(self):
        lines = []
        lines.append("$list$ = []")
        for i, socket in self.inputs:
            if socket.name == "...": continue
            lines.append("$list$.extend(%{}%)".format("list_" + str(i)))
        return "\n".join(lines)

    def edit(self):
        emptySocket = self.inputs["..."]
        origin = getDirectOriginSocket(emptySocket)
        if origin is None: return
        socket = self.newInputSocket()
        self.id_data.links.new(socket, origin)
        emptySocket.removeConnectedLinks()

    def assignSelectedListType(self):
        self.assignedType = self.selectedType

    def recreateSockets(self, inputAmount = 2):
        self.inputs.clear()
        self.outputs.clear()

        self.inputs.new("an_EmptySocket", "...").passiveType = self.listIdName
        for _ in range(inputAmount):
            self.newInputSocket()
        self.outputs.new(self.listIdName, "List")

    def newInputSocket(self):
        socket = self.inputs.new(self.listIdName, self.getNotUsedSocketName("List"))
        socket.nameSettings.display = True
        socket.customName = "List"
        socket.removeable = True
        socket.moveable = True
        if hasattr(socket, "showName"):
            socket.showName = False
        socket.moveUp()
        return socket
