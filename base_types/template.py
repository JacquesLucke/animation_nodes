import bpy
from bpy.props import *
from .. tree_info import getNodeByIdentifier

class Template:

    @classmethod
    def poll(cls, context):
        try: return context.space_data.node_tree.bl_idname == "an_AnimationNodeTree"
        except: return False

    def invoke(self, context, event):
        self.nodesToMove = []
        self.insert()
        self.moveInsertedNodes()
        return {"FINISHED"}

    def insert(self):
        pass

    def newNode(self, type, x = 0, y = 0, move = True):
        bpy.ops.node.add_and_link_node(type = type)
        node = self.nodeTree.nodes[-1]
        node.location.x += x
        node.location.y += y
        if move: self.nodesToMove.append(node)
        return node

    def nodeByIdentifier(self, identifier):
        try: return getNodeByIdentifier(identifier)
        except: return None

    def moveInsertedNodes(self):
        for node in self.nodeTree.nodes:
            node.select = node in self.nodesToMove
        bpy.ops.node.translate_attach("INVOKE_DEFAULT")

    @property
    def nodeTree(self):
        return bpy.context.space_data.edit_tree

    @property
    def activeNode(self):
        return getattr(bpy.context, "active_node", None)
