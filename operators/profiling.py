import bpy
import cProfile

class ProfileMainUnitExecution(bpy.types.Operator):
    bl_idname = "an.profile_main_unit_execution"
    bl_label = "Profile Main Unit Execution"
    bl_description = ""

    @classmethod
    def poll(cls, context):
        try: return context.space_data.edit_tree.bl_idname == "an_AnimationNodeTree"
        except: return False

    def execute(self, context):
        d = {"context" : context}
        cProfile.runctx("context.space_data.edit_tree.execute()", d, d, sort = "cumtime")
        return {"FINISHED"}
