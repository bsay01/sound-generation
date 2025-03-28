import numpy as np
import matplotlib.pyplot as plt
import soundfile as sf
from sg_functions import *

#music21.configure.run() # run this in a new environment!

#####################################################################################################
############################################## DEFINES ##############################################
#####################################################################################################

SAMPLE_RATE = 44100
N_SINES = 100

TEMPO = 120
#tinyNotation_STRING = "4/4 e4. r8 d8 c# d8 r8 r4 chord{C2. e g} e1"

ADSR_DEMO_TITLE = "ADSR Functionality Graphs"

#####################################################################################################
############################################### MAIN ################################################
#####################################################################################################

if __name__ == '__main__':

    ex_freq = [220]
    ex_sr = 44100
    ex_amp = 1
    ex_duration = 2
    ex_k = 8

    ADSR = generate_ADSR_envelope(ex_duration, 0.04, 0.06, 0.6, 0.05)
    ADSR_len = len(ADSR)
    ADSR_duration = ADSR_len / SAMPLE_RATE

    hrm_signal = 0*ADSR
    sin_signal = 0*ADSR
    tri_signal = 0*ADSR
    for f_i in ex_freq:
        hrm_signal = np.add(hrm_signal, k_harmonics(k=ex_k, amp=ex_amp, freq=f_i, duration=ADSR_duration, sr=ex_sr))
        sin_signal = np.add(sin_signal, generate_sine(note_num=freq2midi(f_i), duration=ADSR_duration, sr=ex_sr))
        tri_signal = np.add(tri_signal, generate_triangle(note_num=freq2midi(f_i), duration=ADSR_duration, num_sinusoids=1000, sr=ex_sr))

    r_ADSR = np.array([i/100 for i in ADSR])
    hrm_signal_ADSR = np.multiply(hrm_signal, r_ADSR)[0:ADSR_len]
    sin_signal_ADSR = np.multiply(sin_signal, r_ADSR)[0:ADSR_len]
    tri_signal_ADSR = np.multiply(tri_signal, r_ADSR)[0:ADSR_len]

    PLOT_TITLE = "Signal Plots"

    fig, axs = plt.subplots(3, 1, layout='constrained')

    fig.align_labels()
    fig.set_size_inches(16, 8)
    fig.set_dpi(100)
    fig.suptitle(PLOT_TITLE, fontsize=20)

    samples_in_short_time = int((1 / min(ex_freq)) * ex_sr * 4)

    ex_hrm_signal = hrm_signal[0:samples_in_short_time]
    axs[0].plot([i/44100 for i in range(len(ex_hrm_signal))], ex_hrm_signal)
    ax = axs[0]
    ax.set_title("Harm")
    ax.set_ylabel("Amplitude")

    ex_sin_signal = sin_signal[0:samples_in_short_time]
    axs[1].plot([i/44100 for i in range(len(ex_sin_signal))], ex_sin_signal)
    ax = axs[1]
    ax.set_title("Sine")
    ax.set_ylabel("Amplitude")

    ex_tri_signal = tri_signal[0:samples_in_short_time]
    axs[2].plot([i/44100 for i in range(len(ex_tri_signal))], ex_tri_signal)
    ax = axs[2]
    ax.set_title("Tri")
    ax.set_ylabel("Amplitude")

    ax.set_xlabel("Time (seconds)")

    plt.show()

    try:
        sf.write("output/" + "hrm.wav", hrm_signal_ADSR, ex_sr)
    except:
        sf.write("hrm.wav", hrm_signal_ADSR, ex_sr)

    try:
        sf.write("output/" + "sin.wav", sin_signal_ADSR, ex_sr)
    except:
        sf.write("sin.wav", sin_signal_ADSR, ex_sr)

    try:
        sf.write("output/" + "tri.wav", tri_signal_ADSR, ex_sr)
    except:
        sf.write("tri.wav", tri_signal_ADSR, ex_sr)

    try:
        fig.savefig("output/" + PLOT_TITLE + ".png")
    except:
        fig.savefig(PLOT_TITLE + ".png")
