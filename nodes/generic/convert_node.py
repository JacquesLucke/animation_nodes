import bpy
from bpy.props import *
from ... tree_info import keepNodeLinks
from ... base_types.node import AnimationNode
from ... sockets.info import toIdName

class ConvertNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ConvertNode"
    bl_label = "Convert"

    def assignedTypeChanged(self, context):
        self.targetIdName = toIdName(self.assignedType)
        self.recreateOutputSocket()

    assignedType = StringProperty(update = assignedTypeChanged)
    targetIdName = StringProperty()

    def create(self):
        self.inputs.new("an_GenericSocket", "Old", "old").dataIsModified = True
        self.assignedType = "String"

    def drawAdvanced(self, layout):
        self.invokeSocketTypeChooser(layout, "assignSocketType",
            socketGroup = "ALL", text = "Change Type", icon = "TRIA_RIGHT")

    def edit(self):
        socket = self.outputs[0]
        targets = socket.dataTargets
        if len(targets) == 1:
            self.assignType(targets[0].dataType)

    def assignSocketType(self, dataType):
        self.assignType(dataType)

    def assignType(self, dataType = "Float"):
        if self.assignedType == dataType: return
        self.assignedType = dataType

    @keepNodeLinks
    def recreateOutputSocket(self):
        self.outputs.clear()
        self.outputs.new(self.targetIdName, "New", "new")

    def getExecutionCode(self):
        t = self.assignedType
        if t == "Float": return ("try: new = float(old)",
                                 "except: new = 0")
        elif t == "Integer": return ("try: new = int(old)",
                                     "except: new = 0")
        elif t == "String": return ("try: new = str(old)",
                                    "except: new = ''")
        elif t == "Vector": return ("try: new = mathutils.Vector(old)",
                                    "except: new = mathutils.Vector((0, 0, 0))")
        else:
            return ("new = old")

    def getUsedModules(self):
        t = self.assignedType
        if t == "Vector": return ["mathutils"]
        return []
