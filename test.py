import numpy as np
import IPython.display as ipd
import matplotlib.pyplot as plt

# Install soundifile in your environment to be able to write to a file
import soundfile as sf

def create_sinusoid(amp, freq, duration, sample_rate):
    t = np.arange(0, duration, 1.0 / sample_rate)
    return amp * np.sin(2 * np.pi * freq * t)

# complete the function k_harmonics
def k_harmonics(k, amp, freq, duration, sample_rate):

    total_duration = duration * k
    total_duration_time = np.arange(0, total_duration, 1.0 / sample_rate)
    segment_duration_time = np.arange(0, duration, 1.0 / sample_rate)
    silent_segment = create_sinusoid(0, freq, duration, sample_rate)

    # add the fundamental for og duration
    """
    result = np.array([])
    for i in range(k):
        result = np.append(result, silent_segment)
    """
    result = []

    # add a harmonic each new_duration n with frequency n*freq and amplitude amp/(1+n)
    for n in range(k):

        new_harm = np.array([])
        new_harm_seg = create_sinusoid(amp/(n+1), (n+1)*freq, duration, sample_rate)

        for i in range(n):
            new_harm = np.append(silent_segment, new_harm)

        for i in range(k-n):
            new_harm = np.append(new_harm, new_harm_seg)

        # add created sinusoid to result, index by index
        #result = np.add(result, new_harm)
        result.append(new_harm)

    return result

def funkyfunc(k):

    silent_seg = [0]

    # create initial array (no harmonic sound)
    result = np.array([0 for i in range(k)])

    for n in range(k):

        new_harm = []
        new_harm_seg = [1]

        for i in range(n):
            new_harm = np.append(new_harm, silent_seg)

        for i in range(k-n):
            new_harm = np.append(new_harm, new_harm_seg)

        result = np.add(result, new_harm)

    return result

# 1 to 5 inclusive
for i in range(1,6):
    print(funkyfunc(i))
    print()

# use the code in a notebook cell to plot/listen to the resulting
# signal of the k_harmonics function
f0 = 220
sr = 1000
amp = 0.5
duration = 1
k = 5

graphs = k_harmonics(k, amp, f0, duration, sr)

for p in graphs:
    plt.plot(p)
plt.show()
