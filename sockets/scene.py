import bpy
from bpy.props import *
from .. events import propertyChanged
from .. base_types.socket import AnimationNodeSocket

class SceneSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_SceneSocket"
    bl_label = "Scene Socket"
    dataType = "Scene"
    allowedInputTypes = ["Scene"]
    drawColor = (0.2, 0.3, 0.4, 1)
    storable = False
    comparable = True

    sceneName = StringProperty(name = "Scene", update = propertyChanged)
    useGlobalScene = BoolProperty(name = "Use Global Scene", default = True,
        description = "Use the global scene for this node tree", update = propertyChanged)

    def drawProperty(self, layout, text):
        row = layout.row(align = True)
        if self.useGlobalScene:
            if text != "": text += ": "
            row.label(text + repr(self.nodeTree.scene.name))
        else:
            row.prop_search(self, "sceneName",  bpy.data, "scenes", text = text)
        row.prop(self, "useGlobalScene", text = "", icon = "WORLD")

    def getValue(self):
        if self.useGlobalScene:
            return self.nodeTree.scene
        return bpy.data.scenes.get(self.sceneName)

    def setProperty(self, data):
        self.sceneName, self.useGlobalScene = data

    def getProperty(self):
        return self.sceneName, self.useGlobalScene
