import bpy
from bpy.props import *
from ... events import propertyChanged
from ... base_types.node import AnimationNode
from ... data_structures.mesh import Polygon, Vertex
from mathutils import Vector, Matrix

    # Animation Nodes Adaptive Quad, // ver 0.3 / for refactor milestone
    # deforms a mesh according to deformed quad 
    # by o.g. 19.08.2015, update refactor 10.2015
    # on the idea of JoseConseco, based on Adaptive Duplifaces by Alessandro Zomparelli 

class AdaptiveQuad(bpy.types.Node, AnimationNode): 
    bl_idname = "an_AdaptiveQuad"
    bl_label = "Adaptive Quad"
    
    def checkedPropertiesChanged(self, context):
        self.updateSocketVisibility()
        propertyChanged()
    
    normalDeform = BoolProperty(name = "Normal Deform", default = True, 
                            description = "Deform Z using vertex normals. If off, use straight Z, on polygon normal")
    useBbox = BoolProperty(name = "Use Bound Box", default = False, update = checkedPropertiesChanged,
                            description = "Use min max. If off, use default 2x2 plane base as reference")
    useCustomBaseSide = BoolProperty(name = "Use Custom Base", default = False,  update = checkedPropertiesChanged,
                            description = "Use Custom Reference Square Base Side. If off, use default 2x2 plane base as reference")
    
    def create(self):
        self.inputs.new("an_PolygonSocket", "Polygon", "polygon")
        self.inputs.new("an_PolygonIndicesSocket", "Polygon Indices", "polygonIndices")
        self.inputs.new("an_VertexListSocket", "Vertices", "vertices")
        
        self.inputs.new("an_VectorListSocket", "Instance Vertex Locations", "vertexLocations")
        self.inputs.new("an_FloatSocket", "Z Factor", "zFactor").value = 1.0
        self.inputs.new("an_FloatSocket", "Base Side", "baseSide").value = 2.0
        
        self.inputs[5].hide = True
        self.updateSocketVisibility()
        
        self.outputs.new("an_VectorListSocket", "Deformed Vertex Locations", "deformedVertexLocations")
        
    def draw(self, layout):
        layout.prop(self, "normalDeform")
        layout.prop(self, "useBbox")
        
    def drawAdvanced(self, layout):
        layout.prop(self, "show_options")
        layout.prop(self, "useCustomBaseSide")
        layout.label("Custom Base or default 2x2 plane")
        layout.operator("wm.call_menu", text = "Info / update! v0.3", icon = "INFO").name = "an.show_help_adaptive_quad"
        
    def updateSocketVisibility(self):
        if self.useBbox: self.useCustomBaseSide = False 
        self.inputs["Base Side"].hide = not self.useCustomBaseSide

    def execute(self, polygon, polygonIndices, vertices, vertexLocations, zFactor, baseSide): 
        
        DeformedLocations = []
        
        # define the base square as boundBox or 2x2 or (custom bs x bs)
        bs = baseSide / 2 if self.useCustomBaseSide else 1
        
        minX = min(v[0] for v in vertexLocations) if self.useBbox and len(vertexLocations) > 0 else -bs
        maxX = max(v[0] for v in vertexLocations) if self.useBbox and len(vertexLocations) > 0 else bs
        minY = min(v[1] for v in vertexLocations) if self.useBbox and len(vertexLocations) > 0 else -bs
        maxY = max(v[1] for v in vertexLocations) if self.useBbox and len(vertexLocations) > 0 else bs
        
        # quad points and normals
        if all((len(polygon.vertices) > 2, len(polygonIndices) > 2, len(vertices) > max(i for i in polygonIndices))):
            q0 = polygon.vertices[0]
            q1 = polygon.vertices[1]
            q2 = polygon.vertices[2]
            q3 = polygon.vertices[-1]   # escaping non quads, take last, + tris 2=3
            n0 = vertices[polygonIndices[0]].normal
            n1 = vertices[polygonIndices[1]].normal
            n2 = vertices[polygonIndices[2]].normal
            n3 = vertices[polygonIndices[-1]].normal
            nP = polygon.normal
        else:   
            q0 = Vector((-bs, -bs, 0))
            q1 = Vector(( bs, -bs, 0))
            q2 = Vector(( bs,  bs, 0))
            q3 = Vector((-bs,  bs, 0))
            n0 = Vector((-bs, -bs, bs))
            n1 = Vector(( bs, -bs, bs))
            n2 = Vector(( bs,  bs, bs))
            n3 = Vector((-bs,  bs, bs))
            nP = Vector(( 0,  0, bs))
        
        for v in vertexLocations:
            # vert as ratio (factor for interpolation)
            rx = (v[0] - minX) / (maxX - minX) if maxX - minX != 0 else 1.0
            ry = (v[1] - minY) / (maxY - minY) if maxY - minY != 0 else 1.0
            
            # deform xy
            q01 = q0 + (q1 - q0)*rx
            q32 = q3 + (q2 - q3)*rx
            qdef= q01+ (q32-q01)*ry
            
            # add normal verts (radial) deform or fall to normal poly
            if self.normalDeform:
                n01 = n0 + (n1 - n0)*rx
                n32 = n3 + (n2 - n3)*rx
                ndef= n01+ (n32-n01)*ry
            else:
                ndef= nP
            
            DeformedLocations.append(qdef+ndef*v[2]*zFactor)

        return DeformedLocations


