import bpy

def register():
    bpy.types.Context.isAnimationNodeTreeActive = isAnimationNodeTreeActive

def unregister():
    del bpy.types.Context.isAnimationNodeTreeActive

def isAnimationNodeTreeActive(context):
    if context.area.type == "NODE_EDITOR":
        tree = context.space_data.node_tree
        if tree is not None:
            return tree.bl_idname == "an_AnimationNodeTree"
    return False
