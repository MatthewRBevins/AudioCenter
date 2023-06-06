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

server = True #Change to true when it's time to upload to the server
serverPath = ""
if server:
    serverPath = "./public/AudioCenter/AudioCenterLocal/"

def saveFile(file, output):
    #Saves file at output
    song, fs = librosa.load(file)
    wavfile.write(output+"/audio.wav", fs, song)

def mp3towav(file):
    #Converts wav to mp3
    output = os.path.splitext(file)[0] + ".wav"
    err = subprocess.call(['ffmpeg', '-i', file, output])
    return (output, err)

async def songDetectAsync(file):
    shazam = Shazam()
    start = time.time()
    #Powered by Shazam recognition
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

def makeCut(filepath, cutData, effect, steps=0):
    print(cutData)
    #start, end, length
    sound = AudioSegment.from_file(filepath)
    startpoint = 1000*cutData[0]
    endpoint = 1000*cutData[1]
    print(startpoint)
    #print(filepath)
    print(endpoint)
    print(len(sound))
    selectedsound = sound[int(startpoint):int(endpoint)]
    if effect == 'key':
        selectedKeyChange = keyChange(selectedsound, None, steps)
        finishedcut = sound[:int(startpoint)] + selectedKeyChange + sound[int(endpoint):]
    elif effect == 'speed':
        selectedSpeedChange = changeSpeed(selectedsound, None, steps)
        finishedcut = sound[:int(startpoint)] + selectedSpeedChange + sound[int(endpoint):]
    else:
        finishedcut = sound[:int(startpoint)] + sound[int(endpoint):]
    finishedcut.export(filepath, format='wav')
    return filepath
    

def detectSong(file):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(songDetectAsync(file))

def keyChange(file, output, steps):
    if isinstance(file, AudioSegment):
        y = np.frombuffer(file._data, dtype=np.int16).astype(np.float32)/2**15
        y = librosa.effects.pitch_shift(y, file.frame_rate, n_steps=steps)
        a  = AudioSegment(np.array(y * (1<<15), dtype=np.int16).tobytes(), frame_rate = file.frame_rate, sample_width=2, channels = 1)
        return a
    else:
        pathFound = False
        y, sr = librosa.load(file)
        y_shifted = librosa.effects.pitch_shift(y, sr, n_steps=steps)
        #First of many codeblocks like this
        #This is to avoid filename endings such as "/keychange/keychange.wav," which can cause folder confusion
        if (file.split("/")[len(file.split("/"))-1].split(".w")[0] != "keychange") and (file.split("/")[len(file.split("/"))-1].split(".w")[0] != "amplify") and (file.split("/")[len(file.split("/"))-1].split(".w")[0] != "speedChange"): 
            path = output+file.split("/")[len(file.split("/"))-1].split(".w")[0]
        else:
            path = output+file.split("/")[len(file.split("/"))-2]+"1"
        if os.path.exists(path):
            pathFound = True 
        #pathFound looks redundant, but this is actually necessary to remove a file permission error
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

#Function from https://stackoverflow.com/questions/60352850/wave-error-unknown-format-3-arises-when-trying-to-convert-a-wav-file-into-text
def float2pcm(sig, dtype='int16'): 
    #This function converts a 32-bit float audio file into a 16-bit integer audio file
    #Necessary for the tools in amplify to work with librosa (keychange and speedchange)
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
    #Thank you to the wave module tutorials for letting us know how to work with .wav files!
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

def combine(audio, output):
    file = audio[0]
    audiosegments = []
    for i in audio:
        audiosegments.append(AudioSegment.from_wav(i))
    i = 1
    prev = audiosegments[0]
    while i < len(audiosegments):
        prev = prev.overlay(audiosegments[i]) 
        i+=1
    try:
        os.mkdir(output+file.split("/")[len(file.split("/"))-1].split(".w")[0])
    except:
        pass
    prev.export(output + file.split("/")[len(file.split("/"))-1].split(".w")[0] + '/combine.wav', format='wav')
    return output + file.split("/")[len(file.split("/"))-1].split(".w")[0] + '/combine.wav'

def split(file, output, stems):
    #Spleeter
    separator = Separator('spleeter:'+str(stems)+'stems')
    audio_loader = AudioAdapter.default()
    sample_rate = 44100
    waveform, _ = audio_loader.load(file, sample_rate=sample_rate)
    separator.separate_to_file(file, output)
    actualname = file.split("/")[len(file.split("/"))-1].split(".wav")[0]
    print("*************  " + actualname)
    return [output + actualname + '/accompaniment.wav', output + actualname + '/vocals.wav']


def changeSpeed(file, output, factor):
    if isinstance(file, AudioSegment):
        y = np.frombuffer(file._data, dtype=np.int16).astype(np.float32)/2**15
        y = librosa.effects.time_stretch(y, factor)
        a  = AudioSegment(np.array(y * (1<<15), dtype=np.int16).tobytes(), frame_rate = file.frame_rate, sample_width=2, channels = 1)
        return a
    else:
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
        #time_stretch corresponds to speed changing
        changed = librosa.effects.time_stretch(song, factor)
        print(changed)
        print(changed.astype(np.float16))
        wavfile.write(path+"/speedchange.wav", fs, float2pcm(changed)) # save the song 
        return path+'/speedchange.wav'

def specGen(ratio, audio):
    #Spectrogram generator
    #A lot of the code in this function is from https://learnpython.com/blog/plot-waveform-in-python/
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
    
#convert audiosegment to librosa 
# from https://groups.google.com/g/librosa/c/XWae4PdbXuk?pli=1   
def audiosegment_to_ndarray(audiosegment):
    samples = audiosegment.get_array_of_samples()
    samples_float = librosa.util.buf_to_float(samples,n_bytes=2,
                                      dtype=np.float32)
    sample_all = samples_float
        
        
    return [sample_all,audiosegment.frame_rate]