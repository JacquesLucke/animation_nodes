import numpy
from functools import lru_cache
from math import ceil, log, isclose

class Sound:
    def __init__(self, soundSequences):
        self.soundSequences = soundSequences

    def getSamplesInRange(self, start, end):
        if end <= start: raise ValueError("Invaild range!")
        maxSampleRate = max(sequence.data.sampleRate for sequence in self.soundSequences)
        start, end = int(start * maxSampleRate), int(end * maxSampleRate)
        samples = numpy.zeros(end - start + 1)

        for sequence in self.soundSequences:
            sequenceStart = int(sequence.start * maxSampleRate)
            sequenceEnd = int(sequence.end * maxSampleRate)
            if start > sequenceEnd or end < sequenceStart: continue

            i, j = max(start, sequenceStart), min(end, sequenceEnd)
            chunk = sequence.data.samples[i - sequenceStart:j - sequenceStart]
            samples[i - start:i - start + len(chunk)] += chunk
        return samples

    def computeSpectrum(self, start, end, beta = 6):
        samples = self.getSamplesInRange(start, end)
        chunk = numpy.zeros(2**ceil(log(len(samples), 2)))
        chunk[:len(samples)] = samples * getCachedKaiser(len(samples), beta)
        return numpy.abs(numpy.fft.rfft(chunk)) / len(samples) * 2

    def computeTimeSmoothedSpectrum(self, start, end, attack, release, smoothingSamples = 5, beta = 6):
        FFT = None
        duration = end - start
        for i in range(min(smoothingSamples, int(start // duration)), -1, -1):
            newFFT = self.computeSpectrum(start - i * duration, end - i * duration, beta = beta)
            if FFT is None: FFT = newFFT
            else:
                factor = numpy.array((attack, release))[(newFFT < FFT).astype(int)]
                FFT = FFT * factor + newFFT * (1 - factor)
        return FFT

@lru_cache(maxsize = 16)
def getCachedKaiser(length, beta):
    return numpy.kaiser(length, beta)
