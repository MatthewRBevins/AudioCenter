import numpy as np
import matplotlib.pyplot as plt
import wave, audioop
import mpld3

def displayWaveform(file):
    wav_obj = wave.open(file, 'rb')
    sample_freq = wav_obj.getframerate()
    n_samples = wav_obj.getnframes()
    t_audio = n_samples/sample_freq
    n_channels = wav_obj.getnchannels()
    signal_wave = wav_obj.readframes(n_samples)
    signal_array = np.frombuffer(signal_wave, dtype=np.int16)
    times = np.linspace(0, n_samples/sample_freq, num=len(signal_array))
    fig = plt.figure(figsize=(15, 5))
    plt.plot(times, signal_array)
    plt.title('Waveform Plot')
    plt.ylabel('Signal Value')
    plt.xlabel('Time (s)')
    plt.xlim(0, t_audio)

    html_str = mpld3.fig_to_html(fig)
    Html_file= open("index.html","w")
    Html_file.write(html_str)
    Html_file.close()
    return True


file = input("file: ")
displayWaveform(file)