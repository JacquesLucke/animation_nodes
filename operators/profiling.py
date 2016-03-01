import bpy
import cProfile
from io import StringIO
from .. update import updateEverything
from contextlib import redirect_stdout
from .. preferences import getDeveloperSettings

class PrintProfileExecutionResult(bpy.types.Operator):
    bl_idname = "an.print_profile_execution_result"
    bl_label = "Print Profile Execution Result"
    bl_description = ""

    @classmethod
    def poll(cls, context):
        try: return context.space_data.edit_tree.bl_idname == "an_AnimationNodeTree"
        except: return False

    def execute(self, context):
        result = getExecutionProfilingResult()
        print(result)
        return {"FINISHED"}

class WriteProfileExecutionResult(bpy.types.Operator):
    bl_idname = "an.write_profile_execution_result"
    bl_label = "Write Profile Execution Result"
    bl_description = ""

    @classmethod
    def poll(cls, context):
        try: return context.space_data.edit_tree.bl_idname == "an_AnimationNodeTree"
        except: return False

    def execute(self, context):
        result = getExecutionProfilingResult()

        textBlockName = "Profiling"
        textBlock = bpy.data.texts.get(textBlockName)
        if textBlock is None: textBlock = bpy.data.texts.new(textBlockName)

        textBlock.clear()
        textBlock.write(result)
        return {"FINISHED"}

def getExecutionProfilingResult():
    sortMode = getDeveloperSettings().profilingSortMode
    f = StringIO()
    with redirect_stdout(f):
        d = {"context" : bpy.context}
        cProfile.runctx("context.space_data.edit_tree.execute()", d, d, sort = sortMode)
    return f.getvalue()
