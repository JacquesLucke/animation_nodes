import bpy
from . operators.callbacks import executeCallback

def register():
    bpy.types.Context.getActiveAnimationNodeTree = getActiveAnimationNodeTree
    bpy.types.Operator.an_executeCallback = _executeCallback

def unregister():
    del bpy.types.Context.getActiveAnimationNodeTree
    del bpy.types.Operator.an_executeCallback

def getActiveAnimationNodeTree(context):
    if context.area.type == "NODE_EDITOR":
        tree = context.space_data.node_tree
        if getattr(tree, "bl_idname", "") == "an_AnimationNodeTree":
            return tree

def _executeCallback(operator, callback, *args, **kwargs):
    executeCallback(callback, *args, **kwargs)
