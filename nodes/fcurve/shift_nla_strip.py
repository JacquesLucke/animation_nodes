import bpy
from bpy.props import *
from ... events import executionCodeChanged
from ... base_types.node import AnimationNode

class ShiftNLAStripNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ShiftNLAStripNode"
    bl_label = "Shift NLA Strip"
    
    noStrips = BoolProperty(default = False)
    wrongStripName = BoolProperty(default = False)

    def create(self):
        self.width = 180
        self.inputs.new("an_ObjectSocket", "Object", "object")
        self.inputs.new("an_StringSocket", "Strip Name", "stripName")
        
        self.inputs.new("an_FloatSocket", "Start Frame", "startFrame").value = 1
        self.inputs.new("an_FloatSocket", "End Frame", "endFrame").value = 24
        self.inputs.new("an_FloatSocket", "Repeat", "repeat").value = 1
        
        for socket in self.inputs[2:]:
            socket.useIsUsedProperty = True
            socket.isUsed = False
        
        self.outputs.new("an_ObjectSocket", "Object", "object")
        
    def draw(self, layout):
        if self.noStrips:
            layout.label("No actions set to NLA Strips!", icon = "INFO")
        if self.wrongStripName:
            layout.label("No Strip with this Name!", icon = "INFO")
        
    def execute(self, object, stripName, startFrame, endFrame, repeat):
        self.noStrips, self.wrongStripName = False, False
        if object is not None:
            if object.animation_data is None or object.animation_data.nla_tracks is None:
                self.noStrips = True
                wrongStripName = False
            else:
                self.noStrips = False
                strip = None
                for track in object.animation_data.nla_tracks:
                    if track.strips is not None:
                        for S in track.strips:
                            if S.name == stripName:
                                strip = S
                                
                if strip is not None: 
                    self.wrongStripName = False
                    if self.inputs["Start Frame"].isUsed: strip.frame_start = startFrame
                    if self.inputs["End Frame"].isUsed: strip.frame_end = endFrame
                    if self.inputs["Repeat"].isUsed: strip.repeat = repeat
                        
                else: self.wrongStripName = True
        
        return object
