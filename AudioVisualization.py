import librosa
import numpy as np
import matplotlib.pyplot as plt
y, sr = librosa.load("static/audio/nevergonnabase.wav")
x = np.arange(0,len(y),1)
print(x)
plt.plot(x, y)
plt.show()
