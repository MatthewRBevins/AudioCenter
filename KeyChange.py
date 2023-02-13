import librosa
import soundfile as sf

def keyChange(filename, numSteps, outputFile):
    print("***STARTING KEY CHANGE***")
    y, sr = librosa.load(filename)
    y_shifted = librosa.effects.pitch_shift(y, sr, n_steps=numSteps)
    sf.write('static/audio/'+outputFile, y_shifted, sr, 'PCM_24')
    print("***DONE***")

keyChange('static/audio/nevergonnabase.wav', 4, 'newNeverGonna.wav')