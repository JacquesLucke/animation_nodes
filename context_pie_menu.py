import bpy
from bpy.props import *
from . old_utils import getNode
from . sockets.info import toDataType

'''
                ###############

    #########                      Second active node suggestion

 Data Input                               First active node suggestion

    #########                      All other active node suggestions

                  Debug Node

How to implement suggestions on a per node basis:
1. Create a 'getNextNodeSuggestions(self)' function inside the node
2. Return a list that looks like this:
    [("an_FloatMathNode", (0, 0)),                      # First suggestion
     ("an_CombineVector", (0, 0)),                      # Second suggestion
     ("an_FloatClamp", (0, 0)),                         # ... can be an unlimited amount of suggestions
     ("an_CombineVector", (0, 0), (0, 1), (0, 2))]      # the tuples indicate which sockets to connect: (output index, input index)
'''

class ContextPie(bpy.types.Menu):
    bl_idname = "an.context_pie"
    bl_label = "Context Pie"

    @classmethod
    def poll(cls, context):
        return animationNodeTreeActive()

    def drawLeft(self, context, layout):
        if activeNodeHasInputs():
            layout.operator("an.insert_data_input_node", text = "Data Input")
        else:
            self.empty(layout)

    def drawRight(self, context, layout):
        if len(self.activeNodeSuggestions) > 0:
            self.drawInsertNodeOperator(layout, self.activeNodeSuggestions[0])
        else:
            self.empty(layout)

    def drawBottom(self, context, layout):
        if activeNodeHasOutputs():
            layout.operator("an.insert_debug_node", text = "Debug")
        else:
            self.empty(layout)

    def drawTop(self, context, layout):
        self.empty(layout)

    def drawTopLeft(self, context, layout):
        self.empty(layout)

    def drawTopRight(self, context, layout):
        if len(self.activeNodeSuggestions) > 1:
            self.drawInsertNodeOperator(layout, self.activeNodeSuggestions[1])
        else:
            self.empty(layout)

    def drawBottomLeft(self, context, layout):
        self.empty(layout)

    def drawBottomRight(self, context, layout):
        amount = len(self.activeNodeSuggestions)
        if amount == 3:
            self.drawInsertNodeOperator(layout, self.activeNodeSuggestions[2])
        elif amount > 3:
            col = layout.column()
            for suggestion in self.activeNodeSuggestions[2:]:
                self.drawInsertNodeOperator(col, suggestion)
        else:
            self.empty(layout)


    def draw(self, context):
        self.prepare(context)

        pie = self.layout.menu_pie()
        self.drawLeft(context, pie)
        self.drawRight(context, pie)
        self.drawBottom(context, pie)
        self.drawTop(context, pie)
        self.drawTopLeft(context, pie)
        self.drawTopRight(context, pie)
        self.drawBottomLeft(context, pie)
        self.drawBottomRight(context, pie)

    def prepare(self, context):
        node = context.active_node
        try: self.activeNodeSuggestions = node.getNextNodeSuggestions()
        except: self.activeNodeSuggestions = []

    def empty(self, layout):
        layout.row().label("")

    def drawInsertNodeOperator(self, layout, data):
        nodeIdName = data[0]
        links = data[1:]

        props = layout.operator("an.insert_linked_node", text = getNodeNameFromIdName(nodeIdName))
        props.nodeType = nodeIdName
        for origin, target in links:
            item = props.links.add()
            item.origin = origin
            item.target = target


class InsertDebugNode(bpy.types.Operator):
    bl_idname = "an.insert_debug_node"
    bl_label = "Insert Debug Node"
    bl_description = ""
    bl_options = {"REGISTER"}

    socketIndex = IntProperty(default = 0)
    nodeTreeName = StringProperty()
    nodeName = StringProperty()

    @classmethod
    def poll(cls, context):
        return activeNodeHasOutputs() and animationNodeTreeActive()

    def invoke(self, context, event):
        storeCursorLocation(event)
        node = context.active_node
        bpy.ops.an.choose_socket_and_execute_operator("INVOKE_DEFAULT",
            operatorName = "an.insert_debug_node",
            nodeTreeName = node.id_data.name,
            nodeName = node.name,
            chooseOutputSocket = True)
        return {"FINISHED"}

    def execute(self, context):
        nodeTree = getActiveAnimationNodeTree()
        originNode = getNode(self.nodeTreeName, self.nodeName)
        node = insertNode("an_DebugOutputNode")
        nodeTree.links.new(node.inputs[0], originNode.outputs[self.socketIndex])
        moveNode(node)
        return{"FINISHED"}


