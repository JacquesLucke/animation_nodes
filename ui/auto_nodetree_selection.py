import bpy
from bpy.app.handlers import persistent
from .. utils.nodes import getAnimationNodeTrees

treeNameBySpace = {}

@persistent
def updateAutoNodeTreeSelection(scene):
    nodeTrees = getAnimationNodeTrees()
    if len(nodeTrees) == 0: return

    for space in getAnimationNodeEditorSpaces():
        spaceHash = str(hash(space))

        if space.node_tree is None:
            if len(nodeTrees) == 1:
                space.node_tree = nodeTrees[0]
            else:
                space.node_tree = bpy.data.node_groups.get(treeNameBySpace.get(spaceHash, None))

        treeName = getattr(space.node_tree, "name", None)
        if treeName is not None:
            treeNameBySpace[spaceHash] = treeName

def getAnimationNodeEditorSpaces():
    spaces = []
    for area in getattr(bpy.context.screen, "areas", []):
        if area.type == "NODE_EDITOR":
            space = area.spaces.active
            if space.tree_type == "an_AnimationNodeTree":
                spaces.append(space)
    return spaces



# Register
##################################

def registerHandlers():
    bpy.app.handlers.scene_update_post.append(updateAutoNodeTreeSelection)

def unregisterHandlers():
    bpy.app.handlers.scene_update_post.remove(updateAutoNodeTreeSelection)
