import bpy
from bpy.props import *
from ... events import executionCodeChanged
from ... base_types.node import AnimationNode
from mathutils import Vector, Matrix

    # Animation Nodes Poly Underware / ver 0.2 (refactor version), no vertex normals involved in this ver
    # creates a "wireframe" in centers of poly and middle ofedges, but can be used for normal wireframe too
    # by o.g. 03.09.2015
    # started from dual polyhedron idea on forum 

class PolyUnderwareNode(bpy.types.Node, AnimationNode): 
    bl_idname = "an_PolyUnderwareNode"
    bl_label = "Poly Underware"
    
    useCentral =  BoolProperty(name = "Use Central Poly", default = True,
        description = "Create central poly, at the stripes intersection. If off, there will be a hole",
        update = executionCodeChanged)
    
    def create(self):
        self.inputs.new("an_PolygonSocket", "Polygon", "polygon")
        self.inputs.new("an_FloatSocket", "Width Factor", "widthFactor").value = 0.5
        self.inputs.new("an_FloatSocket", "Smooth Factor", "smoothFactor").value = 0.0
        self.inputs.new("an_FloatSocket", "Center Offset", "centerOffset").value = 0.0
        
        self.outputs.new("an_VectorListSocket", "Vertex Locations", "vertexLocations")
        self.outputs.new("an_PolygonIndicesListSocket", "Polygons Indices", "polygonsIndices")
        
    def draw(self, layout):
        layout.prop(self, "useCentral")
        
    def drawAdvanced(self, layout):
        layout.operator("wm.call_menu", text = "Info / Help", icon = "INFO").name = "an.show_help_poly_underware"
        
    def getExecutionCode(self):
        isLinked = self.getLinkedOutputsDict()
        
        yield "vertexLocations = []"
        yield "polygonsIndices = []"
        
        if any([isLinked["vertexLocations"], isLinked["polygonsIndices"]]):
            # factors
            yield "wFactor = min(max(widthFactor, 0), 1)"   #widthFactor clamp 
            yield "if (1 - wFactor) == 0:"
            yield "    sFactor = min(max(smoothFactor, 0), 1)" 
            yield "    lerpfac = 1 - sFactor"               # corner filled / full face
            yield "else:"
            yield "    sFactor = min(max(smoothFactor, - wFactor / (1 - wFactor)), 1)"
            yield "    lerpfac = wFactor + (1 - wFactor) * sFactor"     # smoothFactor"
            
            yield "Center = polygon.center.lerp(polygon.center + polygon.normal, centerOffset)"
            yield "polyVerts, lenPV = polygon.vertices, len(polygon.vertices)"
            
            yield "centralPoly = []"
            yield "for i, polyVert in enumerate(polyVerts):"
            # stripeVerts
            yield "    stripeVerts = []"
            yield "    i2 = (i+1) % lenPV"
            yield "    middle = polyVert.lerp(polyVerts[i2], 0.5)"
                
            yield "    V0 = Center.lerp(polyVert, lerpfac)"
            yield "    V1 = middle.lerp(polyVert, wFactor)"
            yield "    V2 = middle.lerp(polyVerts[i2], wFactor)"                     
                
            yield "    stripeVerts = [V0, V1, V2]"
            yield "    vertexLocations.extend(stripeVerts)"
        
            if isLinked["polygonsIndices"]:
                # poli indices for stripes
                yield "    Pindex = [3 * i, 3 * i + 1, 3 * i + 2, ( (3 * i + 3) % (3 * lenPV) )]"
                yield "    polygonsIndices.append( Pindex )"
                # poli indices for central 
                if self.useCentral:
                    yield "    centralPoly.append( 3 * i )"
                    yield "polygonsIndices.append(centralPoly)"
    


class ShowHelp(bpy.types.Menu):
    bl_idname = "an.show_help_poly_underware"
    bl_label = "Poly Underware node | Blender - Animation Nodes"

    helpText = StringProperty(default = "help here")
    noteText = StringProperty(default = "note here")
    helpLines = []
    noteLines = []
    
    def draw(self, context):
        layout = self.layout
        layout.operator_context = "INVOKE_DEFAULT"
        layout.label('''Help, notes.''', icon = "INFO")
        row = layout.row(align = True)
        
        col = row.column(align = True)
        helpLines = self.helpText.split("\n")
        for li in helpLines:
            if li:
                col.label(text=li)
                
        col = row.column(align = True)
        noteLines = self.noteText.split("\n")
        for li in noteLines:
            if li:
                col.label(text=li)
            
        layout.label("o.g. 09.2015", icon = "INFO")
        
    helpText ='''
Purpose:
        Creates a mesh based on centers and edge mids of a polygon, a wireframe
    going thru middle of poly. Mostly like an alternative to normal wireframe.
    It actually creates stripes, not wireframes as in edges, with possible vary
    of width or smoothness.
        
        Normally it is used in a loop to distribute this wire/network on the faces of 
    another mesh, deforming according to the shape and normals of the target polygons.
        You can alter the smooth or width per polygon. You can use other loops before 
    or after to get more variation.
    
        The width and smooth factors are related. Smooth depends on the width and
    actually goes with negative values from center of poly till (1) the corners.
    
        The stripes are made of quads, but the center polys are 3, 4 or Ngons like 
    the original poly.
    
Inputs:    
    [ Polygon ]          :  The target polygon, base for the strips
    [ Width Factor ]     :  How wide is the stripe. Factor 0-1 relative to base polygon 
    [ Smooth Factor ]    :  Smooth/round edges of stripes around verts. 
                            Factor is relative to base polygon and Width. 
                     It goes from 0-1 for noSmooth-up to cornes, 
                     but can go <0 till the center of the polygon
Outputs:
    [ Vertex Locations ] : The vertex locations of new mesh (stripes)
    [ Polygons Indices ] : Polygons Indices of new mesh (stripes)
                     use these two in the usual combine mesh to create mesh in AN ways.
                     or just use the verts or so.
'''
    noteText ='''
notes:
    I flirted with other names: 
        
            Poly's secret, sexy Poly, Poly tanga, mesh cleavage, cover your Poly ...
            And for the parameters, polygon = chick, width = thong factor, curvy, etc
    
            (it should probably be called Mid Wireframe or so)
    
    also to be found on:
        http://blenderartists.org/forum  Addon-Animation-Nodes , page xx, post 13xx
        explanations and examples from that point on
    
    The logic of the node being implemented per 1 polygon is to allow
    maximum flexibility in a nodal way. 
    This way, the vertex locations out the node can be altered 
    per polygon, per mesh, polygons can be altered before creating the stripes.
    This is somewhat different form implementing as one whole "black box".
    
    Also, the mesh is only constructed once, at the end of the tree.

To explore further:
    I'm also exploring some edge continuity and more options, offset, 
    subdivisions etc.
    
ps: keep your panties on, Poly!
'''
