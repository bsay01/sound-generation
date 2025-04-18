import matplotlib.pyplot as plt
import soundfile as sf
import random
from sg_functions import *

def main() -> None:

    ######################################## GEN RAND NOTES #########################################

    #- specify info about note stream
    n_amp = 0.7
    n_k = 8
    #ns_dur = [100, 100] # note duration range - see line 58
    ns_dur = 75

    # A MAJ
    # A4 (440 Hz), B4 (493.88 Hz), C5 (523.25 Hz), D5 (587.33 Hz), E5 (659.25 Hz), F#5 (739.99 Hz), G5 (783.99 Hz)
    ns_options = [440, 493.88, 523.25, 587.33, 659.25, 739.99, 783.99]

    ns_options = [n / 4 for n in ns_options]

    # parse text file - must be a bunch of integers separated by any whitespace
    input_data = read_integers_from_file("data_txt/input.txt")

    # normalize values
    minimum = min(input_data)

    for i, _ in enumerate(input_data):
        input_data[i] += minimum

    normalized_input_data = lov_to_new_range(input_data, min(input_data), max(input_data), new_min=0, new_max=6)

    # generate a list of pairs of notes and durations
    ns_values = []
    for i in normalized_input_data:
        frequency = ns_options[i]
        #duration = random.randrange(ns_dur[0],ns_dur[1])/1000
        duration = ns_dur/1000
        ns_values.append([frequency, duration])

    ######################################## GEN SIGNAL #########################################

    #print(ns_values)
    out = generate_signals(ns_values, amp=n_amp, sr=SAMPLE_RATE, k=n_k)
    hrm = out[0]
    sin = out[1]
    tri = out[2]
    #print(out[3])

    ######################################## MAKE WAV FILES #########################################

    output_dir = "data_txt/"

    with open(output_dir + "data.txt", "w") as tf:
        for n in ns_values:
            tf.write("{:0.2f} Hz, {:0.3f} seconds\n".format(n[0], n[1]))

    create_midi_from_notes([(freq2midi(n[0]), n[1]) for n in ns_values], output_dir + "midi_data.mid")

    try:
        sf.write(output_dir + "hrm_txt.wav", hrm, SAMPLE_RATE)
    except:
        sf.write("hrm_txt.wav", hrm, SAMPLE_RATE)

    try:
        sf.write(output_dir + "sin_txt.wav", sin, SAMPLE_RATE)
    except:
        sf.write("sin_txt.wav", sin, SAMPLE_RATE)

    try:
        sf.write(output_dir + "tri_txt.wav", tri, SAMPLE_RATE)
    except:
        sf.write("tri_txt.wav", tri, SAMPLE_RATE)

    ######################################### GRAPH OUTPUT ##########################################

    PLOT_TITLE = "Signal Plots"

    fig, axs = plt.subplots(3, 1, layout='constrained')

    fig.align_labels()
    fig.set_size_inches(8, 4)
    fig.set_dpi(100)
    fig.suptitle(PLOT_TITLE, fontsize=20)

    axs[0].plot([i/44100 for i in range(len(hrm))], hrm)
    ax = axs[0]
    ax.set_title("Harm")
    ax.set_ylabel("Amplitude")

    axs[1].plot([i/44100 for i in range(len(sin))], sin)
    ax = axs[1]
    ax.set_title("Sine")
    ax.set_ylabel("Amplitude")

    axs[2].plot([i/44100 for i in range(len(tri))], tri)
    ax = axs[2]
    ax.set_title("Tri")
    ax.set_ylabel("Amplitude")

    ax.set_xlabel("Time (seconds)")

    try:
        fig.savefig(output_dir + PLOT_TITLE + ".png")
    except:
        fig.savefig(PLOT_TITLE + ".png")

    #plt.show()

if __name__ == "__main__":
    main()
