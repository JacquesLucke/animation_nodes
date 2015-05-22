import bpy

class ContextPie(bpy.types.Menu):
    bl_idname = "mn.context_pie"
    bl_label = "Context Pie"
    
    def draw(self, context):
        pie = self.layout.menu_pie()
        
        
class InsertDebugNode(bpy.types.Operator):
    bl_idname = "mn.insert_debug_node"
    bl_label = "Insert Debug Node"
    bl_description = ""
    bl_options = {"REGISTER"}
    
    @classmethod
    def poll(cls, context):
        return True
    
    def execute(self, context):
        return {"FINISHED"}
                