from ... data_structures import EdgeIndicesList

class GridMeshIndices:
    @classmethod
    def quadPolygons(cls, xDivisions, yDivisions, joinHorizontal = False, joinVertical = False):
        polygons = []
        polygons.extend(cls.innerQuadPolygons(xDivisions, yDivisions))
        if joinHorizontal:
            polygons.extend(cls.joinHorizontalEdgesQuadPolygons(xDivisions, yDivisions))
        if joinVertical:
            polygons.extend(cls.joinVerticalEdgesQuadPolygons(xDivisions, yDivisions))
        if joinHorizontal and joinVertical:
            polygons.append(cls.joinCornersWithQuad(xDivisions, yDivisions))
        return polygons

    @staticmethod
    def innerQuadPolygons(xDivisions, yDivisions):
        polygons = []
        for i in range(0, (xDivisions - 1) * yDivisions, yDivisions):
            for j in range(i, i + yDivisions - 1):
                polygons.append((j, j + 1, j + yDivisions + 1, j + yDivisions))
        return polygons

    @staticmethod
    def joinHorizontalEdgesQuadPolygons(xDivisions, yDivisions):
        polygons = []
        offset = yDivisions * (xDivisions - 1)
        for i in range(yDivisions - 1):
            polygons.append((i, i + offset, i + offset + 1, i + 1))
        return polygons

    @staticmethod
    def joinVerticalEdgesQuadPolygons(xDivisions, yDivisions):
        polygons = []
        for i in range(0, (xDivisions - 1) * yDivisions, yDivisions):
            polygons.append((i, i + yDivisions, i + 2 * yDivisions - 1, i + yDivisions - 1))
        return polygons

    @staticmethod
    def joinCornersWithQuad(xDivisions, yDivisions):
        return (0, yDivisions - 1, yDivisions * xDivisions - 1, yDivisions * (xDivisions - 1))

    @staticmethod
    def innerQuadEdges(xDivisions, yDivisions):
        edges = EdgeIndicesList()
        for i in range((xDivisions - 1) * yDivisions):
            edges.append((i, i + yDivisions))
        for i in range(yDivisions - 1):
            for j in range(xDivisions):
                firstIndex = i + j * yDivisions
                edges.append((firstIndex, firstIndex + 1))
        return edges
