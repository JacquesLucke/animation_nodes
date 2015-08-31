import bpy
from bpy.props import *
from ... utils.layout import writeText
from ... base_types.node import AnimationNode

class CurveObjectOutputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_CurveObjectOutputNode"
    bl_label = "Curve Object Output"

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
        self.inputs.new("an_StringSocket", "Fill Mode", "fillMode")

        self.outputs.new("an_ObjectSocket", "Object", "object")

        for socket in self.inputs[1:]:
            socket.defaultDrawType = "TEXT_ONLY"
        for socket in self.inputs[4:]:
            socket.hide = True

    def draw(self, layout):
        if self.errorMessage != "":
            writeText(layout, self.errorMessage, width = 25, icon = "ERROR")

    def drawAdvanced(self, layout):
        layout.label("This node uses only linked inputs!", icon = "INFO")
        writeText(layout, "Possible values for 'Fill Mode' are: \n3D Curve: 'FULL', 'HALF', 'BACK' and 'FRONT' \n2D Curve: 'NONE', 'BACK', 'FRONT' and 'BOTH'")

    def getExecutionCode(self):
        isLinked = self.getLinkedInputsDict()
        lines = []
        lines.append("if getattr(object, 'type', '') == 'CURVE':")
        lines.append("    curve = object.data")

        if isLinked["bevelDepth"]: lines.append("    curve.bevel_depth = bevelDepth")
        if isLinked["bevelResolution"]: lines.append("    curve.bevel_resolution = bevelResolution")
        if isLinked["bevelStart"]: lines.append("    curve.bevel_factor_start = bevelStart")
        if isLinked["bevelEnd"]: lines.append("    curve.bevel_factor_end = bevelEnd")
        if isLinked["extrude"]: lines.append("    curve.extrude = extrude")
        if isLinked["offset"]: lines.append("    curve.offset = offset")
        if isLinked["previewResolution"]: lines.append("    curve.resolution_u = previewResolution")
        if isLinked["taperObject"]: lines.append("    curve.taper_object = taperObject")
        if isLinked["bevelObject"]: lines.append("    curve.bevel_object = bevelObject")
        if isLinked["fillMode"]: lines.append("    self.setFillMode(curve, fillMode)")

        lines.append("    pass")

        return lines

    def setFillMode(self, curve, fillMode):
        isCorrectFillMode = fillMode in ("FULL", "BACK", "FRONT", "HALF") if curve.dimensions == "3D" else fillMode in ("NONE", "BACK", "FRONT", "BOTH")
        if isCorrectFillMode:
            curve.fill_mode = fillMode
            self.errorMessage = ""
        else:
            self.errorMessage = "The fill mode is invalid. Look in the advanced panels to see all possible values."
