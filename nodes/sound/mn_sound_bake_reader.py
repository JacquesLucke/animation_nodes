import bpy, math
from bpy.types import Node
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling
from ... mn_utils import *
from ... nodes.mn_node_helper import *
from ... mn_cache import *


class mn_SoundBakeReaderNode(Node, AnimationNode):
    bl_idname = "mn_SoundBakeReaderNode"
    bl_label = "Sound Reader"
    
    frameTypes = [
        ("OFFSET", "Offset", ""),
        ("ABSOLUTE", "Absolute", "") ]
    frameType = bpy.props.EnumProperty(name = "Frame Type", items = frameTypes, default = "OFFSET")
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_BakedSoundSocket", "Sound")
        self.inputs.new("mn_FloatSocket", "Frequency")
        self.inputs.new("mn_FloatSocket", "Frame")
        self.outputs.new("mn_FloatListSocket", "Strengths")
        self.outputs.new("mn_FloatSocket", "Strength")
        allowCompiling()
        
    def draw_buttons(self, context, layout):
        layout.prop(self, "frameType", text = "Frame Type")
        
    def getInputSocketNames(self):
        return {"Sound" : "bakeNode",
                "Frequency" : "frequency",
                "Frame" : "frame"}
    def getOutputSocketNames(self):
        return {"Strengths" : "strengths",
                "Strength" : "strength"}
        
    def execute(self, frequency, frame, bakeNode):
        currentFrame = getCurrentFrame()
        if self.frameType == "OFFSET":
            frame += currentFrame
            
        strenghts = []
        if bakeNode is not None:
            strenghts = bakeNode.getStrengthList(frame)
        return strenghts, self.getStrengthOfFrequency(strenghts, frequency)
        
    def getStrengthOfFrequency(self, strengths, frequencyIndicator):
        if len(strengths) > 0:
            length = len(strengths)
            frequencyIndicator *= length
            lower = strengths[max(min(math.floor(frequencyIndicator), length - 1), 0)]
            upper = strengths[max(min(math.ceil(frequencyIndicator), length - 1), 0)]
            influence = frequencyIndicator % 1.0
            influence = self.interpolation(influence)
            return lower * (1 - influence) + upper * influence
        return 0.0
        
    def interpolation(self, influence):
        influence *= 2
        if influence < 1:
            return influence ** 2 / 2
        else:
            return 1 - (2 - influence) ** 2 / 2
        
    def getBakeNode(self):
        return self.id_data.nodes.get(self.bakeNodeName)
