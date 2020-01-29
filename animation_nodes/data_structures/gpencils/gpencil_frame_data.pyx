# cython: profile=True
import textwrap

class GPFrame:
    def __init__(self, strokes = None, frameIndex = None, frameNumber = None):

        if strokes is None: strokes = []
        if frameIndex is None: frameIndex = 0
        if frameNumber is None: frameNumber = 0

        self.strokes = strokes
        self.frameIndex = frameIndex
        self.frameNumber = frameNumber

    def __repr__(self):
        return textwrap.dedent(
        f"""AN Frame Object:
        Strokes: {len(self.strokes)}
        Frame Index: {self.frameIndex}
        Frame Number: {self.frameNumber}""")

    def copy(self):
        return GPFrame(self.strokes, self.frameIndex, self.frameNumber)
