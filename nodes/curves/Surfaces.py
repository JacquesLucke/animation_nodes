import bpy
import bmesh

from . import Math
from . import Curves

class LoftedSurface:
    def __init__(self, blenderObjectRail1, blenderObjectRail2):
        self.curveRail1 = Curves.Curve(blenderObjectRail1)
        self.curveRail2 = Curves.Curve(blenderObjectRail2)
        
    def Calculate(self, resAlong, resAcross):
        pointsRail1 = self.curveRail1.SampleWorld(resAlong)
        pointsRail2 = self.curveRail2.SampleWorld(resAlong)
        
        fltResAcrossM1 = float(resAcross - 1)
        rvVertices = []
        for iAlong in range(resAlong):
            pointRail1 = pointsRail1[iAlong]
            pointRail2 = pointsRail2[iAlong]
            diff12 = pointRail2 - pointRail1
            for iAcross in range(resAcross):
                parAcross = float(iAcross) / fltResAcrossM1
                rvVertices.append(pointRail1 + (diff12 * parAcross))
                
        rvFaces = []
        for iAlong in range(resAlong - 1):
            currAlong = iAlong * resAcross
            nextAlong = currAlong + resAcross
            for iAcross in range(resAcross - 1):
                indexBL = currAlong + iAcross
                indexTL = indexBL + 1
                indexBR = nextAlong + iAcross
                indexTR = indexBR + 1
                
                rvFaces.append([indexBL, indexBR, indexTR, indexTL])
        
        return rvVertices, rvFaces

        
class RevolvedSurface:
    def __init__(self, blenderObjectAxis, blenderObjectProfile):
        self.curveAxis = Curves.Curve(blenderObjectAxis)
        self.curveProfile = Curves.Curve(blenderObjectProfile)
        
    def Calculate(self, resAlong, resAcross):
        worldPointsAxis = self.curveAxis.SampleWorld(resAlong)
        worldPointsProfile = self.curveProfile.SampleWorld(resAlong)
        worldDerivativesAxis = self.curveAxis.SampleDerivativesWorld(resAlong)
        
        rvVertices = []
        for iAlong in range(resAlong):
            center = worldPointsAxis[iAlong]
            pointProfile = worldPointsProfile[iAlong]
            dirX = (pointProfile - center)
            radius = dirX.magnitude
            dirY = worldDerivativesAxis[iAlong].cross(dirX).normalized()
            dirX.normalize()
            
            currPointsAcross = Math.GenerateCircle(center, radius, dirX, dirY, resAcross)
            for iAcross in range(resAcross):
                rvVertices.append(currPointsAcross[iAcross])
        
        rvFaces = []
        for iAlong in range(resAlong - 1):
            currAlong = iAlong * resAcross
            nextAlong = currAlong + resAcross
            for iAcross in range(resAcross - 1):
                indexBL = currAlong + iAcross
                indexTL = indexBL + 1
                indexBR = nextAlong + iAcross
                indexTR = indexBR + 1
                
                rvFaces.append([indexBL, indexBR, indexTR, indexTL])
        
        for iAlong in range(resAlong - 1):
            indexTL = iAlong * resAcross
            indexTR = indexTL + resAcross
            indexBL = indexTL + resAcross - 1
            indexBR = indexTR + resAcross - 1
            
            rvFaces.append([indexBL, indexBR, indexTR, indexTL])
        
        return rvVertices, rvFaces
    
    
