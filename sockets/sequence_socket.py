import bpy
from bpy.props import *
from .. events import propertyChanged
from .. base_types.socket import AnimationNodeSocket

class SequenceSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "mn_SequenceSocket"
    bl_label = "Sequence Socket"
    dataType = "Sequence"
    allowedInputTypes = ["Sequence"]
    drawColor = (0, 0.644, 0, 1)

    sequenceName = StringProperty(update = propertyChanged)
    showName = BoolProperty(default = True)

    def drawInput(self, layout, node, text):
        row = layout.row(align = True)
        if self.showName:
            row.label(text)
        row.prop_search(self, "sequenceName",  bpy.context.scene.sequence_editor, "sequences", icon="NLA", text = "")

        self.callFunctionFromUI(row, "assignActiveSequence", icon = "EYEDROPPER")

    def getValue(self):
        return bpy.context.scene.sequence_editor.sequences.get(self.sequenceName)

    def setStoreableValue(self, data):
        self.sequenceName = data
    def getStoreableValue(self):
        return self.sequenceName

    def assignActiveSequence(self):
        sequenceEditor = bpy.context.scene.sequence_editor
        if not sequenceEditor: return

        sequence = sequenceEditor.active_strip
        if sequence:
            self.sequenceName = sequence.name
