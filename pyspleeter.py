# -*- coding: utf-8 -*-
"""
Created on Thu Feb  2 10:17:43 2023

@author: MichaelY24
"""

from spleeter.separator import Separator
from spleeter.audio.adapter import AudioAdapter
if __name__ == '__main__':    
    separator = Separator('spleeter:5stems')
    audio_loader = AudioAdapter.default()
    sample_rate = 44100
    waveform, _ = audio_loader.load('test.wav', sample_rate=sample_rate)
    separator.separate_to_file('test.wav', 'C:/Users/MichaelY24/Anaconda3/Lib/site-packages/spleeter/output')