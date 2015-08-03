import bpy
from ... old_utils import *

class an_NewPropertyListNode(bpy.types.Operator):
    bl_idname = "an.new_property_to_list_node"
    bl_label = "New String Property to String List Node"
    
    nodeTreeName = bpy.props.StringProperty()
    nodeName = bpy.props.StringProperty()
    
    def execute(self, context):
        node = getNode(self.nodeTreeName, self.nodeName)
        node.addItemToList()
        return {'FINISHED'}
        
class an_RemovePropertyFromListNode(bpy.types.Operator):
    bl_idname = "an.remove_property_from_list_node"
    bl_label = "Remove String Property from String List Node"
    
    nodeTreeName = bpy.props.StringProperty()
    nodeName = bpy.props.StringProperty()
    index = bpy.props.IntProperty()
    
    def execute(self, context):
        node = getNode(self.nodeTreeName, self.nodeName)
        node.removeItemFromList(self.index)
        return {'FINISHED'}
