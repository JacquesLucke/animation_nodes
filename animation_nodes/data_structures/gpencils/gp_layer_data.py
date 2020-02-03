import textwrap

class GPLayer:
    def __init__(self, layerName = None,
                       frames = None,
                       blendMode = None,
                       opacity = None,
                       passIndex = None):

        if layerName is None: layerName = "AN-Layer"
        if frames is None: frames = []
        if blendMode is None: blendMode = "REGULAR"
        if opacity is None: opacity = 1
        if passIndex is None: passIndex = 0

        self.frames = frames
        self.layerName = layerName
        self.blendMode = blendMode
        self.opacity = opacity
        self.passIndex = passIndex

    def __repr__(self):
        return textwrap.dedent(
        f"""AN Layer Object:
        Layer Name: {self.layerName}
        Frames: {len(self.frames)}
        Blend Mode: {self.blendMode}
        Opacity: {self.opacity}
        Pass Index: {self.passIndex}""")

    def copy(self):
        return GPLayer(self.layerName, [frame.copy() for frame in self.frames],
                       self.blendMode, self.opacity, self.passIndex)
