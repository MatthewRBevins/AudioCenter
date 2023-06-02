import wave, audioop
from pydub import AudioSegment
from spleeter.separator import Separator
from spleeter.audio.adapter import AudioAdapter
import librosa
import soundfile as sf
import asyncio
from shazamio import Shazam, Serialize
import time
import shutil
import numpy as np
import matplotlib.pyplot as plt
import os
import subprocess
import contextlib
from scipy.io import wavfile

def saveFile(file, output):
    song, fs = librosa.load(file)
    wavfile.write(output+"/audio.wav", fs, song)

def mp3towav(file):
    output = os.path.splitext(file)[0] + ".wav"
    err = subprocess.call(['ffmpeg', '-i', file, output])
    return (output, err)

async def songDetectAsync(file):
    shazam = Shazam()
    start = time.time()
    out = await shazam.recognize_song(file)
    end = time.time()
    output = dict()
    if len(out['matches']) == 0:
        return None
    else:
        output["title"] = out.get("track").get("title")
        output["artist"] = out.get("track").get("subtitle")
        output["image"] = out.get("track").get("images").get("coverart")
        output["lyrics"] = out.get("track").get("sections")[1].get("text")
        return output

def trimSong(originalWavPath, newWavPath):
    #Assumes file is .wav 
    sampleRate, waveData = wavfile.read(originalWavPath)
    endSample = int(20 * sampleRate )
    trim = wavfile.write(newWavPath, sampleRate, waveData[0:endSample])
    return trim

def makeCut(filepath, startpoint, endpoint, width):
    sound = AudioSegment.from_file(filepath)
    print(startpoint)
    print(endpoint)
    print(width)
    print("****")
    startpoint = startpoint/width
    endpoint = endpoint/width
    soundlength = len(sound)
    print(startpoint)
    print(soundlength)
    print(startpoint*soundlength)
    finishedcut = sound[:int(startpoint*soundlength)] + sound[int(endpoint*soundlength):]
    finishedcut.export(filepath, format='wav')
    

def detectSong(file):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(songDetectAsync(file))

def keyChange(file, output, steps):
    pathFound = False
    y, sr = librosa.load(file)
    y_shifted = librosa.effects.pitch_shift(y, sr, n_steps=steps)
    if (file.split("/")[len(file.split("/"))-1].split(".w")[0] != "keychange") and (file.split("/")[len(file.split("/"))-1].split(".w")[0] != "amplify") and (file.split("/")[len(file.split("/"))-1].split(".w")[0] != "speedChange"): 
        path = output+file.split("/")[len(file.split("/"))-1].split(".w")[0]
    else:
        path = output+file.split("/")[len(file.split("/"))-2]+"1"
    if os.path.exists(path):
        pathFound = True 
    if pathFound: 
        shutil.rmtree(path)
    os.mkdir(path)
    sf.write(path+"/keychange.wav", y_shifted, sr, 'PCM_24')
    return [path+"/keychange.wav"]

def writeFrames(file, frames, output):
    samplerate = 48000
    audio = np.array([np.array(frames), np.array(frames)]).T
    audio = (audio * (2 ** 15 - 1)).astype("<h")
    try:
        os.mkdir(output+file.split("/")[len(file.split("/"))-1].split(".w")[0])
    except:
        pass
    with wave.open(output+file.split("/")[len(file.split("/"))-1].split(".w")[0]+"/cut.wav", "w") as f:
        f.setnchannels(2)
        f.setsampwidth(2)
        f.setframerate(samplerate)
        f.writeframes(audio.tobytes())
    return output+file.split("/")[len(file.split("/"))-1].split(".w")[0]+"/cut.wav"

def length(file):
    with contextlib.closing(wave.open(file,'r')) as f:
        frames = f.getnframes()
        rate = f.getframerate()
        duration = frames / float(rate)
        return duration 
    
def float2pcm(sig, dtype='int16'): 
    sig = np.asarray(sig) 
    dtype = np.dtype(dtype)
    i = np.iinfo(dtype)
    abs_max = 2 ** (i.bits - 1)
    offset = i.min + abs_max
    return (sig * abs_max + offset).clip(i.min, i.max).astype(dtype)

def amplify(file, output, factor): 
    pathFound = False
    factor = factor #Adjust volume by factor
    print("Hi " + file.split("/")[len(file.split("/"))-1].split(".w")[0])
    print(file)
    prospectPath = file.split("/")[len(file.split("/"))-1].split(".w")[0]
    if (prospectPath != "amplify") and (prospectPath != "keychange") and (prospectPath != "speedChange"): 
        path = output+prospectPath
    else:
        path = output+file.split("/")[len(file.split("/"))-2]+"1"
    with wave.open(file, 'rb') as wav:
        p = wav.getparams()
        if os.path.exists(path):
            pathFound = True 
        if pathFound: 
            shutil.rmtree(path)
        os.mkdir(path)
        with wave.open(path+'/amplify.wav', 'wb') as audio:
            audio.setparams(p)
            frames = wav.readframes(p.nframes)
            audio.writeframesraw(audioop.mul(frames, p.sampwidth, factor))
    return [path+'/amplify.wav']

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


def changeSpeed(file, output, factor):
    pathFound = False
    prospectPath = file.split("/")[len(file.split("/"))-1].split(".w")[0]
    if (prospectPath != "amplify") and (prospectPath != "keychange") and (prospectPath != "speedChange"): 
        path = output+prospectPath
    else:
        path = output+file.split("/")[len(file.split("/"))-2]+"1"
    if os.path.exists(path):
        pathFound = True 
    if pathFound: 
        shutil.rmtree(path)
    os.mkdir(path)
    song, fs = librosa.load(file)

    changed = librosa.effects.time_stretch(song, factor)
    print(changed)
    print(changed.astype(np.float16))
    wavfile.write(path+"/speedChange.wav", fs, float2pcm(changed)) # save the song 
    return [path+'/speedChange.wav']

def specGen(ratio, audio):
    wav_obj = wave.open(audio, 'rb')
    sample_freq = wav_obj.getframerate()
    n_samples = wav_obj.getnframes()
    time = n_samples/sample_freq
    signal_wave = wav_obj.readframes(n_samples)
    signal_array = np.frombuffer(signal_wave, dtype=np.int16)
    plt.figure(figsize=(5*ratio, 5))
    plt.specgram(signal_array, Fs=sample_freq, vmin=-20, vmax=50)
    plt.title('Spectrogram for ' + audio)
    plt.ylabel('Frequency (Hz)')
    plt.xlabel('Time (s)')
    plt.xlim(0, time)
    plt.colorbar()
    plt.show()