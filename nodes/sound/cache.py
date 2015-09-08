from ... utils.sequence_editor import getSoundSequences

def getStrengthOfSequence(sequence, bakeDataIndex, frame):
    bakeDataItems = sequence.sound.bakeData
    if sequence.frame_final_start <= frame <= sequence.frame_final_end and len(bakeDataItems) > bakeDataIndex:
        bakeData = bakeDataItems[bakeDataIndex]
        return bakeData.samples[frame - sequence.frame_start].strength
    return 0

def getStrengthOfChannel(channel, bakeDataIndex, frame):
    strength = 0
    for sequence in getSoundSequences():
        if sequence.channel == channel:
            strength += getStrengthOfSequence(sequence, bakeDataIndex, frame)
    return strength

def getStrengthOfAllSequences(bakeDataIndex, frame):
    strength = 0
    for sequence in getSoundSequences():
        strength += getStrengthOfSequence(sequence, bakeDataIndex, frame)
    return strength
