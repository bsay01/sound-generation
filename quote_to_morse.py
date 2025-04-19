import matplotlib.pyplot as plt
import soundfile as sf
from sg_functions import *

# Define the Morse code dictionary for ASCII characters
MORSE_CODE_DICT = {
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.', 'G': '--.', 'H': '....',
    'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..', 'M': '--', 'N': '-.', 'O': '---', 'P': '.--.',
    'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
    'Y': '-.--', 'Z': '--..', '1': '.----', '2': '..---', '3': '...--', '4': '....-', '5': '.....',
    '6': '-....', '7': '--...', '8': '---..', '9': '----.', '0': '-----', ', ': '--..--', '.': '.-.-.-',
    '?': '..--..', '/': '-..-.', '-': '-....-', '(': '-.--.', ')': '-.--.-', ' ': '/'
}

def string_to_morse(input_string):
    input_string += " eom"
    morse = [MORSE_CODE_DICT[char.upper()] if char.upper() in MORSE_CODE_DICT else None for char in input_string]
    cleaned_morse = []
    for i, l in enumerate(morse):
        if (l is not None):
            cleaned_morse.append(l)
    return cleaned_morse

def string_to_morse_tones(input_string, dit_len_ms=100, frequency=600):

    dit_len_s = dit_len_ms/1000
    dah_len_s = 3*dit_len_s

    # generate a list of notes by making morse code of the string
    note_values = []
    for character in string_to_morse(input_string):

        # if we have a space, pause for 7 dits
        # there will already be 3 from the gap after the previous letter
        if character == '/':
            for i in range(4):
                note_values.append([0, dit_len_s])
            continue

        # handle morse code
        for bit in character:
            if bit == '.':
                note_values.append([frequency, dit_len_s])
            elif bit == '-':
                note_values.append([frequency, dah_len_s])
            else:
                raise Exception('morse code borked')
            # add inter-element gap
            note_values.append([0, dit_len_s])

        # add 3 dits time between letters
        # there will already be 1 dit of time from the inter-element gap
        for i in range(2):
            note_values.append([0, dit_len_s])

    return note_values

def main() -> None:

    ######################################## SET UP NOTE STREAM #########################################

    #- specify info about note stream
    amplitude = 0.7
    n_k = 8
    freq = 277.18*2 # A Maj - 220, 277.18, 330
    dit_len_ms = 100

    # parse text file - must be a bunch of integers separated by any whitespace
    input_string1 = "a life whose purpose is money is death" # Albert Camus
    input_string2 = "the opposite of poverty is not wealth; the opposite of poverty is enough" # Wess Stafford
    input_string3 = "our lives begin to end the day we become silent about things that matter" # Martin Luther King Jr.

    input_tones1 = string_to_morse_tones(input_string1, dit_len_ms=dit_len_ms, frequency=freq)
    input_tones2 = string_to_morse_tones(input_string2, dit_len_ms=dit_len_ms, frequency=freq)
    input_tones3 = string_to_morse_tones(input_string3, dit_len_ms=dit_len_ms, frequency=freq)

    # choose input string here to indicate the string you want and a suffix for the output files
    file_suffix = "stafford"
    ns_values = input_tones2

    ######################################## GEN SIGNAL #########################################

    #print(ns_values)
    out = generate_signals(ns_values, amp=amplitude, k=n_k, A=0.01, D=0.0, S=1.0, R=0.01, sr=SAMPLE_RATE)
    hrm = out[0]
    sin = out[1]
    tri = out[2]
    #print(out[3])

    ######################################## MAKE WAV FILES #########################################

    output_dir = "data_quote/"

    with open(output_dir + "data_" + file_suffix + ".txt", "w") as tf:
        for n in ns_values:
            tf.write("{:0.2f} Hz, {:0.3f} seconds\n".format(n[0], n[1]))

    create_midi_from_notes([(freq2midi(n[0]), n[1]) for n in ns_values], output_dir + "midi_data_" + file_suffix + ".mid")

    try:
        sf.write(output_dir + "hrm_" + file_suffix + ".wav", hrm, SAMPLE_RATE)
    except:
        sf.write("hrm_" + file_suffix + ".wav", hrm, SAMPLE_RATE)

    try:
        sf.write(output_dir + "sin_" + file_suffix + ".wav", sin, SAMPLE_RATE)
    except:
        sf.write("sin_" + file_suffix + ".wav", sin, SAMPLE_RATE)

    try:
        sf.write(output_dir + "tri_" + file_suffix + ".wav", tri, SAMPLE_RATE)
    except:
        sf.write("tri_" + file_suffix + ".wav", tri, SAMPLE_RATE)

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
