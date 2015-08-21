import bpy
from bpy.props import *
from ... base_types.node import AnimationNode
from ... tree_info import getSubprogramNetworks, getNodeByIdentifier, getNetworkByIdentifier
from ... utils.enum_items import enumItemsFromDicts
from ... sockets.info import toDataType
from ... execution.units import getSubprogramUnitByIdentifier

class SubprogramCaller(bpy.types.Node, AnimationNode):
    bl_idname = "an_SubprogramCaller"
    bl_label = "Subprogram Caller"

    def subprogramIdentifierChanged(self, context):
        self.updateSockets()

    subprogramIdentifier = StringProperty(name = "Subprogram Identifier", default = "", update = subprogramIdentifierChanged)

    @property
    def inputNames(self):
        return { socket.identifier : "input_" + str(i) for i, socket in enumerate(self.inputs)}

    @property
    def outputNames(self):
        return { socket.identifier : "output_" + str(i) for i, socket in enumerate(self.outputs)}

    def getExecutionCode(self):
        if self.subprogramNode is None: return ""

        parameterString = ", ".join(["input_" + str(i) for i in range(len(self.inputs))])
        outputString = ", ".join(["output_" + str(i) for i in range(len(self.outputs))])

        if outputString == "": return "_subprogram{}({})".format(self.subprogramIdentifier, parameterString)
        return "{} = _subprogram{}({})".format(outputString, self.subprogramIdentifier, parameterString)

    def draw(self, layout):
        networks = getSubprogramNetworks()
        network = self.subprogramNetwork

        layout.separator()
        col = layout.column()
        col.scale_y = 1.6
        if len(networks) == 0:
            self.functionOperator(col, "createNewGroup", text = "Group", icon = "PLUS")
        else:
            text, icon = (network.name, "GROUP_VERTEX") if network else ("Choose", "TRIA_RIGHT")
            props = col.operator("an.change_subprogram", text = text, icon = icon)
            props.nodeIdentifier = self.identifier
        layout.separator()

    def updateSockets(self):
        subprogram = self.subprogramNode
        if subprogram is None: self.clearSockets()
        else: subprogram.getSocketData().apply(self)

    @property
    def subprogramNode(self):
        try: return getNodeByIdentifier(self.subprogramIdentifier)
        except: return None

    @property
    def subprogramNetwork(self):
        return getNetworkByIdentifier(self.subprogramIdentifier)

    def createNewGroup(self):
        bpy.ops.node.add_and_link_node(type = "an_GroupInput")
        inputNode = self.nodeTree.nodes[-1]
        inputNode.location.x -= 200
        inputNode.location.y += 40
        self.subprogramIdentifier = inputNode.identifier
        bpy.ops.node.add_and_link_node(type = "an_GroupOutput")
        outputNode = self.nodeTree.nodes[-1]
        outputNode.location.x += 60
        outputNode.location.y += 40
        outputNode.groupInputIdentifier = inputNode.identifier
        inputNode.select = True
        bpy.ops.node.translate_attach("INVOKE_DEFAULT")


@enumItemsFromDicts
def getSubprogramItems(self, context):
    itemDict = []
    for network in getSubprogramNetworks():
        itemDict.append({
            "id" : network.identifier,
            "name" : network.name,
            "description" : network.description})
    return itemDict

class ChangeSubprogram(bpy.types.Operator):
    bl_idname = "an.change_subprogram"
    bl_label = "Change Subprogram"
    bl_description = "Change Subprogram"

    nodeIdentifier = StringProperty()
    subprogram = EnumProperty(name = "Subprogram", items = getSubprogramItems)

    @classmethod
    def poll(cls, context):
        networks = getSubprogramNetworks()
        return len(networks) > 0

    def invoke(self, context, event):
        node = getNodeByIdentifier(self.nodeIdentifier)
        try: self.subprogram = node.subprogramIdentifier
        except: pass # when the old subprogram identifier doesn't exist
        return context.window_manager.invoke_props_dialog(self, width = 400)

    def check(self, context):
        return True

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "subprogram", expand = self.expandSubprograms)

        network = getNetworkByIdentifier(self.subprogram)
        if network:
            layout.label("Desription: " + network.description)
            layout.separator()
            socketData = network.groupInputNode.getSocketData()

            col = layout.column()
            col.label("Inputs:")
            self.drawSockets(col, socketData.inputs)

            col = layout.column()
            col.label("Outputs:")
            self.drawSockets(col, socketData.outputs)

    def drawSockets(self, layout, sockets):
        col = layout.column(align = True)
        for data in sockets:
            row = col.row()
            row.label(" "*8 + data.customName)
            row.label("<  {}  >".format(toDataType(data.idName)))

    @property
    def expandSubprograms(self):
        networks = getSubprogramNetworks()
        names = "".join([network.name for network in networks])
        return len(names) < 40

    def execute(self, context):
        node = getNodeByIdentifier(self.nodeIdentifier)
        node.subprogramIdentifier = self.subprogram
        return {"FINISHED"}
