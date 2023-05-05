import wave
import matplotlib.pyplot as plt
import numpy as np
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
specGen('/home/msguy01/Documents/School/School Programming/CS5/AudioCenter/static/audio/MatthewBevins/detect/broken [1682447227].wav', 5)