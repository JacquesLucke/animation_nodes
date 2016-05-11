import bpy
from ... base_types.node import AnimationNode

class IntersectSphereSphereNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_IntersectSphereSphereNode"
    bl_label = "Intersect Sphere Sphere"

    def create(self):
        self.width = 160
        self.inputs.new("an_VectorSocket", "Sphere 1 Center", "c1")
        self.inputs.new("an_FloatSocket", "Sphere 1 Radius", "r1").value = 1
        self.inputs.new("an_VectorSocket", "Sphere 2 Center", "c2").value = (0, 0, 1)
        self.inputs.new("an_FloatSocket", "Sphere 2 Radius", "r2").value = 1
        
        self.outputs.new("an_VectorSocket", "Circle Center", "center")
        self.outputs.new("an_VectorSocket", "Circle Normal", "normal")
        self.outputs.new("an_FloatSocket", "Circle Radius", "radius")
        self.outputs.new("an_BooleanSocket", "Is Valid", "isValid").hide = True
        
    def getExecutionCode(self):
        isLinked = self.getLinkedOutputsDict()
        if not any(isLinked.values()): return ""
    
        center  = isLinked["center"]
        normal  = isLinked["normal"]
        radius  = isLinked["radius"]
        isValid = isLinked["isValid"]
        zero = "mathutils.Vector((0,0,0))"
        
        yield "if c1 == c2: "
        if center : yield "    center =" + zero
        if normal : yield "    normal =" + zero
        if radius : yield "    radius = 0"
        if isValid: yield "    isValid = False"
        yield "else:"
        yield "    dif = (c2 - c1)"
        yield "    dist = dif.length"
        yield "    _, intx = mathutils.geometry.intersect_sphere_sphere_2d((0, 0),r1, (dist, 0), r2)"

        yield "    if intx is not None:"
        if center or radius: 
                    yield "        L, radius = intx[0], intx[1] * 2"
        if center : yield "        center = c1.lerp(c2, L/dist)"
        if normal : yield "        normal = dif.normalized()"
        if isValid: yield "        isValid = True"

        yield "    else:"
        if center : yield "        center =" + zero
        if normal : yield "        normal =" + zero
        if radius : yield "        radius = 0"
        if isValid: yield "        isValid = False"
        
    def getUsedModules(self):
        return ["mathutils"]