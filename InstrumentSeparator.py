# -*- coding: utf-8 -*-
"""
Created on Thu Feb  2 10:17:43 2023

@author: MichaelY24
"""

from spleeter.separator import Separator
from spleeter.audio.adapter import AudioAdapter
class Separate():
    def __init__(self, file):
        if __name__ == '__main__':    
            separator = Separator('spleeter:2stems')
            audio_loader = AudioAdapter.default()
            sample_rate = 44100
            waveform, _ = audio_loader.load(file, sample_rate=sample_rate)
            separator.separate_to_file(file, 'static/output')
