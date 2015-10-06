import bpy
from ... base_types.node import AnimationNode

class NLAstripsFromObjectNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_NLAstripsFromObjectNode"
    bl_label = "NLA Strips from Object"

    def create(self):
        self.inputs.new("an_ObjectSocket", "Object", "object").defaultDrawType = "PROPERTY_ONLY"
        self.outputs.new("an_GenericListSocket", "NLA Strips", "NLAStrips")     # replace with an_NLAStripListSocket
    
    def drawAdvanced(self, layout):
        layout.label("This node uses Actions already set to NLA Strips", icon = "INFO")
    
    def execute(self, object):
        stripList = []
        #if object is not None:
        try:
            for track in object.animation_data.nla_tracks:
                stripList.extend(track.strips)
            
            return stripList
        except: return []
