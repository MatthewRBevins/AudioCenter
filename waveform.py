# -*- coding: utf-8 -*-
"""
Created on Fri Jan  6 08:58:34 2023

@author: MichaelY24
"""

#Thanks to https://learnpython.com/blog/plot-waveform-in-python/
import wave
wav_obj = wave.open('BabyElephantWalk60.wav', 'rb')
sample_freq = wav_obj.getframerate()
n_samples = wav_obj.getnframes()
t_audio = n_samples/sample_freq
n_channels = wav_obj.getnchannels()
signal_wave = wav_obj.readframes(n_samples)
import numpy as np
signal_array = np.frombuffer(signal_wave, dtype=np.int16)
times = np.linspace(0, n_samples/sample_freq, num=n_samples)
import matplotlib.pyplot as plt
plt.figure(figsize=(15, 5))
plt.plot(times, signal_array)
plt.title('Waveform Plot')
plt.ylabel('Signal Value')
plt.xlabel('Time (s)')
plt.xlim(0, t_audio)
plt.show()