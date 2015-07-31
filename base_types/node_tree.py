import bpy
from bpy.props import *
from .. events import treeChanged

class AnimationNodeTree(bpy.types.NodeTree):
    bl_idname = "mn_AnimationNodeTree"
    bl_label = "Animation";
    bl_icon = "ACTION"

    isUpdating = BoolProperty()

    def update(self):
        if self.isUpdating: return
        self.isUpdating = True

        updateAllNodes(self)
        treeChanged()

        self.isUpdating = False

def updateAllNodes(nodeTree):
    for node in nodeTree.nodes:
        if hasattr(node, "edit"): node.edit()
