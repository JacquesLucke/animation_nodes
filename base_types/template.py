import bpy
from bpy.props import *
from mathutils import Vector
from .. tree_info import getNodeByIdentifier
from .. nodes.system import subprogram_sockets
from .. utils.nodes import newNodeAtCursor, invokeTranslation

class Template:
    bl_options = {"INTERNAL"}
    nodeOffset = (0, 0)
    menuWidth = 400

    usedMenu = BoolProperty(default = False)

    @classmethod
    def poll(cls, context):
        try: return context.space_data.node_tree.bl_idname == "an_AnimationNodeTree"
        except: return False

    def invoke(self, context, event):
        if hasattr(self, "drawDialog"):
            return context.window_manager.invoke_props_dialog(self, width = self.menuWidth)
        if hasattr(self, "drawMenu") and getattr(self, "needsMenu", False):
            self.usedMenu = True
            context.window_manager.popup_menu(self.drawPopupMenu)
            return {"FINISHED"}
        self.usedMenu = False
        return self.execute(context)

    def draw(self, context):
        self.drawDialog(self.layout)

    def drawPopupMenu(self, menu, context):
        col = menu.layout.column()
        self.drawMenu(col)

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
