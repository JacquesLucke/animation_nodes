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
    hashable = True

    sceneName = StringProperty(name = "Scene", update = propertyChanged)
    useGlobalScene = BoolProperty(name = "Use Global Scene", default = True, update = propertyChanged)

    def drawProperty(self, layout, text):
        if self.useGlobalScene:
            layout.prop(self, "useGlobalScene")
        else:
            row = layout.row(align = True)
            row.prop_search(self, "sceneName",  bpy.data, "scenes", text = text)
            row.prop(self, "useGlobalScene", icon = "WORLD", text = "")

    def getValue(self):
        if self.useGlobalScene:
            return self.nodeTree.scene
        return bpy.data.scenes.get(self.sceneName)

    def setProperty(self, data):
        self.sceneName, self.useGlobalScene = data

    def getProperty(self):
        return self.sceneName, self.useGlobalScene
