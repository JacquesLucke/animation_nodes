import bpy
import bmesh
import mathutils
from mathutils import *
from math import *

from . import DelaunayVoronoi

# utility properties & functions
defaultResolutionSynthesis = 16

# list of safe functions for eval()
safe_list = ['math', 'acos', 'asin', 'atan', 'atan2', 'ceil', 'cos', 'cosh',
             'degrees', 'e', 'exp', 'fabs', 'floor', 'fmod', 'frexp', 'hypot',
             'ldexp', 'log', 'log10', 'modf', 'pi', 'pow', 'radians',
             'sin', 'sinh', 'sqrt', 'tan', 'tanh']

# use the list to filter the local namespace
safe_dict = dict((k, globals().get(k, None)) for k in safe_list)

# A very simple "bridge" tool.
# Connects two equally long vertex rows with faces.
# Returns a list of the new faces (list of  lists)
#
# vertIdx1 ... First vertex list (list of vertex indices).
# vertIdx2 ... Second vertex list (list of vertex indices).
# closed ... Creates a loop (first & last are closed).
# flipped ... Invert the normal of the face(s).
#
# Note: You can set vertIdx1 to a single vertex index to create
#       a fan/star of faces.
# Note: If both vertex idx list are the same length they have
#       to have at least 2 vertices.
def createFaces(vertIdx1, vertIdx2, closed=False, flipped=False):
    faces = []

    if not vertIdx1 or not vertIdx2:
        return None

    if len(vertIdx1) < 2 and len(vertIdx2) < 2:
        return None

    fan = False
    if (len(vertIdx1) != len(vertIdx2)):
        if (len(vertIdx1) == 1 and len(vertIdx2) > 1):
            fan = True
        else:
            return None

    total = len(vertIdx2)

    if closed:
        # Bridge the start with the end.
        if flipped:
            face = [
                vertIdx1[0],
                vertIdx2[0],
                vertIdx2[total - 1]]
            if not fan:
                face.append(vertIdx1[total - 1])
            faces.append(face)

        else:
            face = [vertIdx2[0], vertIdx1[0]]
            if not fan:
                face.append(vertIdx1[total - 1])
            face.append(vertIdx2[total - 1])
            faces.append(face)

    # Bridge the rest of the faces.
    for num in range(total - 1):
        if flipped:
            if fan:
                face = [vertIdx2[num], vertIdx1[0], vertIdx2[num + 1]]
            else:
                face = [vertIdx2[num], vertIdx1[num],
                    vertIdx1[num + 1], vertIdx2[num + 1]]
            faces.append(face)
        else:
            if fan:
                face = [vertIdx1[0], vertIdx2[num], vertIdx2[num + 1]]
            else:
                face = [vertIdx1[num], vertIdx2[num],
                    vertIdx2[num + 1], vertIdx1[num + 1]]
            faces.append(face)

    return faces

    
class VoronoiSurface:
    def __init__(self, locations, xbuff, ybuff):
        self.locations = locations
        self.xbuff = xbuff
        self.ybuff = ybuff

    def Calculate(self):
        rvVertices = []
        rvFaces = []
        
        rawVertices, rawFacesDict = DelaunayVoronoi.computeVoronoiDiagram(self.locations, self.xbuff, self.ybuff, polygonsOutput=True, formatOutput=True, closePoly=False)
        
        for rawVert in rawVertices: 
            rvVertices.append(mathutils.Vector((rawVert[0], rawVert[1], 0.0)))    # TODO: is it possible to keep/calc z?
            
        # need to remove possible doubles, for now
        for key, val in rawFacesDict.items(): 
            newVal = []
            for currI in val:
                if not currI in newVal: newVal.append(currI)
            if len(newVal) >= 3: rvFaces.append(newVal)

        return rvVertices, rvFaces

        
class HeightFunctionCartesianSurface:
    def __init__(self, equation, startX, endX, startY, endY):
        self.equation = equation
        self.startX = startX
        self.endX = endX
        self.startY = startY
        self.endY = endY

    def Calculate(self, resX, resY):
        rvVertices = []
        rvFaces = []
        
        try: expr_args = (compile(self.equation, __file__, 'eval'), {"__builtins__": None}, safe_dict)
        except: return rvVertices, rvFaces

        delta_x = (self.endX - self.startX) / float(resX - 1)
        delta_y = (self.endY - self.startY) / float(resY - 1)
        
        edgeloop_prev = []
        for row_x in range(resX):
            edgeloop_cur = []
            x = self.startX + row_x * delta_x

            for row_y in range(resY):
                y = self.startY + row_y * delta_y
                z = 0.0

                safe_dict['x'] = x
                safe_dict['y'] = y

                try: z = float(eval(*expr_args))
                except: return [], []

                edgeloop_cur.append(len(rvVertices))
                rvVertices.append(Vector((x, y, z)))

            if len(edgeloop_prev) > 0:
                try: faces_row = createFaces(edgeloop_prev, edgeloop_cur)
                except: return [], []
                rvFaces.extend(faces_row)

            edgeloop_prev = edgeloop_cur

        return rvVertices, rvFaces

        
class HeightFunctionPolarSurface:
    def __init__(self, equation, startR, endR, startA, endA):
        self.equation = equation
        self.startR = startR
        self.endR = endR
        self.startA = startA
        self.endA = endA

    def Calculate(self, resR, resA):
        rvVertices = []
        rvFaces = []
        
        try: expr_args = (compile(self.equation, __file__, 'eval'), {"__builtins__": None}, safe_dict)
        except: return rvVertices, rvFaces

        delta_r = (self.endR - self.startR) / float(resR - 1)
        delta_a = (self.endA - self.startA) / float(resA - 1)
        
        edgeloop_prev = []
        for row_r in range(resR):
            edgeloop_cur = []
            r = self.startR + row_r * delta_r

            for row_a in range(resA):
                a = self.startA + row_a * delta_a
                z = 0.0

                safe_dict['r'] = r
                safe_dict['a'] = a

                try: z = float(eval(*expr_args))
                except: return [], []

                x = r * cos(a)
                y = r * sin(a)

                edgeloop_cur.append(len(rvVertices))
                rvVertices.append(Vector((x, y, z)))

            if len(edgeloop_prev) > 0:
                try: faces_row = createFaces(edgeloop_prev, edgeloop_cur)
                except: return [], []
                rvFaces.extend(faces_row)

            edgeloop_prev = edgeloop_cur
        
        return rvVertices, rvFaces
        