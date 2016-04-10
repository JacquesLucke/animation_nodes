import bpy
from ... base_types.node import AnimationNode


class ParticleListInfoNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ParticleListInfoNode"
    bl_label = "Particle List Info"

    def create(self):
        self.newInput("an_ParticleListSocket", "Particles", "particles")
        self.newOutput("an_VectorListSocket", "Locations", "locations")
        self.newOutput("an_VectorListSocket", "Velocities", "velocities").hide = True
        self.newOutput("an_FloatListSocket", "Sizes", "sizes").hide = True
        self.newOutput("an_FloatListSocket", "Birth Times", "birthTimes").hide = True
        self.newOutput("an_FloatListSocket", "Die Times", "dieTimes").hide = True

    def getExecutionCode(self):
        isLinked = self.getLinkedOutputsDict()
        lines = []
        if isLinked["locations"]: lines.append("locations = [p.location for p in particles]")
        if isLinked["velocities"]: lines.append("velocities = [p.velocity for p in particles]")
        if isLinked["sizes"]: lines.append("sizes = [p.size for p in particles]")
        if isLinked["birthTimes"]: lines.append("birthTimes = [p.birth_time for p in particles]")
        if isLinked["dieTimes"]: lines.append("dieTimes = [p.die_time for p in particles]")
        return lines
