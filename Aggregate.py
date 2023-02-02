import wave, audioop
from pydub import AudioSegment

def amplify(file, factor): 
    factor = factor #Adjust volume by factor
    with wave.open(file, 'rb') as wav:
        p = wav.getparams()
        with wave.open('output.wav', 'wb') as audio:
            audio.setparams(p)
            frames = wav.readframes(p.nframes)
            audio.writeframesraw(audioop.mul(frames, p.sampwidth, factor))

def combine(sound1, sound2): 
    audiosound1 = AudioSegment.from_wav(sound1)
    audiosound2 = AudioSegment.from_wav(sound2)
    mixed = audiosound1.overlay(audiosound2) 
    mixed.export("mixed.wav", format='wav')
    
amplify("vocals.wav", 2)
combine("output.wav", "accompaniment.wav")