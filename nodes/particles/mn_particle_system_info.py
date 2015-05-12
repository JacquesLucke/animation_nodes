import bpy, random, mathutils
from bpy.types import Node
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling


class mn_ParticleSystemInfo(Node, AnimationNode):
    bl_idname = "mn_ParticleSystemInfo"
    bl_label = "Particle System Info"
    outputUseParameterName = "useOutput"
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_ParticleSystemSocket", "Particle System")
        self.outputs.new("mn_ParticleListSocket", "Particles")
        self.outputs.new("mn_VectorListSocket", "Particle Locations")
        allowCompiling()
        
    def getInputSocketNames(self):
        return {"Particle System" : "particleSystem"}
    def getOutputSocketNames(self):
        return {"Particles" : "particles",
                "Particle Locations" : "particleLocations"}

    def execute(self, useOutput, particleSystem):
        if not particleSystem: return []
        locations = []
        if useOutput["Particle Locations"]:
            locations = [p.location for p in particleSystem.particles]
        return particleSystem.particles, locations
        

