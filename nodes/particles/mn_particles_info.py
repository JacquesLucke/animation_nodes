import bpy, random, mathutils
from bpy.types import Node
from mathutils import Vector
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling


class mn_ParticlesInfo(Node, AnimationNode):
    bl_idname = "mn_ParticlesInfo"
    bl_label = "Particles Info"
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_ParticleListSocket", "Particles")
        self.outputs.new("mn_VectorListSocket", "Locations")
        allowCompiling()
        
    def getInputSocketNames(self):
        return {"Particles" : "particles"}
    def getOutputSocketNames(self):
        return {"Locations" : "locations"}

    def execute(self, particles):
        locations = [p.location for p in particles]
        return locations
        