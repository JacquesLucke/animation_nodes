import bpy
from bpy.props import *
from .. events import treeChanged
from .. mn_execution import allowCompiling, forbidCompiling
#from .. tree.current_tree

class AnimationNodeTree(bpy.types.NodeTree):
    bl_idname = "mn_AnimationNodeTree"
    bl_label = "Animation";
    bl_icon = "ACTION"
    
    isUpdating = BoolProperty(default = False)
    
    editDeepness = IntProperty(default = 0)
    editsCounter = IntProperty(default = 0)
    
    def startEdit(self):
        if self.editDeepness == 0:
            self.editsCounter = 0
            forbidCompiling()
        self.editDeepness += 1
        
    def stopEdit(self):
        self.editDeepness -= 1
        if self.editDeepness > 0: return
        allowCompiling()
        if self.editsCounter > 0:
            treeChanged()
            
    @property
    def isInEditState(self):
        return self.editDeepness > 0
    
    def update(self):
        if self.isInEditState:
            self.editsCounter += 1
            return
            
        treeChanged()
        return
        
        
        if not self.isUpdating:
            self.isUpdating = True
            self.updateTree()
            self.isUpdating = False
            
    def updateTree(self):
        updateTreeInfo()
        updateNodes(treeInfo)
        createNetworkScripts(treeInfo)