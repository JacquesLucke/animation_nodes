import bpy
from bpy.props import *
from mathutils import Vector
from ... events import executionCodeChanged
from ... base_types.node import AnimationNode
from ... utils.fcurve import getArrayValueAtFrame

frameTypes = [
    ("OFFSET", "Offset", ""),
    ("ABSOLUTE", "Absolute", "") ]

class ObjectTransformsInputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ObjectTransformsInputNode"
    bl_label = "Object Transforms Input"

    def useCurrentTransformsChanged(self, context):
        self.inputs["Frame"].hide = self.useCurrentTransforms
        executionCodeChanged()

    useCurrentTransforms = BoolProperty(
        name = "Use Current Transforms", default = True,
        update = useCurrentTransformsChanged)

    frameType = EnumProperty(
        name = "Frame Type", default = "OFFSET",
        items = frameTypes, update = executionCodeChanged)

    def create(self):
        self.inputs.new("an_ObjectSocket", "Object", "object").defaultDrawType = "PROPERTY_ONLY"
        self.inputs.new("an_FloatSocket", "Frame", "frame").hide = True
        self.outputs.new("an_VectorSocket", "Location", "location")
        self.outputs.new("an_VectorSocket", "Rotation", "rotation")
        self.outputs.new("an_VectorSocket", "Scale", "scale")

    def drawAdvanced(self, layout):
        layout.prop(self, "useCurrentTransforms")
        col = layout.column()
        col.active = not self.useCurrentTransforms
        col.prop(self, "frameType")

    def getExecutionCode(self):
        isLinked = self.getLinkedOutputsDict()
        if not (isLinked["location"] or isLinked["rotation"] or isLinked["scale"]): return []

        frameInput = self.inputs["Frame"]

        lines = []
        add = lines.append

        add("try:")
        if self.useCurrentTransforms:
            if isLinked["location"]: add("    location = object.location")
            if isLinked["rotation"]: add("    rotation = mathutils.Vector(object.rotation_euler)")
            if isLinked["scale"]: add("    scale = object.scale")
        else:
            if self.frameType == "OFFSET": add("    evaluationFrame = frame + bpy.context.scene.frame_current")
            else: add("    evaluationFrame = frame")
            if isLinked["location"]: add("    location = mathutils.Vector(animation_nodes.utils.fcurve.getArrayValueAtFrame(object, 'location', evaluationFrame))")
            if isLinked["rotation"]: add("    rotation = mathutils.Vector(animation_nodes.utils.fcurve.getArrayValueAtFrame(object, 'rotation_euler', evaluationFrame))")
            if isLinked["scale"]: add("    scale = mathutils.Vector(animation_nodes.utils.fcurve.getArrayValueAtFrame(object, 'scale', evaluationFrame))")

        add("except:")
        add("    location = mathutils.Vector((0, 0, 0))")
        add("    rotation = mathutils.Vector((0, 0, 0))")
        add("    scale = mathutils.Vector((0, 0, 0))")

        return lines

    def getUsedModules(self):
        return ["mathutils"]
