import bpy
import math
import mathutils

from . import Math



class Polygon(object):
    def __init__(self, listVerticesa):
        if len(listVerticesa) < 3: raise Exception("You need at least 3 vertices to define a polygon")
        
        self.listVertices = list([v.copy() for v in listVerticesa])
        
        
    def __getattr__(self, attrName):
        if attrName == "nrVertices":
            return len(self.listVertices)
            
        if attrName == "centerPoint":
            rvv3 = mathutils.Vector((0.0, 0.0, 0.0))
            if self.nrVertices < 1: return rvv3
            
            for v in self.listVertices: rvv3 = rvv3 + v
                
            rvv3 /= float(self.nrVertices)
            
            return rvv3
    
    
    
    def OffsetEdges(self, offsetMin, offsetMax):
        offsetDelta = offsetMax - offsetMin
        
        nrVerts = self.nrVertices
        center = self.centerPoint
        verts = self.listVertices
        
        offsetRND = mathutils.noise.random()
        offset = offsetMin + offsetRND * offsetDelta
        newVertices = list()
        for vprev, vcurr, vnext in [[verts[iv - 1], verts[iv], verts[iv + 1 - nrVerts]] for iv in range(nrVerts)]:
            # offsetRND = mathutils.noise.random()
            # offset = offsetMin + offsetRND * offsetDelta
            newVertices.append(Polygon.GetOffsetVertex(vprev, vcurr, vnext, offset, center))
            
        self.listVertices = newVertices
        
        
        
        
        
    # screws up geometry even more than OffsetVertex2()
    def OffsetVertex(self, vprev, vcurr, vnext, offset):
        dirNext = vnext - vcurr
        dirPrev = vprev - vcurr
        rotDiff = dirNext.rotation_difference(dirPrev)
        
        facAngle = mathutils.noise.random()
        # facAngle = 0.5
        rotDiff.angle *= facAngle
        dirNext.rotate(rotDiff)
        dir = dirNext.normalized()
    
        rvv = vcurr + (dir * offset)
        
        return rvv
        
        
    def OffsetVertex2(self, vprev, vcurr, vnext, offset, vcenter):
        dir = (vcenter - vcurr).normalized()
        rvv = vcurr + (dir * offset)
        
        return rvv
        
        
    def OffsetVertices(self, offsetMin, offsetMax):
        offsetDelta = offsetMax - offsetMin
        
        nrVerts = self.nrVertices
        verts = self.listVertices
        center = self.centerPoint
        
        newVertices = list()
        for vprev, vcurr, vnext in [[verts[iv - 1], verts[iv], verts[iv + 1 - nrVerts]] for iv in range(nrVerts)]:
            offsetRND = mathutils.noise.random()
            offset = offsetMin + offsetRND * offsetDelta
            # newVertices.append(self.OffsetVertex(vprev, vcurr, vnext, offset))
            newVertices.append(self.OffsetVertex2(vprev, vcurr, vnext, offset, center))
            
        self.listVertices = newVertices
    
    
    
    
    
    def GetAngle(self, vertIndex):
        verts = self.listVertices
        vprev, vcurr, vnext = verts[vertIndex - 1], verts[vertIndex], verts[vertIndex + 1 - self.nrVertices]
        dirNext = vnext - vcurr
        dirPrev = vprev - vcurr
        
        return dirNext.angle(dirPrev)
        
    def GetSharpestAngle(self):
        minAng = 10.0
        minIndex = -1
        
        for iv in range(self.nrVertices):
            currAng = self.GetAngle(iv)
            if currAng < minAng:
                minAng = currAng
                minIndex = iv
                
        return minAng, minIndex
        
    def GetShortestEdge(self):
        verts = self.listVertices
        
        minLen2 = 1000000.0
        minIndex = -1
        for iv in range(self.nrVertices):
            vcurr, vnext = verts[iv], verts[iv + 1 - self.nrVertices]
            currLen2 = (vcurr - vnext).length_squared
            if currLen2 < minLen2:
                minLen2 = currLen2
                minIndex = iv
        
        minLen = math.sqrt(minLen2)
        
        return minLen, minIndex
        
    
    def RemoveMostObtuseVertex(self):
        maxAng = -1.0
        maxIndex = -1
        
        for iv in range(self.nrVertices):
            currAng = self.GetAngle(iv)
            if currAng > maxAng:
                maxAng = currAng
                maxIndex = iv
                
        if maxIndex >= 0:
            self.listVertices.pop(maxIndex)
    
    def InsertEdgeAtSharpestVertex(self, minPar, maxPar):
        minAng, minIndex = self.GetSharpestAngle()
        if minIndex < 0: raise Exception("minIndex < 0")
        
        dPar = maxPar - minPar
        
        verts = self.listVertices
        vprev, vcurr, vnext = verts[minIndex - 1], verts[minIndex], verts[minIndex + 1 - self.nrVertices]
        dirNext = vnext - vcurr
        dirPrev = vprev - vcurr
        
        parRND = mathutils.noise.random()
        par = minPar + (parRND * dPar)
        v1 = vcurr + (dirPrev * par)
        parRND = mathutils.noise.random()
        par = minPar + (parRND * dPar)
        v2 = vcurr + (dirNext * par)
        
        self.listVertices.pop(minIndex)
        self.listVertices.insert(minIndex, v2)
        self.listVertices.insert(minIndex, v1)
        
    
    # vertIndex of v1 of edge(v1, v2)
    def RemoveEdge(self, vertIndex, mergeAlgo):
        if self.nrVertices < 2: return
        
        verts = self.listVertices
        vcurr, vnext = verts[vertIndex], verts[vertIndex + 1 - self.nrVertices]
        
        vnew = None
        if mergeAlgo == "Vertex1":
            vnew = vcurr
        elif mergeAlgo == "Vertex2":
            vnew = vnext
        elif mergeAlgo == "Center":
            vnew = (vcurr + vnext) * 0.5
        elif mergeAlgo == "Random":
            parRND = mathutils.noise.random()
            vnew = vcurr + ((vnext - vcurr) * parRND)
        
        if vnew is None: raise("Unknown mergeAlgo: " + mergeAlgo)

        self.listVertices.pop(vertIndex)
        if vertIndex >= self.nrVertices: vertIndex = 0
        self.listVertices.pop(vertIndex)
        self.listVertices.insert(vertIndex, vnew)
        
    
    def RemoveShortEdges(self, trshLen, mergeAlgo):
        while True:
            if self.nrVertices < 4: break
            
            minLen, minIndex = self.GetShortestEdge()
            if minIndex < 0: break
            if minLen > trshLen: break
            
            # print("--", "self.RemoveEdge(minIndex, mergeAlgo)", self)
            self.RemoveEdge(minIndex, mergeAlgo)
            
    

    
    # v3Center should be ok for convex polygons -- be careful if that is not the case..
    @staticmethod
    def CalcPerpendicularDirection(v3Edge1, v3Edge2, v3Center):
        v3Edge12 = v3Edge2 - v3Edge1
        v3EdgeDir12 = v3Edge12.normalized()
        
        v3Edge1Center = v3Center - v3Edge1
        v3EdgeDir1Center = v3Edge1Center.normalized()
        
        projection = v3EdgeDir12.dot(v3Edge1Center)
        v3Perp = v3Edge1Center - (v3EdgeDir12 * projection)
        v3PerpDir = v3Perp.normalized()
    
        return v3PerpDir

        
    # v3Center should be ok for convex polygons -- be careful if that is not the case..
    @staticmethod
    def GetOffsetVertex(v3Prev, v3Curr, v3Next, edgeOffset, v3Center):
        perpDir1 = Polygon.CalcPerpendicularDirection(v3Prev, v3Curr, v3Center) * edgeOffset
        p0 = v3Prev + perpDir1
        p1 = v3Curr + perpDir1
        perpDir2 = Polygon.CalcPerpendicularDirection(v3Curr, v3Next, v3Center) * edgeOffset
        q0 = v3Curr + perpDir2
        q1 = v3Next + perpDir2
        
        closestPoint = Math.CalcClosestPointLines(p0, p1, q0, q1)
        
        return closestPoint
    
