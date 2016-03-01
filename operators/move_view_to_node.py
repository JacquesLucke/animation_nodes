import bpy
from bpy.props import *
from .. tree_info import getNodeByIdentifier

class MoveViewToNode(bpy.types.Operator):
    bl_idname = "an.move_view_to_node"
    bl_label = "Move View to Node"
    bl_description = ""

    nodeIdentifier = StringProperty()

    @classmethod
    def poll(cls, context):
        try: return context.space_data.node_tree.bl_idname == "an_AnimationNodeTree"
        except: return False

    def execute(self, context):
        try: searchNode = getNodeByIdentifier(self.nodeIdentifier)
        except: return {"CANCELLED"}

        context.space_data.node_tree = searchNode.nodeTree
        for node in searchNode.nodeTree.nodes: node.select = False
        searchNode.select = True
        searchNode.nodeTree.nodes.active = searchNode

        bpy.ops.node.view_selected()
        return {"FINISHED"}
