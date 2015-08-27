import bpy
from .. events import treeChanged

class TagRetryExecution(bpy.types.Operator):
    bl_idname = "an.tag_retry_execution"
    bl_label = "Tag retry execution"
    bl_description = "Rebuild internal node structures and check for problems again"

    def execute(self, context):
        treeChanged()
        return {"FINISHED"}
