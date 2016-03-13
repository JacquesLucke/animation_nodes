import bpy
from bpy.props import *
from ... utils.layout import writeText
from ... base_types.node import AnimationNode

class CurveObjectOutputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_CurveObjectOutputNode"
    bl_label = "Curve Object Output"
    bl_width_default = 175

    errorMessage = StringProperty()

    def create(self):
        self.inputs.new("an_ObjectSocket", "Object", "object").defaultDrawType = "PROPERTY_ONLY"

        self.inputs.new("an_FloatSocket", "Bevel Depth", "bevelDepth")
        self.inputs.new("an_IntegerSocket", "Bevel Resolution", "bevelResolution")
        self.inputs.new("an_FloatSocket", "Extrude", "extrude")
        self.inputs.new("an_FloatSocket", "Bevel Start", "bevelStart")
        self.inputs.new("an_FloatSocket", "Bevel End", "bevelEnd").value = 1.0
        self.inputs.new("an_FloatSocket", "Offset", "offset")
        self.inputs.new("an_IntegerSocket", "Preview Resolution", "previewResolution").value = 12
        self.inputs.new("an_ObjectSocket", "Taper Object", "taperObject")
        self.inputs.new("an_ObjectSocket", "Bevel Object", "bevelObject")
        self.inputs.new("an_StringSocket", "Fill Mode", "fillMode").value = "FRONT"

        self.outputs.new("an_ObjectSocket", "Object", "object")

        for socket in self.inputs[1:]:
            socket.useIsUsedProperty = True
            socket.isUsed = False
        for socket in self.inputs[4:]:
            socket.hide = True

    def draw(self, layout):
        if self.errorMessage != "":
            writeText(layout, self.errorMessage, width = 25, icon = "ERROR")

    def drawAdvanced(self, layout):
        writeText(layout, "Possible values for 'Fill Mode' are: \n3D Curve: 'FULL', 'HALF', 'BACK' and 'FRONT' \n2D Curve: 'NONE', 'BACK', 'FRONT' and 'BOTH'")

    def getExecutionCode(self):
        yield "if getattr(object, 'type', '') == 'CURVE':"
        yield "    curve = object.data"

        s = self.inputs
        if s["Bevel Depth"].isUsed:         yield "    curve.bevel_depth = bevelDepth"
        if s["Bevel Resolution"].isUsed:    yield "    curve.bevel_resolution = bevelResolution"
        if s["Bevel Start"].isUsed:         yield "    curve.bevel_factor_start = bevelStart"
        if s["Bevel End"].isUsed:           yield "    curve.bevel_factor_end = bevelEnd"
        if s["Extrude"].isUsed:             yield "    curve.extrude = extrude"
        if s["Offset"].isUsed:              yield "    curve.offset = offset"
        if s["Preview Resolution"].isUsed:  yield "    curve.resolution_u = previewResolution"
        if s["Taper Object"].isUsed:        yield "    curve.taper_object = taperObject"
        if s["Bevel Object"].isUsed:        yield "    curve.bevel_object = bevelObject"
        if s["Fill Mode"].isUsed:           yield "    self.setFillMode(curve, fillMode)"

    def setFillMode(self, curve, fillMode):
        isCorrectFillMode = fillMode in ("FULL", "BACK", "FRONT", "HALF") if curve.dimensions == "3D" else fillMode in ("NONE", "BACK", "FRONT", "BOTH")
        if isCorrectFillMode:
            curve.fill_mode = fillMode
            self.errorMessage = ""
        else:
            self.errorMessage = "The fill mode is invalid. Look in the advanced panels to see all possible values."
