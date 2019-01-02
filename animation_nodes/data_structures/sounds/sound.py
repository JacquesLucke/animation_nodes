import numpy
from math import ceil, log
from functools import lru_cache

class Sound:
    def __init__(self, soundSequences):
        self.soundSequences = soundSequences

    def getSamplesInRange(self, start, end):
        if end <= start: raise ValueError("Invaild range!")
        maxSampleRate = max(sequence.soundData.sampleRate for sequence in self.soundSequences)
        samplesSize = int(maxSampleRate * (end - start))
        samples = numpy.zeros(samplesSize)

        for sequence in self.soundSequences:
            sequenceStart = sequence.start / sequence.fps
            sequenceEnd = sequence.end / sequence.fps
            if sequenceStart > end or sequenceEnd < start: continue

            samplesData, sampleRate = sequence.soundData.samples, sequence.soundData.sampleRate
            i = int(max(start - sequenceStart, 0) * sampleRate)
            j = int((end - sequenceStart) * sampleRate)
            chunk = samplesData[i:j] * sequence.volume

            relativeStart  = max((sequenceStart - start) / (end - start), 0)
            i = int(relativeStart * samplesSize)
            j = i + len(chunk)
            if sampleRate == maxSampleRate:
                samples[i:j] += chunk
            else:
                pass # Variable sample rate, needs interpolation.
        return samples

    def computeSpectrum(self, start, end, beta = 6):
        samples = self.getSamplesInRange(start, end)
        chunk = numpy.zeros(2**ceil(log(len(samples), 2)))
        chunk[:len(samples)] = samples * self.getCachedKaiser(len(samples), beta)
        return numpy.abs(numpy.fft.rfft(chunk)) / len(samples) * 2

    def computeTimeSmoothedSpectrum(self, start, end, attack, release, smoothingSamples = 5, beta = 6):
        FFT = None
        duration = end - start
        for i in range(min(smoothingSamples, int(start / duration)), -1, -1):
            newFFT = self.computeSpectrum(start - i * duration, end - i * duration, beta = beta)
            if FFT is None: FFT = newFFT
            else:
                factor = numpy.array((attack, release))[(newFFT < FFT).astype(int)]
                FFT = FFT * factor + newFFT * (1 - factor)
        return FFT

    @lru_cache(maxsize = 16)
    def getCachedKaiser(self, length, beta):
        return numpy.kaiser(length, beta)
