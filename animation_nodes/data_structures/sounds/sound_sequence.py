import os
import bpy
import aud
from functools import lru_cache
from . sound_data import SoundData

# We define a constant sampleRate to avoid expensive resampling during execution.
sampleRate = 44100

class SoundSequence:
    def __init__(self, data, start, end, volume, fps):
        self.data = data
        self.start = start
        self.end = end
        self.volume = volume
        self.fps = fps

    @classmethod
    def fromSequence(cls, sequence):
        if sequence.type != "SOUND": raise ValueError("Not a sound sequence!")
        if sequence.sound.packed_file is None:
            path = bpy.path.abspath(sequence.sound.filepath)
            if not os.path.exists(path): return None
            soundData = getCachedSoundDataFromPath(path)
        else:
            soundData = getCachedSoundDataFromSound(sequence.sound)

        sequenceScene = findSceneWithSequence(sequence)
        fps = sequenceScene.render.fps
        return cls(soundData, sequence.frame_final_start / fps, sequence.frame_final_end / fps,
            sequence.volume, fps)

@lru_cache(maxsize=16)
def getCachedSoundDataFromPath(path):
    return getSoundData(aud.Sound.file(path))

@lru_cache(maxsize=16)
def getCachedSoundDataFromSound(sound):
    return getSoundData(sound.factory)

def getSoundData(sound):
    if sound.specs[0] == sampleRate:
        return SoundData(sound.rechannel(1).data().ravel(), sampleRate)
    else:
        return SoundData(sound.rechannel(1).resample(sampleRate).data().ravel(), sampleRate)

def findSceneWithSequence(sequence):
    for scene in bpy.data.scenes:
         if scene.sequence_editor is not None:
            for strip in scene.sequence_editor.sequences_all:
                if strip == sequence:
                    return scene
