import bpy
from bpy.props import *
from .. events import treeChanged
from .. utils.recursion import noRecursion
from .. utils.nodes import iterAnimationNodes
from .. import tree_info

treeUpdated = False

class AnimationNodeTree(bpy.types.NodeTree):
    bl_idname = "an_AnimationNodeTree"
    bl_label = "Animation";
    bl_icon = "ACTION"

    def update(self):
        global treeUpdated
        treeUpdated = True

        update()
        treeChanged()

@noRecursion
def update():
    updateAllNodes()
    updateDataIfNecessary()

def updateAllNodes():
    global treeUpdated
    for node in iterAnimationNodes():
        updateDataIfNecessary()
        node.edit()

def updateDataIfNecessary():
    global treeUpdated
    if treeUpdated:
        tree_info.update()
        treeUpdated = False
