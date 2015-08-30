import bpy
from bpy.props import *
from .. events import propertyChanged
from .. base_types.socket import AnimationNodeSocket

class SequenceSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_SequenceSocket"
    bl_label = "Sequence Socket"
    dataType = "Sequence"
    allowedInputTypes = ["Sequence"]
    drawColor = (0, 0.644, 0, 1)

    sequenceName = StringProperty(update = propertyChanged)
    
    def drawProperty(self, layout, text):
        row = layout.row(align = True)

        editor = bpy.context.scene.sequence_editor
        if editor:
            row.prop_search(self, "sequenceName",  editor, "sequences", icon="NLA", text = text)
            self.invokeFunction(row, "assignActiveSequence", icon = "EYEDROPPER")
        else:
            row.label("No Sequence Editor")


    def getValue(self):
        editor = bpy.context.scene.sequence_editor
        if editor: return editor.sequences.get(self.sequenceName)
        return None

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
