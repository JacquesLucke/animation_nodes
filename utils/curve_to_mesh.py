def loftSplines(spline1, spline2, splineSamples, surfaceSamples):
    samples1 = spline1.getSamples(splineSamples)
    samples2 = spline2.getSamples(splineSamples)
    
    vertices = []
    for start, end in zip(samples1, samples2):
        for i in range(surfaceSamples):
            influence = i / (surfaceSamples - 1)
            vertices.append(start * influence + end * (1 - influence))
            
    polygons = []
    for i in range(0, (splineSamples - 1) * surfaceSamples, surfaceSamples):
        for j in range(i, i + surfaceSamples - 1):
            polygons.append((j, j + 1, j + surfaceSamples + 1, j + surfaceSamples))
            
    return vertices, polygons