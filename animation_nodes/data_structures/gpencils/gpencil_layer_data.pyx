# cython: profile=True
import textwrap
from .. lists.base_lists cimport DoubleList

class GPLayer:
    def __init__(self, layerName = None,
                       frames = None,
                       frameNumbers = None,
                       blendMode = None,
                       opacity = None,
                       passIndex = None):

        if layerName is None: layerName = "AN-Layer"
        if frames is None: frames = []
        if frameNumbers is None: frameNumbers = DoubleList()
        if blendMode is None: blendMode = "REGULAR"
        if opacity is None: opacity = 1
        if passIndex is None: passIndex = 0

        self.frames = frames
        self.layerName = layerName
        self.frameNumbers = frameNumbers
        self.blendMode = blendMode
        self.opacity = opacity
        self.passIndex = passIndex

    def __repr__(self):
        return textwrap.dedent(
        f"""AN Layer Object:
        Layer Name: {self.layerName}
        Frames: {len(self.frames)}
        Frame Numbers: {self.frameNumbers}
        Blend Mode: {self.blendMode}
        Opacity: {self.opacity}
        Pass Index: {self.passIndex}""")

    def copy(self):
        return GPLayer(self.layerName, self.frames, self.frameNumbers, self.blendMode, self.opacity, self.passIndex)
