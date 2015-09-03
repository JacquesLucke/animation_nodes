import bpy
from bpy.props import *
from . an_operator import AnimationNodeOperator
from .. sockets.info import isBase, toListDataType
from .. node_creator import InsertNodesTemplate

class LoopifySocketProperties(bpy.types.PropertyGroup):
    useList = BoolProperty(default = True)

class Loopify(bpy.types.Operator, AnimationNodeOperator):
    bl_idname = "an.loopify"
    bl_label = "Loopify"
    bl_description = ""

    socketSettings = CollectionProperty(type = LoopifySocketProperties)

    def invoke(self, context, event):
        for socket in self.node.inputs:
            self.socketSettings.add()
        return context.window_manager.invoke_props_dialog(self, width = 200)

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        for i, socket in enumerate(self.node.inputs):
            if not isBase(socket.bl_idname): continue
            col.prop(self.socketSettings[i], "useList", text = socket.getDisplayedName())


    def execute(self, context):
        LoopifyTemplate(self.socketSettings)
        return {"FINISHED"}

    @property
    def node(self):
        return bpy.context.active_node


class LoopifyTemplate(InsertNodesTemplate):
    def insert(self, socketSettings):
        node = bpy.context.active_node
        replacedNode = node.nodeTree.nodes.new("an_InvokeSubprogramNode")
        replacedNode.location = node.location
        iterators = [socket for i, socket in enumerate(node.inputs) if socketSettings[i].useList]
        parameters = [socket for i, socket in enumerate(node.inputs) if not socketSettings[i].useList]
        for socket in node.sockets:
            socket.removeLinks()
        loopInput = self.newNode("an_LoopInputNode")
        for socket in iterators:
            iterator = loopInput.newIterator(toListDataType(socket.bl_idname), name = socket.getDisplayedName())
            iterator.linkWith(socket)
        for socket in parameters:
            parameter = loopInput.newParameter(socket.dataType, name = socket.getDisplayedName())
            parameter.linkWith(socket)
        for i, socket in enumerate(node.outputs):
            generatorNode = self.newNode("an_LoopGeneratorOutputNode", x = 500, y = -80 * i)
            generatorNode.loopInputIdentifier = loopInput.identifier
            generatorNode.listDataType = toListDataType(socket.bl_idname)
            generatorNode.outputName = socket.getDisplayedName() + " List "
            link = generatorNode.inputs[1].linkWith(socket)
            print(link.from_socket, link.to_socket)
        self.take(node)
        node.location.x = loopInput.location.x + 250
        node.location.y = loopInput.location.y
        replacedNode.subprogramIdentifier = loopInput.identifier
