def tubeQuadPolygonIndices(xDivisions, yDivisions):
    polygons = []
    polygons.extend(gridQuadPolygonIndices(xDivisions, yDivisions))
    polygons.extend(gridEndEdgesQuadPolygonIndices(xDivisions, yDivisions))
    return polygons

def gridQuadPolygonIndices(xDivisions, yDivisions):
    polygons = []
    for i in range(0, (xDivisions - 1) * yDivisions, yDivisions):
        for j in range(i, i + yDivisions - 1):
            polygons.append((j, j + 1, j + yDivisions + 1, j + yDivisions))
    return polygons
    
def gridEndEdgesQuadPolygonIndices(xDivisions, yDivisions):
    polygons = []
    for i in range(0, (xDivisions - 1) * yDivisions, yDivisions):
        polygons.append((i, i + yDivisions, i + 2 * yDivisions - 1, i + yDivisions - 1))
    return polygons