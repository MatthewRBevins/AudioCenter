import librosa
import soundfile as sf

y, sr = librosa.load('hello.wav')
y_shifted = librosa.effects.pitch_shift(y, sr, n_steps=-4)
sf.write('keychanged.wav', y_shifted, sr, 'PCM_24')