import textwrap

class GPFrame:
    def __init__(self, strokes = None, frameNumber = None):

        if strokes is None: strokes = []
        if frameNumber is None: frameNumber = 0

        self.strokes = strokes
        self.frameNumber = frameNumber

    def __repr__(self):
        return textwrap.dedent(
        f"""AN Frame Object:
        Strokes: {len(self.strokes)}
        Frame Number: {self.frameNumber}""")

    def copy(self):
        return GPFrame([stroke.copy() for stroke in self.strokes], self.frameNumber)
