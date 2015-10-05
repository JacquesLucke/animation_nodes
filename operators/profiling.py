import bpy
import io
import cProfile
from .. update import updateEverything
from contextlib import redirect_stdout

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

class ProfileUpdating(bpy.types.Operator):
    bl_idname = "an.profile_updating"
    bl_label = "Profile Updating"
    bl_description = ""

    def execute(self, context):
        f = io.StringIO()
        with redirect_stdout(f):
            d = {"update" : updateEverything}
            cProfile.runctx("update()", d, d, sort = "cumtime")
        text = f.getvalue()
        lines = text.split("\n")
        outText = "\n".join([line for line in lines if "" in line])
        getTextBlock("Profile").from_string(outText)
        return {"FINISHED"}

def getTextBlock(name):
    text = bpy.data.texts.get(name)
    if text is None: text = bpy.data.texts.new(name)
    return text
