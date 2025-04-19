import matplotlib.pyplot as plt
import soundfile as sf
from sg_functions import *

if __name__ == '__main__':

    ex_freq = [110]
    ex_sr = 44100
    ex_amp = 0.2
    ex_duration = 10
    ex_k = 8

    out = generate_signals([[i, float(ex_duration)] for i in ex_freq], amp=ex_amp, k=ex_k, A=0.1, D=0.0, S=1.0, R=0.1, sr=SAMPLE_RATE)
    hrm = out[0]
    sin = out[1]
    tri = out[2]

    PLOT_TITLE = "Signal Plots"

    fig, axs = plt.subplots(3, 1, layout='constrained')

    fig.align_labels()
    fig.set_size_inches(16, 8)
    fig.set_dpi(100)
    fig.suptitle(PLOT_TITLE, fontsize=20)

    samples_in_short_time = int((1 / min(ex_freq)) * ex_sr * 4)

    ex_hrm_signal = hrm[0:samples_in_short_time]
    axs[0].plot([i/44100 for i in range(len(ex_hrm_signal))], ex_hrm_signal)
    ax = axs[0]
    ax.set_title("Harm")
    ax.set_ylabel("Amplitude")

    ex_sin_signal = sin[0:samples_in_short_time]
    axs[1].plot([i/44100 for i in range(len(ex_sin_signal))], ex_sin_signal)
    ax = axs[1]
    ax.set_title("Sine")
    ax.set_ylabel("Amplitude")

    ex_tri_signal = sin[0:samples_in_short_time]
    axs[2].plot([i/44100 for i in range(len(ex_tri_signal))], ex_tri_signal)
    ax = axs[2]
    ax.set_title("Tri")
    ax.set_ylabel("Amplitude")

    ax.set_xlabel("Time (seconds)")

    #plt.show()

    output_dir = "data_sg/"

    try:
        sf.write(output_dir + "hrm.wav", hrm, ex_sr)
    except:
        sf.write("hrm.wav", hrm, ex_sr)

    try:
        sf.write(output_dir + "sin.wav", sin, ex_sr)
    except:
        sf.write("sin.wav", sin, ex_sr)

    try:
        sf.write(output_dir + "tri.wav", tri, ex_sr)
    except:
        sf.write("tri.wav", tri, ex_sr)

    try:
        fig.savefig(output_dir + PLOT_TITLE + ".png")
    except:
        fig.savefig(PLOT_TITLE + ".png")
