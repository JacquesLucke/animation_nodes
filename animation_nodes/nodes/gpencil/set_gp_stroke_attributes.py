import bpy
from bpy.props import *
from ... events import propertyChanged
from ... data_structures import GPStroke, VirtualPyList, VirtualDoubleList, VirtualLongList, VirtualBooleanList
from ... base_types import AnimationNode, VectorizedSocket

class SetGPStrokeAttributesNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_SetGPStrokeAttributesNode"
    bl_label = "Set GP Stroke Attributes"
    errorHandlingType = "EXCEPTION"

    useStrokeList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput(VectorizedSocket("GPStroke", "useStrokeList",
            ("Stroke", "stroke"), ("Strokes", "strokes")), dataIsModified = True)
        self.newInput(VectorizedSocket("Float", "useStrokeList",
            ("Line Width", "lineWidth"), ("Line Widths", "lineWidths")), value = 250)
        self.newInput(VectorizedSocket("Boolean", "useStrokeList",
            ("Cyclic", "drawCyclic"), ("Cyclics", "drawCyclics")), value = False)
        self.newInput(VectorizedSocket("Text", "useStrokeList",
            ("Start Cap Mode", "startCapMode"), ("Start Cap Modes", "startCapModes")), value = 'ROUND', hide = True)
        self.newInput(VectorizedSocket("Text", "useStrokeList",
            ("End Cap Mode", "endCapMode"), ("End Cap Modes", "endCapModes")), value = 'ROUND', hide = True)
        self.newInput(VectorizedSocket("Integer", "useStrokeList",
            ("Material Index", "materialIndex"), ("Material Indices", "materialIndices")), value = 0, hide = True)
        self.newInput(VectorizedSocket("Text", "useStrokeList",
            ("Display Mode", "displayMode"), ("Display Modes", "displayModes")), value = '3DSPACE', hide = True)
        self.newOutput(VectorizedSocket("GPStroke", "useStrokeList",
            ("Stroke", "stroke"), ("Strokes", "strokes")))

        for socket in self.inputs[1:]:
            socket.useIsUsedProperty = True
            socket.isUsed = False

    def getExecutionCode(self, required):
        s = self.inputs
        if self.useStrokeList:
            pass
            yield "lineWidths = VirtualDoubleList.create(lineWidths, 250)"
            yield "drawCyclics = VirtualBooleanList.create(drawCyclics, False)"
            yield "startCapModes = VirtualPyList.create(startCapModes, 'ROUND')"
            yield "endCapModes = VirtualPyList.create(endCapModes, 'ROUND')"
            yield "materialIndices = VirtualLongList.create(materialIndices, 0)"
            yield "displayModes = VirtualPyList.create(displayModes, '3DSPACE')"
            yield "for i, stroke in enumerate(strokes):"
            if s["Line Widths"].isUsed:     yield "    stroke.lineWidth = lineWidths[i]"
            if s["Cyclics"].isUsed:         yield "    stroke.drawCyclic = drawCyclics[i]"
            if s["Start Cap Modes"].isUsed: yield "    self.setStartCapMode(stroke, startCapModes[i])"
            if s["End Cap Modes"].isUsed:   yield "    self.setEndCapMode(stroke, endCapModes[i])"
            if s["Material Indices"].isUsed: yield "    stroke.materialIndex = materialIndices[i]"
            if s["Display Modes"].isUsed:   yield "    self.setDisplayMode(stroke, displayModes[i])"
            yield "    pass"
        else:
            if s["Line Width"].isUsed:     yield "stroke.lineWidth = lineWidth"
            if s["Cyclic"].isUsed:         yield "stroke.drawCyclic = drawCyclic"
            if s["Start Cap Mode"].isUsed: yield "self.setStartCapMode(stroke, startCapMode)"
            if s["End Cap Mode"].isUsed:   yield "self.setEndCapMode(stroke, endCapMode)"
            if s["Material Index"].isUsed: yield "stroke.materialIndex = materialIndex"
            if s["Display Mode"].isUsed:   yield "self.setDisplayMode(stroke, displayMode)"

    def setStartCapMode(self, stroke, startCapMode):
        if startCapMode not in ['ROUND', 'FLAT']:
            self.raiseErrorMessage("The Start Cap Mode is invalid. \n\nPossible values for 'Start Cap Mode' are: 'ROUND', 'FLAT'")
        stroke.startCapMode = startCapMode
        return stroke

    def setEndCapMode(self, stroke, endCapMode):
        if endCapMode not in ['ROUND', 'FLAT']:
            self.raiseErrorMessage("The End Cap Mode is invalid. \n\nPossible values for 'End Cap Mode' are: 'ROUND', 'FLAT'")
        stroke.endCapMode = endCapMode
        return stroke

    def setDisplayMode(self, stroke, displayMode):
        if displayMode not in ['SCREEN', '3DSPACE', '2DSPACE', '2DIMAGE']:
            self.raiseErrorMessage("The Display Mode is invalid. \n\nPossible values for 'Display Mode' are: 'SCREEN', '3DSPACE', '2DSPACE', '2DIMAGE'")
        stroke.displayMode = displayMode
        return stroke
