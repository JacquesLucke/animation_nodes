import bpy
from ... base_types import AnimationNode


class ParticleListInfoNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ParticleListInfoNode"
    bl_label = "Particle List Info"

    def create(self):
        self.newInput("Particle List", "Particles", "particles")
        self.newOutput("Vector List", "Locations", "locations")
        self.newOutput("Vector List", "Velocities", "velocities", hide = True)
        self.newOutput("Float List", "Sizes", "sizes", hide = True)
        self.newOutput("Float List", "Birth Times", "birthTimes", hide = True)
        self.newOutput("Float List", "Die Times", "dieTimes", hide = True)

    def getExecutionCode(self):
        isLinked = self.getLinkedOutputsDict()
        if isLinked["locations"]:  yield "locations = Vector3DList.fromValues(p.location for p in particles)"
        if isLinked["velocities"]: yield "velocities = Vector3DList.fromValues(p.velocity for p in particles)"
        if isLinked["sizes"]:      yield "sizes = DoubleList.fromValues(p.size for p in particles)"
        if isLinked["birthTimes"]: yield "birthTimes = DoubleList.fromValues(p.birth_time for p in particles)"
        if isLinked["dieTimes"]:   yield "dieTimes = DoubleList.fromValues(p.die_time for p in particles)"
