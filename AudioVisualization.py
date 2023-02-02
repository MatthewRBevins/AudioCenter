import librosa
import numpy as np
y, sr = librosa.load("static/audio/nevergonnabase.wav")
D = librosa.stft(y)
s = np.abs(librosa.stft(y)**2) # Get magnitude of stft
chroma = librosa.feature.chroma_stft(S=s, sr=sr)
chroma = np.cumsum(chroma)
import matplotlib.pylab as plt
x = np.linspace(-chroma, chroma)
plt.plot(x, np.sin(x))
plt.xlabel('Angle [rad]')
plt.ylabel('sin(x)')
plt.axis('tight')
plt.show()