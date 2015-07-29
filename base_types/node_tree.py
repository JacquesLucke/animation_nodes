import bpy
from bpy.props import *
from .. mn_execution import nodeTreeChanged
#from .. tree.current_tree

class AnimationNodeTree(bpy.types.NodeTree):
    bl_idname = "mn_AnimationNodeTree"
    bl_label = "Animation";
    bl_icon = "ACTION"
    
    isUpdating = BoolProperty(default = False)
    
    def update(self):
        nodeTreeChanged()
        return
        if not self.isUpdating:
            self.isUpdating = True
            self.updateTree()
            self.isUpdating = False
            
    def updateTree(self):
        updateTreeInfo()
        updateNodes(treeInfo)
        createNetworkScripts(treeInfo)