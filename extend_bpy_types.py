import bpy
from . operators.callbacks import executeCallback

def register():
    bpy.types.Context.isAnimationNodeTreeActive = isAnimationNodeTreeActive
    bpy.types.Operator.an_executeCallback = _executeCallback

def unregister():
    del bpy.types.Context.isAnimationNodeTreeActive
    del bpy.types.Context.an_executeCallback

def isAnimationNodeTreeActive(context):
    if context.area.type == "NODE_EDITOR":
        tree = context.space_data.node_tree
        if tree is not None:
            return tree.bl_idname == "an_AnimationNodeTree"
    return False

def _executeCallback(operator, callback, *args, **kwargs):
    executeCallback(callback, *args, **kwargs)
