import bpy
import bmesh
import mathutils

from . import DelaunayVoronoi


class VoronoiSurface:
    def __init__(self, locations, xbuff, ybuff):
        self.locations = locations
        self.xbuff = xbuff
        self.ybuff = ybuff

    def Calculate(self, offsetEdges, offsetEdgesMin, offsetEdgesMax):
        rvVertices = []
        rvFaces = []
        
        rawVertices, rawFacesDict = DelaunayVoronoi.computeVoronoiDiagram(self.locations, self.xbuff, self.ybuff, polygonsOutput=True, formatOutput=True, closePoly=False)
        
        for rawVert in rawVertices: 
            rvVertices.append(mathutils.Vector((rawVert[0], rawVert[1], 0.0)))    # TODO: is it possible to keep z?
            
        # need to remove possible doubles, for now
        for key, val in rawFacesDict.items(): 
            newVal = []
            for currI in val:
                if not currI in newVal: newVal.append(currI)
            if len(newVal) >= 3: rvFaces.append(newVal)

        return rvVertices, rvFaces
