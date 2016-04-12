import bpy
import sys
from bpy.props import *
from .. events import propertyChanged
from .. base_types.socket import AnimationNodeSocket

def getValue(self):
    return min(max(self.minValue, self.get("value", 0)), self.maxValue)
def setValue(self, value):
    self["value"] = min(max(self.minValue, value), self.maxValue)

class FloatSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_FloatSocket"
    bl_label = "Float Socket"
    dataType = "Float"
    allowedInputTypes = ["Float", "Integer"]
    drawColor = (0.4, 0.4, 0.7, 1)
    comparable = True
    storable = True

    value = FloatProperty(default = 0.0,
        set = setValue, get = getValue,
        update = propertyChanged)

    minValue = FloatProperty(default = -1e10)
    maxValue = FloatProperty(default = sys.float_info.max)

    def drawProperty(self, layout, text):
        layout.prop(self, "value", text = text)

    def getValue(self):
        return self.value

    def setProperty(self, data):
        self.value = data

    def getProperty(self):
        return self.value

    def setRange(self, min, max):
        self.minValue = min
        self.maxValue = max

    def shouldBeIntegerSocket(self):
        targets = self.dataTargets
        if len(targets) == 0: return False

        ignoredNodesCounter = 0
        for socket in targets:
            if socket.dataType == "Generic":
                if "Debug" not in socket.node.bl_idname:
                    return False
                else:
                    ignoredNodesCounter += 1
            elif socket.dataType != "Integer":
                return False

        if ignoredNodesCounter == len(targets):
            return False
        return True


class FloatListSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_FloatListSocket"
    bl_label = "Float List Socket"
    dataType = "Float List"
    baseDataType = "Float"
    allowedInputTypes = ["Float List", "Integer List"]
    drawColor = (0.4, 0.4, 0.7, 0.5)
    storable = True
    comparable = False

    def getValueCode(self):
        return "[]"

    @classmethod
    def getCopyExpression(cls):
        return "value[:]"
