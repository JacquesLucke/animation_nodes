import bpy
import cProfile
from bpy.props import *
from io import StringIO
from .. update import updateEverything
from contextlib import redirect_stdout
from .. preferences import getDeveloperSettings, getProfilingSortMode

profilingTargetFunctionItems = [
    ("EXECUTION", "Execution", ""),
    ("TREE_ANALYSIS", "Tree Analysis", ""),
    ("UPDATE_EVERYTHING", "Update Everything", ""),
    ("SCRIPT_GENERATION", "Script Generation", "")]

outputTypeItems = [
    ("CONSOLE", "Console", ""),
    ("TEXT_BLOCK", "Text Block", "")]

sortTypeItems = [
    ("cumtime", "Cumulative Time", ""),
    ("ncalls", "Call Amount", "")]

class ProfileAnimationNodes(bpy.types.Operator):
    bl_idname = "an.profile"
    bl_label = "Profile"

    targetFunction = EnumProperty(name = "Target", items = profilingTargetFunctionItems)
    output = EnumProperty(name = "Output", items = outputTypeItems)
    sort = EnumProperty(name = "Sort", items = sortTypeItems)

    def execute(self, context):
        if self.targetFunction == "EXECUTION":
            result = profileTreeExecution()
        elif self.targetFunction == "TREE_ANALYSIS":
            result = profileTreeAnalysis()
        elif self.targetFunction == "UPDATE_EVERYTHING":
            result = profileUpdateEverything()
        elif self.targetFunction == "SCRIPT_GENERATION":
            result = profileScriptGeneration()

        if self.output == "CONSOLE":
            print(result)
        elif self.output == "TEXT_BLOCK":
            textBlock = self.getOutputTextBlock()
            textBlock.clear()
            textBlock.write(result)

    def getOutputTextBlock(self):
        textBlockName = "Profiling"
        if textBlockName in bpy.data.texts:
            return bpy.data.texts[textBlockName]
        else:
            return bpy.data.texts.new(textBlockName)


class PrintProfileExecutionResult(bpy.types.Operator):
    bl_idname = "an.print_profile_execution_result"
    bl_label = "Print Profile Execution Result"
    bl_description = ""

    @classmethod
    def poll(cls, context):
        try: return context.space_data.edit_tree.bl_idname == "an_AnimationNodeTree"
        except: return False

    def execute(self, context):
        result = profileTreeExecution()
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

def returnProfilingResult(function):
    def profilingWrapper(*args, **kwargs):
        resultBuffer = StringIO()
        with redirect_stdout(resultBuffer):
            d = {"function" : function,
                 "args" : args,
                 "kwargs" : kwargs}
            cProfile.runctx("function(*args, **kwargs)", d, d, sort = getProfilingSortMode())
        return resultBuffer.getvalue()
    return profilingWrapper

@returnProfilingResult
def profileTreeExecution():
    bpy.context.space_data.edit_tree.execute()

@returnProfilingResult
def profileTreeAnalysis():
    from .. import tree_info
    tree_info.update()

@returnProfilingResult
def profileUpdateEverything():
    from .. import update
    update.updateEverything()

@returnProfilingResult
def profileScriptGeneration():
    from .. execution import units
    units.createExecutionUnits()