class InsertDataInputNode(bpy.types.Operator):
    bl_idname = "an.insert_data_input_node"
    bl_label = "Insert Data Input Node"
    bl_description = ""
    bl_options = {"REGISTER"}

    socketIndex = IntProperty(default = 0)
    nodeTreeName = StringProperty()
    nodeName = StringProperty()

    @classmethod
    def poll(cls, context):
        return activeNodeHasInputs() and animationNodeTreeActive()

    def invoke(self, context, event):
        storeCursorLocation(event)
        node = context.active_node
        bpy.ops.an.choose_socket_and_execute_operator("INVOKE_DEFAULT",
            operatorName = "an.insert_data_input_node",
            nodeTreeName = node.id_data.name,
            nodeName = node.name,
            chooseOutputSocket = False)
        return {"FINISHED"}

    def execute(self, context):
        nodeTree = getActiveAnimationNodeTree()
        targetNode = getNode(self.nodeTreeName, self.nodeName)
        targetSocket = targetNode.inputs[self.socketIndex]
        data = targetSocket.getStoreableValue()

        node = insertNode("an_DataInput")
        node.assignSocketType(toDataType(targetSocket.bl_idname))
        node.inputs[0].setStoreableValue(data)

        nodeTree.links.new(targetSocket, node.outputs[0])
        moveNode(node)
        return{"FINISHED"}


class ChooseSocketAndExecuteOperator(bpy.types.Operator):
    bl_idname = "an.choose_socket_and_execute_operator"
    bl_label = "Choose Socket and Execute Operator"
    bl_description = ""
    bl_options = {"REGISTER"}

    operatorName = StringProperty()
    nodeTreeName = StringProperty()
    nodeName = StringProperty()
    chooseOutputSocket = BoolProperty()

    def invoke(self, context, event):
        node = getNode(self.nodeTreeName, self.nodeName)
        sockets = node.outputs if self.chooseOutputSocket else node.inputs
        amount = len(sockets)
        if amount == 1:
            exec("bpy.ops.{}('EXEC_DEFAULT', socketIndex = 0, nodeTreeName = {}, nodeName = {})".format(self.operatorName, repr(self.nodeTreeName), repr(self.nodeName)))
        elif amount >= 2:
            context.window_manager.popup_menu(self.drawSocketChooser, title = "Choose Socket")
        return {"FINISHED"}

    def drawSocketChooser(self, menu, context):
        node = getNode(self.nodeTreeName, self.nodeName)
        sockets = node.outputs if self.chooseOutputSocket else node.inputs

        col = menu.layout.column()
        col.operator_context = "EXEC_DEFAULT"
        for i, socket in enumerate(sockets):
            if not socket.hide:
                props = col.operator(self.operatorName, text = socket.getDisplayedName())
                props.socketIndex = i
                props.nodeTreeName = self.nodeTreeName
                props.nodeName = self.nodeName


class LinkedIndices(bpy.types.PropertyGroup):
    origin = IntProperty(default = 0)
    target = IntProperty(default = 0)

class InsertLinkedNode(bpy.types.Operator):
    bl_idname = "an.insert_linked_node"
    bl_label = "Insert Linked Node"
    bl_description = ""
    bl_options = {"REGISTER"}

    nodeType = StringProperty(default = "")
    links = CollectionProperty(type = LinkedIndices)

    @classmethod
    def poll(cls, context):
        return activeNodeHasOutputs() and animationNodeTreeActive()

    def invoke(self, context, event):
        storeCursorLocation(event)

        nodeTree = getActiveAnimationNodeTree()
        originNode = getActiveNode()
        node = insertNode(self.nodeType)
        for item in self.links:
            nodeTree.links.new(node.inputs[item.target], originNode.outputs[item.origin])

        moveNode(node)
        return{"FINISHED"}


def insertNode(type):
    space = bpy.context.space_data
    nodeTree = space.node_tree
    node = nodeTree.nodes.new(type)
    node.location = space.cursor_location
    return node

def moveNode(node):
    onlySelect(node)
    bpy.ops.transform.translate("INVOKE_DEFAULT")

def storeCursorLocation(event):
    space = bpy.context.space_data
    nodeTree = space.node_tree
    space.cursor_location_from_region(event.mouse_region_x, event.mouse_region_y)

def onlySelect(node):
    bpy.ops.node.select_all(action = "DESELECT")
    node.select = True
    node.id_data.nodes.active = node


def getNodeNameFromIdName(idName):
    try: return getattr(bpy.types, idName).bl_label
    except: return ""


def activeNodeHasOutputs():
    if not activeNodeExists(): return False
    node = getActiveNode()
    return len(node.outputs) > 0

def activeNodeHasInputs():
    if not activeNodeExists(): return False
    node = getActiveNode()
    return len(node.inputs) > 0

def activeNodeExists():
    try: return getActiveNode() is not None
    except: return False

def getActiveNode():
    return getattr(bpy.context, "active_node", None)

def animationNodeTreeActive():
    try: return getActiveAnimationNodeTree() is not None
    except: return False

def getActiveAnimationNodeTree():
    try:
        nodeTree = bpy.context.space_data.edit_tree
        if nodeTree.bl_idname == "an_AnimationNodeTree": return nodeTree
    except: pass
    return None
