import bpy
from . sound_data import SoundData

class SoundSequence:
    def __init__(self, data, startFrame, endFrame, volume, fps):
        self.data = data
        self.startFrame = startFrame
        self.endFrame = endFrame
        self.volume = volume
        self.fps = fps

    @classmethod
    def fromSequence(cls, sequence):
        for scene in bpy.data.scenes:
            if scene.sequence_editor is not None:
                for strip in scene.sequence_editor.sequences_all:
                    if strip == sequence:
                        sequenceScene = scene
                        break
        factory = sequence.sound.factory
        cls(SoundData(factory.rechannel(1).data().ravel(), factory.specs[0]),
            sequence.frame_final_start, sequence.frame_final_end,
            sequence.volume, sequenceScene.render.fps)
