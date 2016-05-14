import bpy
from bpy.props import *
from mathutils import Vector, geometry
from ... events import executionCodeChanged
from ... base_types.node import AnimationNode

edgesTypeItems = [  ("POINTS", "Points in order", ""),
                    ("EDGES", "Points by edges", "") ]

class IntersectPolylinePlaneNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_IntersectPolylinePlaneNode"
    bl_label = "Intersect Polyline Plane"
    bl_width_default = 160
    
    def edgesTypeChanged(self, context):
        executionCodeChanged()
    
    edgesType = EnumProperty(name = "Plane Type", default = "POINTS",
        items = edgesTypeItems, update = edgesTypeChanged)
    message = StringProperty(name = "Message", default = "Expecting Points")
    cyclic = BoolProperty(name = "Cyclic Points", 
        description = "Consider last point to first point also, for closed polygon or cyclic spline", 
        default = True, update = executionCodeChanged)
        
    def create(self):
        self.newInput("Vector List", "Positions", "positions")
        self.newInput("Edge Indices List", "Edge Indices", "edges")
        self.inputs[1].useIsUsedProperty = True
        self.inputs[1].isUsed = False
        self.newInput("Vector", "Plane Point", "planePoint")
        self.newInput("Vector", "Plane Normal", "planeNormal", value = (0, 0, 1))

        self.newOutput("Vector List", "Intersections List", "intersections")
        self.newOutput("Integer List", "Intersected Edge Index", "cutEdges", hide = True)
        self.newOutput("Integer List", "Intersected Edge Plane Side", "cutEdgesDir", hide = True)
        self.newOutput("Boolean", "Is Valid", "isValid", hide = True)
        
    def draw(self, layout):
        if self.edgesType == 'POINTS': layout.prop(self, "cyclic")

    def getExecutionCode(self):
        if self.inputs["Edge Indices"].isUsed: self.edgesType = 'EDGES'
        else: self.edgesType = "POINTS"
        
        isLinked = self.getLinkedInputsDict()
        isLinkedOut = self.getLinkedOutputsDict()
        if not any(isLinkedOut.values()): return ""
        
        int  = "intersections"  if isLinkedOut["intersections"] else ""
        edge = "cutEdges"       if isLinkedOut["cutEdges"] else ""
        dir  = "cutEdgesDir"    if isLinkedOut["cutEdgesDir"] else ""
        valid= "isValid"        if isLinkedOut["isValid"] else ""

        yield from intersectPolylinePlane(  "positions", "edges", 
                                            "planePoint", "planeNormal",
                                            self.edgesType, self.cyclic,
                                            intersections = int, 
                                            cutEdges = edge, 
                                            cutEdgesDir = dir, 
                                            isValid = valid, 
                                            message = "self.message" )

    def getUsedModules(self):
        return ["mathutils"]



def intersectPolylinePlane( positions, edges, planeCo, planeNo,
                            type, cyclic, 
                            intersections = "", 
                            cutEdges = "", 
                            cutEdgesDir = "", 
                            isValid = "", 
                            message = ""):

    getInt  = True if intersections != "" else False
    getEdge = True if cutEdges != "" else False
    getDir  = True if cutEdgesDir != "" else False
    getOk   = True if isValid != "" else False
    getMsg  = True if message != "" else False
    
    if not any([getInt, getEdge, getDir, getOk]): return

    if getInt : yield intersections + " = []"
    if getEdge: yield cutEdges + " = []"
    if getDir : yield cutEdgesDir + " = []"
    if getOk  : yield isValid + " = False"

    yield "lenP = len({})".format(positions)
    yield "if lenP > 1:"

    i = " " * 8
    if type == "POINTS":
        yield "    for i, pos1 in enumerate({}):".format(positions)
        
        if cyclic: i = " " * 4
        else: yield "        if i != 0:"
        yield i + "    pos0 = {}[i-1]".format(positions)
    
    elif type == "EDGES":
        yield "    for i, edge in enumerate({}):".format(edges)
        yield "        if max(edge) < lenP:"
        yield i + "    pos0, pos1 = {}[edge[0]], {}[edge[1]]".format(positions, positions)
    
    yield i + "    dot0, dot1 = (pos0-{}).dot({}), (pos1-{}).dot({})".format(planeCo, planeNo, planeCo, planeNo,)

    yield i + "    if dot1 == 0:"
    if getInt : yield i + "        {}.append(pos1)".format(intersections)
    if getEdge: yield i + "        {}.append(i)".format(cutEdges)
    if getDir : yield i + "        {}.append(0)".format(cutEdgesDir)
    if getOk  : yield i + "        {} = True".format(isValid)

    yield i + "    elif (dot0 > 0 and dot1 < 0):"
    if getInt : yield i + ("        {}.append(mathutils.geometry.intersect_line_plane(pos0, pos1, {}, {}))"
                                                .format(intersections, planeCo, planeNo))
    if getEdge: yield i + "        {}.append(i)".format(cutEdges)
    if getDir : yield i + "        {}.append(-1)".format(cutEdgesDir)
    if getOk  : yield i + "        {} = True".format(isValid)

    yield i + "    elif (dot0 < 0 and dot1 > 0):"
    if getInt : yield i + ("        {}.append(mathutils.geometry.intersect_line_plane(pos0, pos1, {}, {}))"
                                                .format(intersections, planeCo, planeNo))
    if getEdge: yield i + "        {}.append(i)".format(cutEdges)
    if getDir : yield i + "        {}.append( 1)".format(cutEdgesDir)
    if getOk  : yield i + "        {} = True".format(isValid)


    if getMsg  : 
        yield "    if not edges: {} = 'No Edges !'".format(message)
        yield "else: {} = 'Not enough points'".format(message)

