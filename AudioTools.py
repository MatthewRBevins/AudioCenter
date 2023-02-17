import wave, audioop
from pydub import AudioSegment
from spleeter.separator import Separator
from spleeter.audio.adapter import AudioAdapter
import librosa
import soundfile as sf

def keyChange(file, output, steps):
    y, sr = librosa.load(file)
    y_shifted = librosa.effects.pitch_shift(y, sr, n_steps=steps)
    sf.write(output+file.split("/")[len(file.split("/"))-1], y_shifted, sr, 'PCM_24')
    return [output+file]

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

def split(file, output, stems):
    separator = Separator('spleeter:'+str(stems)+'stems')
    audio_loader = AudioAdapter.default()
    sample_rate = 44100
    waveform, _ = audio_loader.load(file, sample_rate=sample_rate)
    separator.separate_to_file(file, output)
    actualname = file.split("/")[len(file.split("/"))-1].split(".wav")[0]
    print("*************  " + actualname)
    return [output + actualname + '/accompaniment.wav', output + actualname + '/vocals.wav']