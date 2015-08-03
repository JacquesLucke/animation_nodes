import bpy
from bpy.props import *
from .. base_types.socket import AnimationNodeSocket
from .. events import propertyChanged

class mn_SequenceSocket(bpy.types.NodeSocket, AnimationNodeSocket):
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

        selector = row.operator("mn.assign_active_sequence_to_socket", text = "", icon = "EYEDROPPER")
        selector.nodeTreeName = node.id_data.name
        selector.nodeName = node.name
        selector.isOutput = self.is_output
        selector.socketName = self.name
        selector.target = "sequenceName"

    def getValue(self):
        return bpy.context.scene.sequence_editor.sequences.get(self.sequenceName)

    def setStoreableValue(self, data):
        self.sequenceName = data
    def getStoreableValue(self):
        return self.sequenceName


class AssignActiveSequenceToSocket(bpy.types.Operator):
    bl_idname = "mn.assign_active_sequence_to_socket"
    bl_label = "Assign Active Sequence"

    nodeTreeName = StringProperty()
    nodeName = StringProperty()
    target = StringProperty()
    isOutput = BoolProperty()
    socketName = StringProperty()

    @classmethod
    def poll(cls, context):
        return getActive() is not None

    def execute(self, context):
        sequenceEditor = context.scene.sequence_editor
        sequence = None
        if sequenceEditor:
            sequence = sequenceEditor.active_strip

        node = getNode(self.nodeTreeName, self.nodeName)
        socket = getSocketFromNode(node, self.isOutput, self.socketName)
        setattr(socket, self.target, sequence.name)
        return {'FINISHED'}
