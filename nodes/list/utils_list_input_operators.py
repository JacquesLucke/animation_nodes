import bpy
from bpy.props import *
from ... utils.nodes import getNode

class an_RemovePropertyFromListNode(bpy.types.Operator):
    bl_idname = "an.remove_property_from_list_node"
    bl_label = "Remove String Property from String List Node"

    nodeTreeName = StringProperty()
    nodeName = StringProperty()
    index = IntProperty()

    def execute(self, context):
        node = getNode(self.nodeTreeName, self.nodeName)
        node.removeItemFromList(self.index)
        return {'FINISHED'}
