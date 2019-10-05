import bpy
from bpy.props import *
from ... sockets.info import isBase, toBaseDataType
from ... events import propertyChanged
from ... base_types import AnimationNode, ListTypeSelectorSocket
from . MTB import create_MIDI, execute_MIDI

# trackNum, frame : content
cache = {}

class MidiTrackNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_MidiTrackNode"
    bl_label = "MIDI Track"
    bl_width_default = 180

    assignedType: ListTypeSelectorSocket.newProperty(default = "Float")

    trackNum = IntProperty(name = "Track Number", default = 1, min = 0, max=15,
    description = "Track Number from MIDI file", update = propertyChanged)

    def create(self):
        prop = ("assignedType", "BASE")
        self.newInput("Generic", "MIDI Data", "midiData")
        self.newInput("Integer", "Frame", "frame")
        self.newOutput(ListTypeSelectorSocket("List", "outList", "LIST", prop))

    def draw(self, layout):
        layout.prop(self, "trackNum")

    def execute(self, midiData, frame):
        # ch = "outList = [1.0,2.0,3.0,4.0,5.0]"
        if midiData is None: return None

        trackNum = self.trackNum

        key = trackNum, frame

        if key not in cache:
            # print("D2 - len = " + str(len(midiData)))

            fps = bpy.context.scene.render.fps
            tb_notes = execute_MIDI(midiData[trackNum], frame, fps)

            # print("D3")
            # print(tb_notes)

            # tb_notes = [1.0,2.0,3.0,4.0,5.0]

            # variableNames = [str(tb_notes[i]) for i, socket in enumerate(tb_notes)]
            # print(variableNames)
            # createPyListExpression = "[" + ", ".join(variableNames) + "]"
            # print(createPyListExpression)
            # createListExpression = self.outputs[0].getFromValuesCode().replace("value", createPyListExpression)
            # print(createListExpression)
            cache[key] = tb_notes
            return tb_notes
        else:
            return cache[key]

        # return "outList = " + createListExpression

    def getEmptyStartList(self):
        return self.outputs[0].getDefaultValue()
