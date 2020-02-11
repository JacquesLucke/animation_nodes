import bpy
from bpy.props import *
from ... events import propertyChanged
from ... base_types import AnimationNode, VectorizedSocket

class SetGPStrokeAttributesNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_SetGPStrokeAttributesNode"
    bl_label = "Set GP Stroke Attributes"
    errorHandlingType = "EXCEPTION"

    useStrokeList: VectorizedSocket.newProperty()
    useLineWidthList: VectorizedSocket.newProperty()
    useCyclicList: VectorizedSocket.newProperty()
    useStartCapModeList: VectorizedSocket.newProperty()
    useEndCapModeList: VectorizedSocket.newProperty()
    useMaterialIndexList: VectorizedSocket.newProperty()
    useDisplayModeList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput(VectorizedSocket("GPStroke", "useStrokeList",
            ("Stroke", "strokes"), ("Strokes", "strokes")), dataIsModified = True)
        self.newInput(VectorizedSocket("Float", "useLineWidthList",
            ("Line Width", "lineWidths"), ("Line Widths", "lineWidths")), value = 250)
        self.newInput(VectorizedSocket("Boolean", "useCyclicList",
            ("Cyclic", "cyclics"), ("Cyclics", "cyclics")), value = False, hide = True)
        self.newInput(VectorizedSocket("Text", "useStartCapModeList",
            ("Start Cap Mode", "startCapModes"), ("Start Cap Modes", "startCapModes")), value = 'ROUND', hide = True)
        self.newInput(VectorizedSocket("Text", "useEndCapModeList",
            ("End Cap Mode", "endCapModes"), ("End Cap Modes", "endCapModes")), value = 'ROUND', hide = True)
        self.newInput(VectorizedSocket("Integer", "useMaterialIndexList",
            ("Material Index", "materialIndices"), ("Material Indices", "materialIndices")), value = 0)
        self.newInput(VectorizedSocket("Text", "useDisplayModeList",
            ("Display Mode", "displayModes"), ("Display Modes", "displayModes")), value = '3DSPACE', hide = True)

        self.newOutput(VectorizedSocket("GPStroke",
            ["useStrokeList", "useLineWidthList", "useCyclicList",
            "useStartCapModeList", "useEndCapModeList", "useMaterialIndexList", "useDisplayModeList"],
            ("Stroke", "outStroke"), ("Strokes", "outStrokes")))

        for socket in self.inputs[1:]:
            socket.useIsUsedProperty = True
            socket.isUsed = False

    def getExecutionCode(self, required):
        s = self.inputs
        isLineWidth = s[1].isUsed
        isCylic = s[2].isUsed
        isStartCapMode = s[3].isUsed
        isEndCapMode = s[4].isUsed
        isMaterialIndex = s[5].isUsed
        isDisplayMode = s[6].isUsed
        if any([self.useStrokeList, self.useLineWidthList, self.useCyclicList, self.useStartCapModeList,
                self.useEndCapModeList, self.useMaterialIndexList, self.useDisplayModeList]):
            if any([isLineWidth, isCylic, isStartCapMode, isEndCapMode, isMaterialIndex, isDisplayMode]):
                if isLineWidth:     yield "_lineWidths = VirtualDoubleList.create(lineWidths, 0)"
                if isCylic:         yield "_cyclics = VirtualBooleanList.create(cyclics, False)"
                if isStartCapMode:  yield "_startCapModes = VirtualPyList.create(startCapModes, 'ROUND')"
                if isEndCapMode:    yield "_endCapModes = VirtualPyList.create(endCapModes, 'ROUND')"
                if isMaterialIndex: yield "_materialIndices = VirtualLongList.create(materialIndices, 0)"
                if isDisplayMode:   yield "_displayModes = VirtualPyList.create(displayModes, '3DSPACE')"

                yield                     "_strokes = VirtualPyList.create(strokes, GPStroke())"
                yield                     "amount = VirtualPyList.getMaxRealLength(_strokes"
                if isLineWidth:     yield "         , _lineWidths"
                if isCylic:         yield "         , _cyclics"
                if isStartCapMode:  yield "         , _startCapModes"
                if isEndCapMode:    yield "         , _endCapModes"
                if isMaterialIndex: yield "         , _materialIndices"
                if isDisplayMode:   yield "         , _displayModes"
                yield                     "         )"

                yield                     "outStrokes = []"
                yield                     "for i in range(amount):"
                yield                     "    strokeNew = _strokes[i].copy()"
                if isLineWidth:     yield "    strokeNew.lineWidth = _lineWidths[i]"
                if isCylic:         yield "    strokeNew.drawCyclic = _cyclics[i]"
                if isStartCapMode:  yield "    self.setStartCapMode(strokeNew, _startCapModes[i])"
                if isEndCapMode:    yield "    self.setEndCapMode(strokeNew, _endCapModes[i])"
                if isMaterialIndex: yield "    strokeNew.materialIndex = _materialIndices[i]"
                if isDisplayMode:   yield "    self.setDisplayMode(strokeNew, _displayModes[i])"
                yield                     "    outStrokes.append(strokeNew)"
            else:
                yield                     "outStrokes = strokes"

        else:
            yield                     "outStroke = strokes"
            if isLineWidth:     yield "outStroke.lineWidth = lineWidths"
            if isCylic:         yield "outStroke.drawCyclic = cyclics"
            if isStartCapMode:  yield "self.setStartCapMode(outStroke, startCapModes)"
            if isEndCapMode:    yield "self.setEndCapMode(outStroke, endCapModes)"
            if isMaterialIndex: yield "outStroke.materialIndex = materialIndices"
            if isDisplayMode:   yield "self.setDisplayMode(outStroke, displayModes)"

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
