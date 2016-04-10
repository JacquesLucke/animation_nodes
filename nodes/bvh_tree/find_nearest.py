import bpy
from ... base_types.node import AnimationNode

class FindNearestSurfacePointNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_FindNearestSurfacePointNode"
    bl_label = "Find Nearest Surface Point"
    bl_width_default = 165

    def create(self):
        self.newInput("an_BVHTreeSocket", "BVHTree", "bvhTree")
        self.newInput("an_VectorSocket", "Vector", "vector").defaultDrawType = "PROPERTY_ONLY"
        socket = self.newInput("an_FloatSocket", "Max Distance", "maxDistance")
        socket.minValue = 0.0
        socket.value = 1e6
        socket.hide = True

        self.newOutput("an_VectorSocket", "Location", "location")
        self.newOutput("an_VectorSocket", "Normal", "normal")
        self.newOutput("an_FloatSocket", "Distance", "distance")
        self.newOutput("an_IntegerSocket", "Polygon Index", "polygonIndex").hide = True
        self.newOutput("an_BooleanSocket", "Hit", "hit")

    def getExecutionCode(self):
        yield "location, normal, polygonIndex, distance = bvhTree.find_nearest(vector, maxDistance)"
        yield "if location is None:"
        yield "    location = mathutils.Vector((0, 0, 0))"
        yield "    normal = mathutils.Vector((0, 0, 0))"
        yield "    polygonIndex = -1"
        yield "    distance = 0"
        yield "    hit = False"
        yield "else: hit = True"

    def getUsedModules(self):
        return ["mathutils"]
