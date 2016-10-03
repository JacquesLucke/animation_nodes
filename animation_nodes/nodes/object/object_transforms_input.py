import bpy
from bpy.props import *
from ... events import executionCodeChanged
from ... base_types import AnimationNode
from ... utils.fcurve import getArrayValueAtFrame

frameTypeItems = [
    ("OFFSET", "Offset", ""),
    ("ABSOLUTE", "Absolute", "") ]

class ObjectTransformsInputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ObjectTransformsInputNode"
    bl_label = "Object Transforms Input"
    bl_width_default = 165

    def useCurrentTransformsChanged(self, context):
        self.updateFrameSocket()
        executionCodeChanged()

    useCurrentTransforms = BoolProperty(
        name = "Use Current Transforms", default = True,
        update = useCurrentTransformsChanged)

    frameType = EnumProperty(
        name = "Frame Type", default = "OFFSET",
        items = frameTypeItems, update = executionCodeChanged)

    def create(self):
        self.newInput("Object", "Object", "object", defaultDrawType = "PROPERTY_ONLY")
        self.newOutput("Vector", "Location", "location")
        self.newOutput("Euler", "Rotation", "rotation")
        self.newOutput("Vector", "Scale", "scale")
        self.newOutput("Quaternion", "Quaternion", "quaternion", hide = True)

    def updateFrameSocket(self):
        if self.useCurrentTransforms:
            if "Frame" in self.inputs:
                self.inputs["Frame"].remove()
        else:
            if "Frame" not in self.inputs:
                self.newInput("an_FloatSocket", "Frame", "frame")

    def draw(self, layout):
        if not self.useCurrentTransforms:
            layout.prop(self, "frameType")

    def drawAdvanced(self, layout):
        layout.prop(self, "useCurrentTransforms")
        col = layout.column()
        col.active = not self.useCurrentTransforms
        col.prop(self, "frameType")
        self.invokeFunction(layout, "createAutoExecutionTrigger", text = "Create Execution Trigger")

    def getExecutionCode(self):
        isLinked = self.getLinkedOutputsDict()
        if not any(isLinked.values()): return

        yield "try:"
        if self.useCurrentTransforms:
            if isLinked["location"]: yield "    location = object.location"
            if isLinked["rotation"]: yield "    rotation = object.rotation_euler"
            if isLinked["scale"]:    yield "    scale = object.scale"
            if isLinked["quaternion"]: yield "    quaternion = object.rotation_quaternion"
        else:
            if self.frameType == "OFFSET": yield "    evaluationFrame = frame + self.nodeTree.scene.frame_current_final"
            else: yield "    evaluationFrame = frame"
            if isLinked["location"]: yield "    location = Vector(animation_nodes.utils.fcurve.getArrayValueAtFrame(object, 'location', evaluationFrame))"
            if isLinked["rotation"]: yield "    rotation = Euler(animation_nodes.utils.fcurve.getArrayValueAtFrame(object, 'rotation_euler', evaluationFrame))"
            if isLinked["scale"]:    yield "    scale = Vector(animation_nodes.utils.fcurve.getArrayValueAtFrame(object, 'scale', evaluationFrame))"
            if isLinked["quaternion"]:    yield "    quaternion = Quaternion(animation_nodes.utils.fcurve.getArrayValueAtFrame(object, 'rotation_quaternion', evaluationFrame, arraySize = 4))"

        yield "except:"
        yield "    location = Vector((0, 0, 0))"
        yield "    rotation = Euler((0, 0, 0))"
        yield "    scale = Vector((0, 0, 0))"
        yield "    quaternion = Quaternion((1, 0, 0, 0))"

    def createAutoExecutionTrigger(self):
        isLinked = self.getLinkedOutputsDict()
        customTriggers = self.nodeTree.autoExecution.customTriggers

        objectName = self.inputs["Object"].objectName

        if isLinked["location"]:
            customTriggers.new("MONITOR_PROPERTY", idType = "OBJECT", dataPath = "location", idObjectName = objectName)
        if isLinked["rotation"]:
            customTriggers.new("MONITOR_PROPERTY", idType = "OBJECT", dataPath = "rotation_euler", idObjectName = objectName)
        if isLinked["scale"]:
            customTriggers.new("MONITOR_PROPERTY", idType = "OBJECT", dataPath = "scale", idObjectName = objectName)
        if isLinked["quaternion"]:
            customTriggers.new("MONITOR_PROPERTY", idType = "OBJECT", dataPath = "rotation_quaternion", idObjectName = objectName)
