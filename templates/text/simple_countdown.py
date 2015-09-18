import bpy
from ... base_types.template import Template

class SimpleCountdownTemplate(bpy.types.Operator, Template):
    bl_idname = "an.simple_countdown_template"
    bl_label = "Countdown"
    nodeOffset = (-500, 0)

    def insert(self):
        timeInfoNode = self.newNode('an_TimeInfoNode', x = 0, y = 0)
        mapRangeNode = self.newNode('an_MapRangeNode', x = 195, y = 50)
        mapRangeNode.inputs[1].value = 0
        mapRangeNode.inputs[2].value = 100
        mapRangeNode.inputs[3].value = 10
        mapRangeNode.inputs[4].value = 0
        roundNumberNode = self.newNode('an_RoundNumberNode', x = 420, y = 50)
        convertNode = self.newNode('an_ConvertNode', x = 630, y = 50)
        textOutputNode = self.newNode('an_TextObjectOutputNode', x = 840, y = 100)

        self.newLink(timeInfoNode.outputs[0], mapRangeNode.inputs[0])
        self.newLink(mapRangeNode.outputs[0], roundNumberNode.inputs[0])
        self.newLink(roundNumberNode.outputs[0], convertNode.inputs[0])
        self.newLink(convertNode.outputs[0], textOutputNode.inputs[1])