class ShowHelp(bpy.types.Menu):
    bl_idname = "an.show_help_adaptive_quad"
    bl_label = "Adaptive Quad node v0.3 | Blender - Animation Nodes"

    helpText = StringProperty(default = "help here")
    noteText = StringProperty(default = "note here")
    helpLines = []
    noteLines = []
    
    def draw(self, context):
        layout = self.layout
        layout.operator_context = "INVOKE_DEFAULT"
        layout.label('''Help, notes. v 0.3''', icon = "INFO")
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
            
        layout.label("o.g. 08.2015, update .10.2015", icon = "INFO")
        
    helpText ='''
Purpose:
        Deform a mesh based on a deformed polygon, connecting mesh instances into a continuous fabric, over connected polygons.
    The polygons are preferably quad. On non quads, the results may be harder to control. Triangels are acceptable (see on the
    forum how it works, a red sphere ...), but more than 4 points Ngons will leave a gap in the fabric.
    
         Normally it is used in a loop to distribute a mesh on the faces of another, deforming the instances according to 
    the shape and normals of the target polygons. You can alter the mesh before or after deformation in any way. You can use 
    more than 1 mesh to distribute and may use adaptives on top of adaptives.(see forum)
    
Inputs:
>>>>These are for the target polygon:
    [ Polygon ]          :  The target polygon, that will deform the instance
    [ Polygon Indices  ] :  The target polygon indices, helper for vertex normals
    [ Vertices]          :  The target vertices list, helper for vertex normals
    
>>>>These are the mesh instance to be deformed:
    [ Vertex Locations ] :  Vertices of the mesh to be instanced and stretched 
    [ ZFactor ]          :  An extra z factor. Will multiply with original z of the mesh (instance)
    
>>>>This is an extra option in the Advanced panel, in case you need other htan the 2x2 square base
    [ Base Side ]:  The side of base square, if not using Bbox. This is centered on obj center. Default is 2, like the default plane (-1 to 1)

Outputs:
    [ Deformed Vertex Locations ] :  The vertex locations deformed positions 

Options:
    [ Normal Deform ] :  z on the normals (interpolated) or straight up /// 
            [v] On  =  deforming on Z in a "radial" way, based on the normal of vertices. Instances will make a continuous contact on z.
            [.] Off =  deforming xy, but keep z straight up from the poly. No "radial" deformation, more like buildings on a sphere.
    [ Use Bound Box ] : the reference source for deformation ///
            [v] On  =  basis of the mesh is the bounding box (xyz min/max). This rectangle will be morphed into the target poly. 
                            Z +/- to the origin of the mesh obj. The mesh will be "enclosed" in the polygon area.
            [.] Off =  basis of the mesh is a square centered on obj center, side = Base Side or 2x2. Default 2 gives a 2x2 square 
                            like the B default plane (-1 to 1) with the origin 0. This square will be morphed into the target polygon. 
                       Useful when you want the mesh to go outside the polygon base.
'''
    noteText ='''
notes:
    Note that useBbox is False by default. This is an extra option, different from original and other variants, where only sq 
    bases are found. The scope it to keep continuity in the mesh connection at the edges, if mesh Vertex Location are deformed inside the loop, 
    per polygon, before the Adaptive node. 
    
other notes
    + mesh orientation will match X of the instance to vertex 0 -> 1 of polygon
    + Base Side socket (activated in the advanced panel) will allow other square sizes for Non Bbox (same center). default 2 = 2x2 Plane (-1 to 1)
    + Show options (in prop panel) can hide the checkboxes to make node smaller

    Updated on v 0.3:
        + different Refactor code etc + eliminated Matrix cause now we have vector list * matrix node :)
        + but added poly indices and verts in order to get vertex normals :(
        + useBbox is False by default + Base Side socket Goes to advanced properties and is hiddent
        + some internal cleaning + + eliminated min/max z and rz ratios as they are not used, maybe to get some effi
..............................................................................
    also to be found on: http://blenderartists.org/forum Addon-Animation-Nodes, page 68, post 1350 (from that point on)

    The logic of the node being implemented per 1 polygon is to allow maximum flexibility in a nodal way. 
    This way, the vertex locations in or out the node can be altered per polygon, per mesh, before or afer 
    deform and in any combination. Use loops to iterate the mesh points give maximum freedom.
    This is somewhat different form implementing as one whole "black box".
    
    Also, the mesh is only constructed once, at the end of the tree. Being usually executed in a loop, 
    and with many mesh instances, any optimization becomes imortant. Plus, there is no concern over recalc normals etc.
'''
