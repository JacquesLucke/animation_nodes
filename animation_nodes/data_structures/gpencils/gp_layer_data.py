import textwrap
from .. color import Color

class GPLayer:
    def __init__(self, layerName = None,
                       frames = None,
                       blendMode = None,
                       opacity = None,
                       useLights = None,
                       tintColor = None,
                       tintFactor = None,
                       lineChange = None,
                       passIndex = None,
                       invertAsMask = None,
                       maskLayers = None):

        if layerName is None: layerName = "AN-Layer"
        if frames is None: frames = []
        if blendMode is None: blendMode = "REGULAR"
        if opacity is None: opacity = 1
        if useLights is None: useLights = True
        if tintColor is None: tintColor = Color((0, 0, 0, 0))
        if tintFactor is None: tintFactor = 0
        if lineChange is None: lineChange = 0
        if passIndex is None: passIndex = 0
        if invertAsMask is None: invertAsMask = False
        if maskLayers is None: maskLayers = []

        self.frames = frames
        self.layerName = layerName
        self.blendMode = blendMode
        self.opacity = opacity
        self.useLights = useLights
        self.tintColor = tintColor
        self.tintFactor = tintFactor
        self.lineChange = lineChange
        self.passIndex = passIndex
        self.invertAsMask = invertAsMask
        self.maskLayers = maskLayers

    def __repr__(self):
        return textwrap.dedent(
        f"""AN Layer Object:
        Layer Name: {self.layerName}
        Frames: {len(self.frames)}
        Blend Mode: {self.blendMode}
        Opacity: {self.opacity}
        Use Lights: {self.useLights}
        Tint Color: {self.tintColor}
        Tint Factor: {self.tintFactor}
        Stroke Thickness: {self.lineChange}
        Pass Index: {self.passIndex}
        Mask Layers: {[maskLayer.layerName for maskLayer in self.maskLayers]}""")

    def copy(self):
        return GPLayer(self.layerName, [frame.copy() for frame in self.frames],
                       self.blendMode, self.opacity, self.useLights, self.tintColor,
                       self.tintFactor, self.lineChange, self.passIndex, self.invertAsMask,
                       self.maskLayers)

    def isEmptyLayer(self):
        for frame in self.frames:
            if len(frame.strokes) > 0:
                return False
        return True
