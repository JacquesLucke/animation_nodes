import textwrap
from .. lists.base_lists import DoubleList, Vector3DList

class GPStroke:
    def __init__(self, vertices = None, strengths = None, pressures = None,
                 uvRotations = None, lineWidth = None, drawCyclic = None,
                 startCapMode = None, endCapMode = None, materialIndex = None,
                 displayMode = None):

        if vertices is None: vertices = Vector3DList()
        if strengths is None: strengths = DoubleList()
        if pressures is None: pressures = DoubleList()
        if uvRotations is None: uvRotations = DoubleList()
        if lineWidth is None: lineWidth = 250
        if drawCyclic is None: drawCyclic = False
        if startCapMode is None: startCapMode = "ROUND"
        if endCapMode is None: endCapMode = "ROUND"
        if materialIndex is None: materialIndex = 0
        if displayMode is None: displayMode = "3DSPACE"

        self.vertices = vertices
        self.strengths = strengths
        self.pressures = pressures
        self.uvRotations = uvRotations
        self.lineWidth = lineWidth
        self.drawCyclic = drawCyclic
        self.startCapMode = startCapMode
        self.endCapMode = endCapMode
        self.materialIndex = materialIndex
        self.displayMode = displayMode

    def __repr__(self):
        return textwrap.dedent(
            f"""AN Stroke Object:
            Points: {len(self.vertices)}
            Line Width: {self.lineWidth}
            Cyclic: {self.drawCyclic}
            Start Cap Mode: {self.startCapMode}
            End Cap Mode: {self.endCapMode}
            Material Index: {self.materialIndex}
            Display Mode: {self.displayMode}""")

    def copy(self):
        return GPStroke(self.vertices.copy(), self.strengths.copy(), self.pressures.copy(),
                        self.uvRotations.copy(), self.lineWidth, self.drawCyclic,
                        self.startCapMode, self.endCapMode, self.materialIndex,
                        self.displayMode)