class SweptSurface:
    def __init__(self, blenderObjectRail, blenderObjectProfile):
        self.curveRail = Curves.Curve(blenderObjectRail)
        self.curveProfile = Curves.Curve(blenderObjectProfile)
        
    def Calculate(self, resAlong, resAcross):
        worldPointsRail = self.curveRail.SampleWorld(resAlong)
        localDerivativesRail = self.curveRail.SampleDerivatives(resAlong)
        worldMatrixRail = self.curveRail.worldMatrix
        worldMatrixRailInv = worldMatrixRail.inverted()
        
        localPointsProfile = self.curveProfile.Sample(resAcross)
        currWorldMatrixProfile = self.curveProfile.worldMatrix
        
        rvVertices = []
        prevDerivativeRail = localDerivativesRail[0]
        for iRail in range(resAlong):
            currDerivativeRail = localDerivativesRail[iRail]
            localRotMatRail = Math.CalcRotationMatrix(prevDerivativeRail, currDerivativeRail)
            
            currLocalProfileToLocalRail = worldMatrixRailInv * currWorldMatrixProfile       
            worldPointsProfile = []
            for iProfile in range(resAcross):
                pointProfileLocalToRail = currLocalProfileToLocalRail * localPointsProfile[iProfile]
                rotatedPointProfile = localRotMatRail * pointProfileLocalToRail
                worldPointsProfile.append(worldMatrixRail * rotatedPointProfile)
                
            worldOffsetsProfile = []
            worldPoint0Profile = worldPointsProfile[0]
            for iProfile in range(resAcross): worldOffsetsProfile.append(worldPointsProfile[iProfile] - worldPoint0Profile)
            
            for iProfile in range(resAcross):
                currVert = worldPointsRail[iRail] + worldOffsetsProfile[iProfile]
                rvVertices.append(currVert)
                
            prevDerivativeRail = currDerivativeRail
            currWorldMatrixProfile = worldMatrixRail * localRotMatRail * currLocalProfileToLocalRail

        rvFaces = []
        for iAlong in range(resAlong - 1):
            currAlong = iAlong * resAcross
            nextAlong = currAlong + resAcross
            for iAcross in range(resAcross - 1):
                indexBL = currAlong + iAcross
                indexTL = indexBL + 1
                indexBR = nextAlong + iAcross
                indexTR = indexBR + 1
                
                rvFaces.append([indexBL, indexBR, indexTR, indexTL])
        
        return rvVertices, rvFaces
    
    
class BirailedSurface:
    def __init__(self, blenderObjectRail1, blenderObjectRail2, blenderObjectProfile):
        self.curveRail1 = Curves.Curve(blenderObjectRail1)
        self.curveRail2 = Curves.Curve(blenderObjectRail2)
        self.curveProfile = Curves.Curve(blenderObjectProfile)
        
    def Calculate(self, resAlong, resAcross):
        worldMatrixRail1 = self.curveRail1.worldMatrix
        worldMatrixProfile = self.curveProfile.worldMatrix
        
        localPointsProfile = self.curveProfile.Sample(resAcross)
        worldPointsRail1 = self.curveRail1.SampleWorld(resAlong)
        localDerivativesRail1 = self.curveRail1.SampleDerivatives(resAlong)
        worldPointsRail2 = self.curveRail2.SampleWorld(resAlong)
        
        rvVertices = []
        currWorldMatrixProfile = worldMatrixProfile
        worldMatrixRail1Inv = worldMatrixRail1.inverted()
        prevDerivativeRail1 = localDerivativesRail1[0]
        for iRail in range(resAlong):
            currDerivativeRail1 = localDerivativesRail1[iRail]
            localRotMatRail1 = Math.CalcRotationMatrix(prevDerivativeRail1, currDerivativeRail1)
            
            currLocalProfileToLocalRail1 = worldMatrixRail1Inv * currWorldMatrixProfile       
            worldPointsProfileRail1 = []
            for iProfile in range(resAcross):
                pointProfileLocalToRail1 = currLocalProfileToLocalRail1 * localPointsProfile[iProfile]
                rotatedPointProfile = localRotMatRail1 * pointProfileLocalToRail1
                worldPointsProfileRail1.append(worldMatrixRail1 * rotatedPointProfile)
                
            worldOffsetsProfileRail1 = []
            worldPoint0ProfileRail1 = worldPointsProfileRail1[0]
            for iProfile in range(resAcross): worldOffsetsProfileRail1.append(worldPointsProfileRail1[iProfile] - worldPoint0ProfileRail1)
                
            worldStartPointProfileRail1 = worldPointsRail1[iRail]
            worldEndPointProfileRail1 = worldStartPointProfileRail1 + worldOffsetsProfileRail1[-1]
            v3From = worldEndPointProfileRail1 - worldStartPointProfileRail1
            v3To = worldPointsRail2[iRail] - worldStartPointProfileRail1
            scaleFactorRail2 = v3To.magnitude / v3From.magnitude
            rotMatRail2 = Math.CalcRotationMatrix(v3From, v3To)
            
            worldOffsetsProfileRail2 = []
            for iProfile in range(resAcross):
                offsetProfileRail1 = worldOffsetsProfileRail1[iProfile]
                worldOffsetsProfileRail2.append(rotMatRail2 * (offsetProfileRail1 * scaleFactorRail2))
            
            for iProfile in range(resAcross):
                currVert = worldPointsRail1[iRail] + worldOffsetsProfileRail2[iProfile]
                rvVertices.append(currVert)
                
            prevDerivativeRail1 = currDerivativeRail1
            currWorldMatrixProfile = worldMatrixRail1 * localRotMatRail1 * currLocalProfileToLocalRail1

        rvFaces = []
        for iAlong in range(resAlong - 1):
            currAlong = iAlong * resAcross
            nextAlong = currAlong + resAcross
            for iAcross in range(resAcross - 1):
                indexBL = currAlong + iAcross
                indexTL = indexBL + 1
                indexBR = nextAlong + iAcross
                indexTR = indexBR + 1
                
                rvFaces.append([indexBL, indexBR, indexTR, indexTL])
        
        return rvVertices, rvFaces
    
    
