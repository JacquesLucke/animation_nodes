import textwrap
from ... data_structures.color import Color
from .. lists.base_lists import FloatList, Vector3DList, ColorList
from ... data_structures.color import Color

class GPStroke:
    def __init__(self, vertices = None, strengths = None, pressures = None,
                 uvRotations = None, vertexColors = None, lineWidth = None,
                 hardness = None, useCyclic = None, startCapMode = None,
                 endCapMode = None, vertexColorFill = None, materialIndex = None,
                 displayMode = None):

        if vertices is None: vertices = Vector3DList()
        if strengths is None: strengths = FloatList()
        if pressures is None: pressures = FloatList()
        if uvRotations is None: uvRotations = FloatList()
        if vertexColors is None: vertexColors = ColorList()
        if lineWidth is None: lineWidth = 250
        if hardness is None: hardness = 1
        if useCyclic is None: useCyclic = False
        if startCapMode is None: startCapMode = "ROUND"
        if endCapMode is None: endCapMode = "ROUND"
        if vertexColorFill is None: vertexColorFill = Color((0, 0, 0, 0))
        if materialIndex is None: materialIndex = 0
        if displayMode is None: displayMode = "3DSPACE"

        self.vertices = vertices
        self.strengths = strengths
        self.pressures = pressures
        self.uvRotations = uvRotations
        self.vertexColors = vertexColors
        self.lineWidth = lineWidth
        self.hardness = hardness
        self.useCyclic = useCyclic
        self.startCapMode = startCapMode
        self.endCapMode = endCapMode
        self.vertexColorFill = vertexColorFill
        self.materialIndex = materialIndex
        self.displayMode = displayMode

    def __repr__(self):
        return textwrap.dedent(
            f"""AN Stroke Object:
            Points: {len(self.vertices)}
            Line Width: {self.lineWidth}
            Hardeness: {self.hardness}
            Cyclic: {self.useCyclic}
            Start Cap Mode: {self.startCapMode}
            End Cap Mode: {self.endCapMode}
            Vertex Color Fill: {self.vertexColorFill}
            Material Index: {self.materialIndex}
            Display Mode: {self.displayMode}""")

    def copy(self):
        return GPStroke(self.vertices.copy(), self.strengths.copy(), self.pressures.copy(),
                        self.uvRotations.copy(), self.vertexColors.copy(), self.lineWidth,
                        self.hardness, self.useCyclic, self.startCapMode, self.endCapMode,
                        self.vertexColorFill, self.materialIndex, self.displayMode)
