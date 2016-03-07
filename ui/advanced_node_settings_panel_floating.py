import bpy

class FloatingAdvancedPanel(bpy.types.Operator):
    bl_idname = "an.floating_advanced_node_settings_panel"
    bl_label = "Advanced Node Settings"

    @classmethod
    def poll(cls, context):
        try: return context.active_node.isAnimationNode
        except: return False

    def check(self, context):
        return True

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width = 250)

    def draw(self, context):
        try: context.active_node.drawAdvanced(self.layout)
        except: pass

    def execute(self, context):
        return {"INTERFACE"}