class SweptAndMorphedSurface:
    def __init__(self, blenderObjectRail, blenderObjectBeginProfile, blenderObjectEndProfile):
        self.curveRail = Curves.Curve(blenderObjectRail)
        self.curveBeginProfile = Curves.Curve(blenderObjectBeginProfile)
        self.curveEndProfile = Curves.Curve(blenderObjectEndProfile)
        
    def Calculate(self, resAlong, resAcross):
        worldMatrixRail = self.curveRail.worldMatrix
        worldMatrixRailInv = worldMatrixRail.inverted()
        worldMatrixBeginProfile = self.curveBeginProfile.worldMatrix
        worldMatrixEndProfile = self.curveEndProfile.worldMatrix
        
        # 1. rail
        worldPointsRail = self.curveRail.SampleWorld(resAlong)
        localDerivativesRail = self.curveRail.SampleDerivatives(resAlong)
        
        # 2. beginProfile
        localPointsBeginProfile = self.curveBeginProfile.Sample(resAcross)
        currWorldMatrixBeginProfile = worldMatrixBeginProfile
        prevDerivativeRail = localDerivativesRail[0]
        vertsBeginProfile = []
        for iRail in range(resAlong):
            currDerivativeRail = localDerivativesRail[iRail]
            localRotMatRail = Math.CalcRotationMatrix(prevDerivativeRail, currDerivativeRail)
            
            currLocalProfileToLocalRail = worldMatrixRailInv * currWorldMatrixBeginProfile       
            worldPointsProfile = []
            for iProfile in range(resAcross):
                pointProfileLocalToRail = currLocalProfileToLocalRail * localPointsBeginProfile[iProfile]
                rotatedPointProfile = localRotMatRail * pointProfileLocalToRail
                worldPointsProfile.append(worldMatrixRail * rotatedPointProfile)
                
            worldOffsetsProfile = []
            worldPoint0Profile = worldPointsProfile[0]
            for iProfile in range(resAcross): worldOffsetsProfile.append(worldPointsProfile[iProfile] - worldPoint0Profile)
            
            for iProfile in range(resAcross):
                currVert = worldPointsRail[iRail] + worldOffsetsProfile[iProfile]
                vertsBeginProfile.append(currVert)
                
            prevDerivativeRail = currDerivativeRail
            currWorldMatrixBeginProfile = worldMatrixRail * localRotMatRail * currLocalProfileToLocalRail
    
        # 3. endProfile
        localPointsEndProfile = self.curveEndProfile.Sample(resAcross)
        currWorldMatrixEndProfile = worldMatrixEndProfile
        prevDerivativeRail = localDerivativesRail[-1]
        vertsEndProfile = [None] * (resAlong * resAcross)
        for iRail in reversed(range(resAlong)):
            currDerivativeRail = localDerivativesRail[iRail]
            localRotMatRail = Math.CalcRotationMatrix(prevDerivativeRail, currDerivativeRail)
            
            currLocalProfileToLocalRail = worldMatrixRailInv * currWorldMatrixEndProfile       
            worldPointsProfile = []
            for iProfile in range(resAcross):
                pointProfileLocalToRail = currLocalProfileToLocalRail * localPointsEndProfile[iProfile]
                rotatedPointProfile = localRotMatRail * pointProfileLocalToRail
                worldPointsProfile.append(worldMatrixRail * rotatedPointProfile)
                
            worldOffsetsProfile = []
            worldPoint0Profile = worldPointsProfile[0]
            for iProfile in range(resAcross): worldOffsetsProfile.append(worldPointsProfile[iProfile] - worldPoint0Profile)
            
            for iProfile in range(resAcross):
                iVert = (resAcross * iRail) + iProfile
                currVert = worldPointsRail[iRail] + worldOffsetsProfile[iProfile]
                vertsEndProfile[iVert] = currVert
                
            prevDerivativeRail = currDerivativeRail
            currWorldMatrixEndProfile = worldMatrixRail * localRotMatRail * currLocalProfileToLocalRail
    
        # 4. morph
        rvVertices = []
        fltResRailMin1 = float(resAlong - 1)
        for iRail in range(resAlong):
            weightEnd = float(iRail) / fltResRailMin1
            weightBegin = 1.0 - weightEnd
            for iProfile in range(resAcross):
                iVert = (resAcross * iRail) + iProfile
                vertBegin = vertsBeginProfile[iVert]
                vertEnd = vertsEndProfile[iVert]
                vertMorphed = (vertBegin * weightBegin) + (vertEnd * weightEnd)
                rvVertices.append(vertMorphed)

        rvFaces = []
        for iAlong in range(resAlong - 1):
            currAlong = iAlong * resAcross
            nextAlong = currAlong + resAcross
            for iAcross in range(resAcross - 1):
                indexBL = currAlong + iAcross
                indexTL = indexBL + 1
                indexBR = nextAlong + iAcross
                indexTR = indexBR + 1
                
                rvFaces.append([indexBL, indexBR, indexTR, indexTL])
        
        return rvVertices, rvFaces
    
    
