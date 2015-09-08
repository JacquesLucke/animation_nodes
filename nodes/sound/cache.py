
def getStrengthOfSequence(sequence, bakeDataIndex, frame):
    bakeData = sequence.sound.bakeData[bakeDataIndex]
    return bakeData.samples[frame - sequence.frame_start].strength
