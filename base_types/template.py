import bpy
from bpy.props import *
from mathutils import Vector
from .. tree_info import getNodeByIdentifier
from .. nodes.system import subprogram_sockets
from .. utils.nodes import newNodeAtCursor, invokeTranslation

class Template:
    bl_options = {"INTERNAL"}
    nodeOffset = (0, 0)

    @classmethod
    def poll(cls, context):
        try: return context.space_data.node_tree.bl_idname == "an_AnimationNodeTree"
        except: return False

    def invoke(self, context, event):
        if hasattr(self, "drawMenu"):
            return context.window_manager.invoke_props_dialog(self, width = 400)
        return self.execute(context)

    def draw(self, context):
        self.drawMenu(self.layout)

    def check(self, context):
        return True

    def execute(self, context):
        self.nodesToMove = []
        self.newNodes = []
        self.insert()
        self.offsetNewNodesPosition()
        self.moveInsertedNodes()
        return {"FINISHED"}

    def insert(self):
        pass

    def newNode(self, type, x = 0, y = 0, move = True, label = ""):
        node = self.nodeTree.nodes.new(type = type)
        node.location.x += x
        node.location.y += y
        node.label = label
        self.newNodes.append(node)
        if move: self.nodesToMove.append(node)
        return node

    def newLink(self, fromSocket, toSocket):
        self.nodeTree.links.new(toSocket, fromSocket)

    def nodeByIdentifier(self, identifier):
        try: return getNodeByIdentifier(identifier)
        except: return None

    def offsetNewNodesPosition(self):
        tempNode = newNodeAtCursor("an_DebugNode")
        offset = tempNode.location
        self.nodeTree.nodes.remove(tempNode)
        for node in self.newNodes:
            node.location += offset + Vector(self.nodeOffset)

    def moveInsertedNodes(self):
        for node in self.nodeTree.nodes:
            node.select = node in self.nodesToMove
        invokeTranslation()

    @property
    def nodeTree(self):
        return bpy.context.space_data.edit_tree

    @property
    def activeNode(self):
        return getattr(bpy.context, "active_node", None)

    def updateSubprograms(self):
        subprogram_sockets.updateIfNecessary()
