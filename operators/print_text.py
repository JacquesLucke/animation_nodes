import bpy
from bpy.props import *

class PrintText(bpy.types.Operator):
    bl_idname = "an.print_text"
    bl_label = "Print Text"

    text = StringProperty(name = "Text")
    emptyLines = IntProperty()

    def execute(self, context):
        print("\n" * self.emptyLines)
        print(self.text)
        return {"CANCELLED"}
