import bpy
from bpy.props import *
from bpy.app.handlers import persistent
from . utils.mn_node_utils import getAnimationNodeTrees
from . mn_utils import getNode

deprecatedNodeIdNames = ["mn_TransfromVector", "mn_SubstringNode", "mn_ObjectKeyframeInput"]

brokenNodes = []

for i, name in enumerate(deprecatedNodeIdNames):
    class __DeprecatedNode(bpy.types.Node):
        bl_idname = name
        bl_label = "Deprecated"
    bpy.utils.register_class(__DeprecatedNode)

@persistent
def findAndUpdateBrokenNodes(scene):
    global brokenNodes
    
    brokenNodes = []
    
    for node in iterateAnimationNodes():
        if node.bl_idname in deprecatedNodeIdNames:
            brokenNodes.append((node.id_data.name, node.name))
        else:
            if hasattr(node, "updateOlderNode"):
                node.updateOlderNode()
                
                
def iterateAnimationNodes():
    for nodeTree in getAnimationNodeTrees():
        for node in nodeTree.nodes:
            yield node
            
            
def containsBrokenNodes():
    return len(brokenNodes) > 0
    
def getBrokenNodes():
    return brokenNodes
    
    
class FindBrokenNodes(bpy.types.Operator):
    bl_idname = "mn.find_broken_nodes"
    bl_label = "Find Broken Nodes"
    bl_description = ""

    def execute(self, context):
        findAndUpdateBrokenNodes(context.scene)
        return {'FINISHED'} 


class SelectAndViewNode(bpy.types.Operator):
    bl_idname = "mn.select_and_view_node"
    bl_label = "Select and View Node"
    bl_description = ""
    
    nodeTreeName = StringProperty()
    nodeName = StringProperty()

    def execute(self, context):
        node = getNode(self.nodeTreeName, self.nodeName)
        bpy.ops.node.select_all(action = "DESELECT")
        node.select = True
        context.space_data.node_tree = bpy.data.node_groups[self.nodeTreeName]
        bpy.ops.node.view_selected()
        return {'FINISHED'}
            
    
def register_handlers():    
    bpy.app.handlers.load_post.append(findAndUpdateBrokenNodes)
    
def unregister_handlers():
    bpy.app.handlers.load_post.remove(findAndUpdateBrokenNodes) 