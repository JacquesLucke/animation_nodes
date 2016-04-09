import bpy
from bpy.props import *
from .. events import propertyChanged
from .. base_types.socket import AnimationNodeSocket

class SceneListSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_SceneListSocket"
    bl_label = "Scene List Socket"
    dataType = "Scene List"
    allowedInputTypes = ["Scene List"]
    drawColor = (0.2, 0.3, 0.4, 0.5)
    storable = False
    comparable = False

    useGlobalScene = BoolProperty(name = "Use Global Scene", default = True,
        description = "Use the global scene for this node tree", update = propertyChanged)

    def drawProperty(self, layout, text):
        row = layout.row(align = True)
        if self.useGlobalScene:
            if text != "": text += ": "
            row.label(text + "[{}]".format(repr(self.nodeTree.scene.name)))
        else:
            if text is "": text = self.text
            row.label(text)
        row.prop(self, "useGlobalScene", icon = "WORLD", text = "")

    def getValue(self):
        return [self.nodeTree.scene]

    @classmethod
    def getCopyExpression(cls):
        return "value[:]"
