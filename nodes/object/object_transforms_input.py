import bpy
from bpy.props import *
from mathutils import Vector
from ... events import executionCodeChanged
from ... base_types.node import AnimationNode
from ... utils.fcurve import getArrayValueAtFrame

frameTypeItems = [
    ("OFFSET", "Offset", ""),
    ("ABSOLUTE", "Absolute", "") ]

class ObjectTransformsInputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ObjectTransformsInputNode"
    bl_label = "Object Transforms Input"

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
        self.width = 165
        self.inputs.new("an_ObjectSocket", "Object", "object").defaultDrawType = "PROPERTY_ONLY"
        self.outputs.new("an_VectorSocket", "Location", "location")
        self.outputs.new("an_EulerSocket", "Rotation", "rotation")
        self.outputs.new("an_VectorSocket", "Scale", "scale")
        self.outputs.new("an_QuaternionSocket", "Quaternion", "quaternion").hide = True

    def updateFrameSocket(self):
        if self.useCurrentTransforms:
            if "Frame" in self.inputs:
                self.inputs["Frame"].remove()
        else:
            if "Frame" not in self.inputs:
                self.inputs.new("an_FloatSocket", "Frame", "frame")

    def draw(self, layout):
        if not self.useCurrentTransforms:
            layout.prop(self, "frameType")

    def drawAdvanced(self, layout):
        layout.prop(self, "useCurrentTransforms")
        col = layout.column()
        col.active = not self.useCurrentTransforms
        col.prop(self, "frameType")

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
            if isLinked["location"]: yield "    location = mathutils.Vector(animation_nodes.utils.fcurve.getArrayValueAtFrame(object, 'location', evaluationFrame))"
            if isLinked["rotation"]: yield "    rotation = mathutils.Euler(animation_nodes.utils.fcurve.getArrayValueAtFrame(object, 'rotation_euler', evaluationFrame))"
            if isLinked["scale"]:    yield "    scale = mathutils.Vector(animation_nodes.utils.fcurve.getArrayValueAtFrame(object, 'scale', evaluationFrame))"
            if isLinked["quaternion"]:    yield "    quaternion = mathutils.Quaternion(animation_nodes.utils.fcurve.getArrayValueAtFrame(object, 'rotation_quaternion', evaluationFrame, arraySize = 4))"

        yield "except:"
        yield "    location = mathutils.Vector((0, 0, 0))"
        yield "    rotation = mathutils.Euler((0, 0, 0))"
        yield "    scale = mathutils.Vector((0, 0, 0))"
        yield "    quaternion = mathutils.Quaternion((1, 0, 0, 0))"

    def getUsedModules(self):
        return ["mathutils"]
