import bpy
from bpy.props import *
from ... events import propertyChanged
from ... base_types import AnimationNode

class GPMaterialOutputNode(AnimationNode, bpy.types.Node):
    bl_idname = "an_GPMaterialOutputNode"
    bl_label = "GP Material Output"
    errorHandlingType = "EXCEPTION"

    def create(self):
        self.newInput("Material", "Material", "material", defaultDrawType = "PROPERTY_ONLY")
        self.newInput("Boolean", "Show Stroke", "showStroke", value = True)
        self.newInput("Text", "Stroke Draw Mode", "strokeDrawMode", value = "LINE")
        self.newInput("Color", "Stroke Color", "strokeColor")
        self.newInput("Boolean", "Show Fill", "showFill", value = False, hide = True)
        self.newInput("Color", "Fill Color", "fillColor", hide = True)
        self.newInput("Integer", "Pass Index", "passIndex", value = 0, minVlaue = 0, hide = True)

        self.newOutput("Material", "Material", "material")

        for socket in self.inputs[1:]:
            socket.useIsUsedProperty = True
            socket.isUsed = False

    def getExecutionCode(self, required):
        yield "if material is not None:"
        yield "    if not material.is_grease_pencil:"
        yield "        bpy.data.materials.create_gpencil_data(material)"

        s = self.inputs
        isShowStroke = s["Show Stroke"].isUsed
        isStrokeDrawMode = s["Stroke Draw Mode"].isUsed
        isStrokeColor = s["Stroke Color"].isUsed
        isShowFill = s["Show Fill"].isUsed
        isFillColor = s["Fill Color"].isUsed
        isPassIndex = s["Pass Index"].isUsed

        if any([isShowStroke, isStrokeDrawMode, isStrokeColor, isShowFill, isFillColor, isPassIndex]):
            yield                      "    gpMaterial = material.grease_pencil"
            if isShowStroke:     yield "    gpMaterial.show_stroke = showStroke"
            if isStrokeDrawMode: yield "    self.setStrokeDrawMode(gpMaterial, strokeDrawMode)"
            if isStrokeColor:    yield "    gpMaterial.color = strokeColor"
            if isShowFill:       yield "    gpMaterial.show_fill = showFill"
            if isFillColor:      yield "    gpMaterial.fill_color = fillColor"
            if isPassIndex:      yield "    gpMaterial.pass_index = passIndex"

    def setStrokeDrawMode(self, gpMaterial, strokeDrawMode):
        if strokeDrawMode not in ["LINE", "DOTS", "BOX"]:
            self.raiseErrorMessage("The Stroke Draw Mode is invalid. \n\nPossible values for 'Stroke Draw Mode' are: 'LINE', 'DOTS', 'BOX'")
        gpMaterial.mode = strokeDrawMode
