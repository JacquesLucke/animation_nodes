import bpy
from bpy.props import *
from .. tree_info import getNodeByIdentifier

class ChoosePath(bpy.types.Operator):
    bl_idname = "an.choose_path"
    bl_label = "Choose Path"

    filepath = StringProperty(subtype = "FILE_PATH")
    nodeIdentifier = StringProperty()
    callback = StringProperty()

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        node = getNodeByIdentifier(self.nodeIdentifier)
        function = getattr(node, self.callback)
        function(self.filepath)
        return {"FINISHED"}