class BirailedAndMorphedSurface:
    def __init__(self, blenderObjectRail1, blenderObjectRail2, blenderObjectBeginProfile, blenderObjectEndProfile):
        self.curveRail1 = Curves.Curve(blenderObjectRail1)
        self.curveRail2 = Curves.Curve(blenderObjectRail2)
        self.curveBeginProfile = Curves.Curve(blenderObjectBeginProfile)
        self.curveEndProfile = Curves.Curve(blenderObjectEndProfile)
        
    def Calculate(self, resAlong, resAcross):
        worldMatrixRail1 = self.curveRail1.worldMatrix
        worldMatrixBeginProfile = self.curveBeginProfile.worldMatrix
        worldMatrixEndProfile = self.curveEndProfile.worldMatrix
        
        # 1. rail
        worldPointsRail1 = self.curveRail1.SampleWorld(resAlong)
        localDerivativesRail1 = self.curveRail1.SampleDerivatives(resAlong)
        worldPointsRail2 = self.curveRail2.SampleWorld(resAlong)
        
        # 2. beginProfile
        localPointsBeginProfile = self.curveBeginProfile.Sample(resAcross)
        currWorldMatrixBeginProfile = worldMatrixBeginProfile
        worldMatrixRail1Inv = worldMatrixRail1.inverted()
        prevDerivativeRail1 = localDerivativesRail1[0]
        vertsBeginProfile = []
        for iRail in range(resAlong):
            currDerivativeRail1 = localDerivativesRail1[iRail]
            localRotMatRail1 = Math.CalcRotationMatrix(prevDerivativeRail1, currDerivativeRail1)
            
            currLocalBeginProfileToLocalRail1 = worldMatrixRail1Inv * currWorldMatrixBeginProfile       
            worldPointsBeginProfileRail1 = []
            for iProfile in range(resAcross):
                pointBeginProfileLocalToRail1 = currLocalBeginProfileToLocalRail1 * localPointsBeginProfile[iProfile]
                rotatedPointProfile = localRotMatRail1 * pointBeginProfileLocalToRail1
                worldPointsBeginProfileRail1.append(worldMatrixRail1 * rotatedPointProfile)
                
            worldOffsetsBeginProfileRail1 = []
            worldPoint0BeginProfileRail1 = worldPointsBeginProfileRail1[0]
            for iProfile in range(resAcross): worldOffsetsBeginProfileRail1.append(worldPointsBeginProfileRail1[iProfile] - worldPoint0BeginProfileRail1)
                
            worldStartPointBeginProfileRail1 = worldPointsRail1[iRail]
            worldEndPointBeginProfileRail1 = worldStartPointBeginProfileRail1 + worldOffsetsBeginProfileRail1[-1]
            v3From = worldEndPointBeginProfileRail1 - worldStartPointBeginProfileRail1
            v3To = worldPointsRail2[iRail] - worldStartPointBeginProfileRail1
            scaleFactorRail2 = v3To.magnitude / v3From.magnitude
            rotMatRail2 = Math.CalcRotationMatrix(v3From, v3To)
            
            worldOffsetsBeginProfileRail2 = []
            for iProfile in range(resAcross):
                offsetBeginProfileRail1 = worldOffsetsBeginProfileRail1[iProfile]
                worldOffsetsBeginProfileRail2.append(rotMatRail2 * (offsetBeginProfileRail1 * scaleFactorRail2))
            
            for iProfile in range(resAcross):
                currVert = worldPointsRail1[iRail] + worldOffsetsBeginProfileRail2[iProfile]
                vertsBeginProfile.append(currVert)
                
            prevDerivativeRail1 = currDerivativeRail1
            currWorldMatrixBeginProfile = worldMatrixRail1 * localRotMatRail1 * currLocalBeginProfileToLocalRail1
        
        # 3. endProfile
        localPointsEndProfile = self.curveEndProfile.Sample(resAcross)
        currWorldMatrixEndProfile = worldMatrixEndProfile
        worldMatrixRail1Inv = worldMatrixRail1.inverted()
        prevDerivativeRail1 = localDerivativesRail1[-1]
        vertsEndProfile = [None] * (resAlong * resAcross)
        for iRail in reversed(range(resAlong)):
            currDerivativeRail1 = localDerivativesRail1[iRail]
            localRotMatRail1 = Math.CalcRotationMatrix(prevDerivativeRail1, currDerivativeRail1)
            
            currLocalEndProfileToLocalRail1 = worldMatrixRail1Inv * currWorldMatrixEndProfile       
            worldPointsEndProfileRail1 = []
            for iProfile in range(resAcross):
                pointEndProfileLocalToRail1 = currLocalEndProfileToLocalRail1 * localPointsEndProfile[iProfile]
                rotatedPointProfile = localRotMatRail1 * pointEndProfileLocalToRail1
                worldPointsEndProfileRail1.append(worldMatrixRail1 * rotatedPointProfile)
                
            worldOffsetsEndProfileRail1 = []
            worldPoint0EndProfileRail1 = worldPointsEndProfileRail1[0]
            for iProfile in range(resAcross): worldOffsetsEndProfileRail1.append(worldPointsEndProfileRail1[iProfile] - worldPoint0EndProfileRail1)
                
            worldStartPointEndProfileRail1 = worldPointsRail1[iRail]
            worldEndPointEndProfileRail1 = worldStartPointEndProfileRail1 + worldOffsetsEndProfileRail1[-1]
            v3From = worldEndPointEndProfileRail1 - worldStartPointEndProfileRail1
            v3To = worldPointsRail2[iRail] - worldStartPointEndProfileRail1
            scaleFactorRail2 = v3To.magnitude / v3From.magnitude
            rotMatRail2 = Math.CalcRotationMatrix(v3From, v3To)
            
            worldOffsetsEndProfileRail2 = []
            for iProfile in range(resAcross):
                offsetEndProfileRail1 = worldOffsetsEndProfileRail1[iProfile]
                worldOffsetsEndProfileRail2.append(rotMatRail2 * (offsetEndProfileRail1 * scaleFactorRail2))
            
            for iProfile in range(resAcross):
                iVert = (resAcross * iRail) + iProfile
                currVert = worldPointsRail1[iRail] + worldOffsetsEndProfileRail2[iProfile]
                vertsEndProfile[iVert] = currVert
                
            prevDerivativeRail1 = currDerivativeRail1
            currWorldMatrixEndProfile = worldMatrixRail1 * localRotMatRail1 * currLocalEndProfileToLocalRail1
        
        # 4. morph
        rvVertices = []
        fltResRailMin1 = float(resAlong - 1)
        for iRail in range(resAlong):
            weightEnd = float(iRail) / fltResRailMin1
            weightBegin = 1.0 - weightEnd
            for iProfile in range(resAcross):
                iVert = (resAcross * iRail) + iProfile
                vertBegin = vertsBeginProfile[iVert]
                vertEnd = vertsEndProfile[iVert]
                vertMorphed = (vertBegin * weightBegin) + (vertEnd * weightEnd)
                rvVertices.append(vertMorphed)

        rvFaces = []
        for iAlong in range(resAlong - 1):
            currAlong = iAlong * resAcross
            nextAlong = currAlong + resAcross
            for iAcross in range(resAcross - 1):
                indexBL = currAlong + iAcross
                indexTL = indexBL + 1
                indexBR = nextAlong + iAcross
                indexTR = indexBR + 1
                
                rvFaces.append([indexBL, indexBR, indexTR, indexTL])
        
        return rvVertices, rvFaces
