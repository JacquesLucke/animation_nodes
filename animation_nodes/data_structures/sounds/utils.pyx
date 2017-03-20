cdef findStartAndEndFrame(list sequences):
    startFrame = min(sequence.frame_final_start for sequence in sequences)
    endFrame = max(sequence.frame_final_end for sequence in sequences)
    return startFrame, endFrame
