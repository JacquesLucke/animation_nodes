def gridQuadPolygonIndices(xDivisions, yDivisions):
    polygons = []
    for i in range(0, (xDivisions - 1) * yDivisions, yDivisions):
        for j in range(i, i + yDivisions - 1):
            polygons.append((j, j + 1, j + yDivisions + 1, j + yDivisions))
    return polygons