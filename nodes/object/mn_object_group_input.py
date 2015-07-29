import bpy
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged

class mn_ObjectGroupInput(bpy.types.Node, AnimationNode):
    bl_idname = "mn_ObjectGroupInput"
    bl_label = "Object Group Input"
    
    groupName = bpy.props.StringProperty(default = "", update = nodePropertyChanged)
    
    def init(self, context):
        self.outputs.new("mn_ObjectListSocket", "Objects")
        
    def draw_buttons(self, context, layout):
        layout.prop_search(self, "groupName", bpy.data, "groups", text = "")
        
    def getInputSocketNames(self):
        return {}
    def getOutputSocketNames(self):
        return {"Objects" : "objects"}
                
    def execute(self):
        group = bpy.data.groups.get(self.groupName)
        objects = []
        if group:
            objects = group.objects
        return objects
