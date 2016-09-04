import bpy
from bpy.props import *
from ... tree_info import keepNodeState
from ... events import executionCodeChanged
from ... base_types import AnimationNode
from mathutils.geometry import tessellate_polygon
from bpy_extras.mesh_utils import ngon_tessellate


polyTypeItems = [
    ("VECTORS", "Vectors in order", "", "", 0),
    ("INDICES", "Simple Poly Index", "", "", 1),
    ("INDICES_LIST", "Poly Indices List", "", "", 2),
    ("MESH", "Mesh Data", "", "", 3),
    ("POLY", "Polygon", "", "", 4),
    ("POLY_LIST", "Polygon List", "", "", 5)]

typesWithLoopFix = ["INDICES_LIST", "MESH"]

operationItems = [
    ("TRI", "Simple Mathutils Tri", "Speed ok. Use mathutils simple triangulate", "", 0),
    ("NGON", "Ngon Simple", "Slower 2x-3x. Use extras ngon triangulate", "", 1)  ]
operationItemsFix = operationItems + [
    ("NGON_FIX", "Ngon Fix Loops", "Slower 4x-5x. Use extras ngon. Solve some loop stuf", "", 2)]
    

class PolygonsTriangulateNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_PolygonsTriangulateNode"
    bl_label = "Triangulate Polygons"
    bl_width_default = 180

    def polyTypeChanged(self, context):
        self.recreateSockets()
        executionCodeChanged()

    operation = EnumProperty(name = "Operation", default = "TRI",
                items = operationItems, update = executionCodeChanged)
    operationFix = EnumProperty(name = "Operation Fix", default = "TRI",
                items = operationItemsFix, update = executionCodeChanged)
                
    polyType = EnumProperty(name = "Polygon  Definition", default = "INDICES_LIST",
                items = polyTypeItems, update = polyTypeChanged)

    def getActiveEnumOp(self):
        if self.polyType in typesWithLoopFix: 
            return  self.operationFix
        else: return  self.operation

    def create(self):
        self.recreateSockets()
        self.polyType = "INDICES_LIST"

    @keepNodeState
    def recreateSockets(self):
        self.inputs.clear()
        self.outputs.clear()
        type = self.polyType

        if type == "VECTORS":
            self.newInput("Vector List", "Ordered Vectors", "vertexLocations")
            self.newOutput("Polygon Indices List", "Triangulated Polygon Indices", "triIndices")
        
        elif type == "INDICES":
            self.newInput("Vector List", "Vertex Locations", "vertexLocations")
            self.newInput("Integer List", "Polygon Index", "indices")
            self.newOutput("Polygon Indices List", "Triangulated Polygon Indices", "triIndices")
        
        elif type == "INDICES_LIST":
            self.newInput("Vector List", "Vertex Locations", "vertexLocations")
            self.newInput("Polygon Indices List", "Polygon Indices", "polygonIndices")
            self.newOutput("Polygon Indices List", "Triangulated Polygon Indices", "triIndices")
            self.newOutput("Integer List", "Source Ngon Indices", "ngonIndices")
        
        elif type == "MESH":
            self.newInput("Mesh Data", "Mesh Data", "meshData")
            self.newOutput("Mesh Data", "Mesh Data", "triMeshData")
            self.newOutput("Integer List", "Source Ngon Indices", "ngonIndices")
        
        elif type == "POLY":
            self.newInput("Polygon", "Polygon", "polygon")
            self.newOutput("Polygon List", "Triangulated Polygon", "triPolyList")
        
        elif type == "POLY_LIST":
            self.newInput("Polygon List", "Polygon List", "polygonList")
            self.newOutput("Polygon List", "Triangulated Polygons", "triPolyList")
            self.newOutput("Integer List", "Source Ngon Indices", "ngonIndices")

    def draw(self, layout):
        layout.prop(self, "polyType", text = "")
        
        if self.polyType in typesWithLoopFix:
            layout.prop(self, "operationFix", expand = True)
        else: 
            layout.prop(self, "operation", expand = True)
        
    def getExecutionCode(self):
        isLinked = self.getLinkedOutputsDict()
        if not any(isLinked.values()): return 
    
        type = self.polyType
        op = self.getActiveEnumOp()


        if type == "VECTORS":
            yield "triIndices = []"

            yield "lenV = len(vertexLocations)"
            yield "if lenV > 2:"
            if op == "TRI": 
                yield "    triIndices = list(self.tesselateVecs(vertexLocations))"
            elif op == "NGON":
                yield "    triIndices = list(self.tesselatePolyNgon(vertexLocations, range(lenV), False))"


        elif type == "INDICES":
            yield "triIndices = []"

            yield "lenV = len(vertexLocations)"
            yield "if lenV > 2 and indices:"
            yield "    if self.isValidPolyIndex(lenV, indices):"
            if op == "TRI": 
                yield "        vertexLocations = [vertexLocations[i] for i in indices]"
                yield "        triIndices = [tuple(indices[i] for i in t) for t in self.tesselateVecs(vertexLocations)]"
            elif op == "NGON":
                yield "        triIndices = list(self.tesselatePolyNgon(vertexLocations, indices, False))"


        elif type == "INDICES_LIST":
            yield "triIndices, ngonIndices = [], []"

            yield "lenV = len(vertexLocations)"
            yield "if lenV > 2 and polygonIndices:"
            yield "    for p, poly in enumerate(polygonIndices):"
            yield "        if self.isValidPolyIndex(lenV, poly):"
            if op == "TRI": 
                yield "    " * 3 + "for t in self.tesselatePoly(vertexLocations, poly):"
            elif op == "NGON":
                yield "    " * 3 + "for t in self.tesselatePolyNgon(vertexLocations, poly, False):"
            elif op == "NGON_FIX":
                yield "    " * 3 + "for t in self.tesselatePolyNgon(vertexLocations, poly, True):"
            if isLinked["triIndices"]: yield "    " * 4 + "triIndices.append(t)"
            if isLinked["ngonIndices"]: yield "    " * 4 + "ngonIndices.append(p)"


        elif type == "MESH":
            yield "triMeshData = meshData"
            yield "triIndices, ngonIndices = [], []"

            yield "vertexLocations, polygonIndices = meshData.vertices, meshData.polygons"
            yield "lenV = len(vertexLocations)"
            yield "if lenV > 2 and polygonIndices:"
            yield "    for p, poly in enumerate(polygonIndices):"
            if op == "TRI": 
                yield "    " * 2 + "for t in self.tesselatePoly(vertexLocations, poly):"
            elif op == "NGON":
                yield "    " * 2 + "for t in self.tesselatePolyNgon(vertexLocations, poly, False):"
            elif op == "NGON_FIX":
                yield "    " * 2 + "for t in self.tesselatePolyNgon(vertexLocations, poly, True):"
            if isLinked["ngonIndices"]: 
                yield "    " * 3 + "ngonIndices.append(p)"
            if isLinked["triMeshData"]: 
                yield "    " * 3 + "triIndices.append(t)"
                yield "    triMeshData.polygons = triIndices"


        elif type == "POLY":
            yield "triPolyList = []"
            yield "if polygon is not None:"
            yield "    vertexLocations = polygon.vertexLocations"
            yield "    lenV = len(vertexLocations)"

            yield "    if lenV < 4: triPolyList = [polygon]"
            yield "    else:"
            if op == "TRI": 
                yield "        for t in self.tesselateVecs(vertexLocations):"
            elif op == "NGON":
                yield "        for t in self.tesselatePolyNgon(vertexLocations, range(lenV), False):"
            yield "    " * 3 + "newPoly = polygon.copy()"
            yield "    " * 3 + "newPoly.vertexLocations = [vertexLocations[i] for i in t]"
            yield "    " * 3 + "triPolyList.append(newPoly)"


        elif type == "POLY_LIST":
            yield "triPolyList, ngonIndices = [], []"
            yield "if polygonList:"
            yield "    for p, polygon in enumerate(polygonList):"
            yield "        vecs = polygon.vertexLocations"
            yield "        lenV = len(vecs)"
        
            yield "        if lenV < 4: triPolyList.append(polygon)"
            yield "        else:"
            if op == "TRI": 
                yield "    " * 3 + "for t in self.tesselateVecs(vecs):"
            elif op == "NGON":
                yield "    " * 3 + "for t in self.tesselatePolyNgon(vecs, range(lenV), False):"
            if isLinked["triPolyList"]: 
                yield "    " * 4 + "newPoly = polygon.copy()"
                yield "    " * 4 + "newPoly.vertexLocations = [vecs[i] for i in t]"
                yield "    " * 4 + "triPolyList.append(newPoly)"
            if isLinked["ngonIndices"]: yield "    " * 4 + "ngonIndices.append(p)"


    def isValidPolyIndex(self, lenV, poly):
        return 0 <= min(poly) and max(poly) < lenV

    def tesselateVecs(self, vecs):
        return (tuple(reversed(t)) for t in tessellate_polygon( [[v for v in vecs]] ) )

    def tesselatePoly(self, vecs, poly):
        return (tuple(poly[i] for i in t) for t in tessellate_polygon( [[vecs[v] for v in poly]] ) )

    def tesselatePolyNgon(self, vecs, poly, fix):
        return (tuple(poly[i] for i in t) for t in ngon_tessellate(vecs, poly, fix_loops=fix))
