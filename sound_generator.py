import numpy as np
import IPython.display as ipd
import matplotlib.pyplot as plt
import soundfile as sf
import music21
import math
import tkinter as tk
from tkinter import messagebox
import os

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
############################################# FUNCTIONS #############################################
#####################################################################################################

def freq2midi(freq: float):
    return int(12 * math.log2(freq/440) + 69) if freq > 0 else -1

def midi2freq(note_num: int):
    return 440 * pow(2, (note_num - 69) / 12) if note_num >= 0 and note_num < 128 else 0

def generate_triangle(note_num: int, duration: float, num_sinusoids: int):
    freq = midi2freq(note_num)
    t = np.arange(0, duration, 1.0/SAMPLE_RATE)
    output = 0*t
    for i in range(num_sinusoids):
        n = 2*i+1
        new_harm = (pow(-1,i)/pow(n,2)) * np.sin(2*np.pi*freq*n*t)
        output = np.add(output, new_harm)
    return np.multiply(output, 8/pow(np.pi,2))

def generate_sine(note_num: int, duration: float):
    return np.sin(2*np.pi*midi2freq(note_num)*np.arange(0, duration, 1.0/SAMPLE_RATE))

def k_harmonics(k, amp, freq, duration, sample_rate):
    silent_seg = 0 * np.arange(0, duration, 1.0 / sample_rate)
    output = np.array(silent_seg)
    for n in range(k):
        new_harm = amp/(n+1) * np.sin(2 * np.pi * (n+1)*freq * np.arange(0, duration, 1.0 / sample_rate))
        output = np.add(output, new_harm)
    return output

def generate_ADSR_envelope(duration, A=0.04, D=0.06, S=0.6, R=0.05):
    attack  = np.array([             i/A for i in np.arange(0,        A, 1.0/SAMPLE_RATE)])
    decay   = np.array([ (1-((1-S)/D)*i) for i in np.arange(0,        D, 1.0/SAMPLE_RATE)])
    sustain = np.array([               S for i in np.arange(0, duration, 1.0/SAMPLE_RATE)])
    ADS = np.append(np.append(attack, decay), sustain)[0:int(duration*SAMPLE_RATE)]
    last = ADS[-1]
    release = np.array([(-last/R*i+last) for i in np.arange(0,        R, 1.0/SAMPLE_RATE)])
    return np.array([i*100 for i in np.append(ADS, release)])

def print_note_stream_info(note_strm, met_mark):
    for n in note_strm:
        name = n.name
        try:
            octave = n.octave
            frequency = n.pitch.frequency
        except:
            octave = ""
            frequency = 0
        duration_sec = met_mark.durationToSeconds(n.duration)
        print("{}{} ({:.4f} Hz), duration: {} sec".format(name, octave, frequency, duration_sec))
    print()

def validate_tempo():
    try:
        tempo_to_validate = int(tempo_entry.get())
        if tempo_to_validate < 30:
            tempo_entry.delete(0, tk.END)
            tempo_entry.insert(0, "30")
        elif tempo_to_validate > 400:
            tempo_entry.delete(0, tk.END)
            tempo_entry.insert(0, "400")
    except ValueError:
        tempo_entry.delete(0, tk.END)
        tempo_entry.insert(0, TEMPO)

def update_tempo(increment):
    try:
        tempo_entered = int(tempo_entry.get())
    except ValueError:
        messagebox.showwarning("Input Error", "Please enter a valid number!")
        tempo_entry.delete(0, tk.END)
        tempo_entry.insert(0, TEMPO)
        return
    tempo_entry.delete(0, tk.END)
    tempo_entry.insert(0, str(tempo_entered + increment))
    validate_tempo()

def submit_score():

    global TEMPO

    try:
        tempo_entered = int(tempo_entry.get())
        TEMPO = tempo_entered
        analyze_submission()

    except ValueError:
        messagebox.showwarning("Input Error", "Please enter a valid number!")
        tempo_entry.delete(0, tk.END)
        tempo_entry.insert(0, TEMPO)

def reset_window():

    global TEMPO
    TEMPO = 120
    tempo_entry.delete(0, tk.END)
    tempo_entry.insert(0, TEMPO)

class ChordState(music21.tinyNotation.State):
    def affectTokenAfterParse(self, n):
       super(ChordState, self).affectTokenAfterParse(n)
       return None # do not append Note object

    def end(self):
        ch = music21.chord.Chord(self.affectedTokens)
        ch.duration = self.affectedTokens[0].duration
        return ch

def analyze_submission():

    tempo_object = music21.tempo.MetronomeMark(number = TEMPO)

    try:

        with open("input.txt", "r") as input:
            tinyNotation_STRING = input.read().replace("\n", " ").replace("\t", " ")

        #strm = music21.converter.parse("tinyNotation: " + tinyNotation_STRING)

        # ! polyphonic scoring works, but not polyphonic playback. maybe next time... :(
        tnc = music21.tinyNotation.Converter()
        tnc.bracketStateMapping['chord'] = ChordState
        tnc.load("tinyNotation: " + tinyNotation_STRING)
        strm = tnc.parse().stream

    except:
        messagebox.showwarning("Input Error", "Entry could not be read in tN format! Please try again.")
        reset_window()
        return

    #strm.plot() # graph the music
    strm.show() # write out the music notation

    note_strm = strm.flatten().notesAndRests.stream()

    #print_note_stream_info(note_strm, tempo_object)

    # combine the notes together without using ADSR amplitude modification for each note
    tri_noADSR = np.array([])
    sin_noADSR = np.array([])
    for n in note_strm:
        try:
            midi_note = freq2midi(n.pitch.frequency)
        except:
            midi_note = freq2midi(0)
        duration_sec = tempo_object.durationToSeconds(n.duration)
        tri_noADSR = np.append(tri_noADSR, generate_triangle(midi_note, duration_sec, N_SINES))
        sin_noADSR = np.append(sin_noADSR, generate_sine(midi_note, duration_sec))

    # combine the notes together using ADSR amplitude modification for each note
    total_duration = R # because the last note will have some release time
    for n in note_strm:
        total_duration += tempo_object.durationToSeconds(n.duration)
    samples = np.arange(0, total_duration, 1.0/SAMPLE_RATE)

    fig, axs = plt.subplots(4, 1, layout='constrained')

    note_index = 0
    last_note_length = 0
    tri_ADSR = 0*samples
    sin_ADSR = 0*samples
    envelope = 0*samples
    for i, foo in enumerate(note_strm):

        note_duration = tempo_object.durationToSeconds(note_strm[i].duration)
        ADSR = generate_ADSR_envelope(note_duration, 0.04, 0.06, 0.6, 0.05)
        ADSR_len = len(ADSR)
        ADSR_duration = ADSR_len / SAMPLE_RATE

        note_index += last_note_length
        last_note_length = int(note_duration*SAMPLE_RATE)

        try:
            midi_note = freq2midi(note_strm[i].pitch.frequency)
        except:
            midi_note = freq2midi(0)
            ADSR = np.array([0 for i in ADSR])
        tri_note = generate_triangle(midi_note, ADSR_duration, N_SINES)
        sin_note = generate_sine(midi_note, ADSR_duration)

        # for graphing, append zeroes to get to total clip length - at start and end
        tn = np.append(np.zeros(note_index), tri_note)
        tn = np.append(tn, np.zeros(len(tri_ADSR) - len(tn)))
        sn = np.append(np.zeros(note_index), sin_note)
        sn = np.append(sn, np.zeros(len(sin_ADSR) - len(sn)))

        # multiply note signal array with ADSR
        r_ADSR = np.array([i/100 for i in ADSR])
        tri_note = np.multiply(tri_note, r_ADSR)
        sin_note = np.multiply(sin_note, r_ADSR)
        tri_note = tri_note[0:ADSR_len]
        sin_note = sin_note[0:ADSR_len]
        #plt.subplot(312)
        #plt.plot(ADSR, label=str(i))

        # append zeroes to get to total clip length - at start and end
        tri_note = np.append(np.zeros(note_index), tri_note)
        tri_note = np.append(tri_note, np.zeros(len(tri_ADSR) - len(tri_note)))
        sin_note = np.append(np.zeros(note_index), sin_note)
        sin_note = np.append(sin_note, np.zeros(len(sin_ADSR) - len(sin_note)))
        ADSR = np.append(np.zeros(note_index), ADSR)
        ADSR = np.append(ADSR, np.zeros(len(envelope) - len(ADSR)))
        #plt.subplot(313)
        #plt.plot(tri_note, label=str(i))

        # add note to the output
        tri_ADSR = np.add(tri_ADSR, tri_note)
        sin_ADSR = np.add(sin_ADSR, sin_note)
        for j, bar in enumerate(envelope):
            if envelope[j]>0 and ADSR[j]>0:
                envelope[j] = envelope[j] if envelope[j]>ADSR[j] else ADSR[j]
            else:
                envelope[j] += ADSR[j]

        axs[0].plot([i/44100 for i in range(len(tn))], tn)
        axs[1].plot([i/44100 for i in range(len(ADSR))], ADSR)
        axs[3].plot([i/44100 for i in range(len(tri_note))], tri_note)

    # make the output files
    try:
        os.mkdir('output')
    except:
        pass

    try:
        sf.write("output/tri_noADSR.wav", tri_noADSR, SAMPLE_RATE)
        sf.write("output/sin_noADSR.wav", sin_noADSR, SAMPLE_RATE)
        sf.write("output/tri_ADSR.wav", tri_ADSR, SAMPLE_RATE)
        sf.write("output/sin_ADSR.wav", sin_ADSR, SAMPLE_RATE)
    except:
        sf.write("tri_noADSR.wav", tri_noADSR, SAMPLE_RATE)
        sf.write("sin_noADSR.wav", sin_noADSR, SAMPLE_RATE)
        sf.write("tri_ADSR.wav", tri_ADSR, SAMPLE_RATE)
        sf.write("sin_ADSR.wav", sin_ADSR, SAMPLE_RATE)

    ax = axs[0]
    ax.set_title("Triangle Waves - No ASDR")
    ax.set_ylabel("Amplitude")

    ax = axs[1]
    ax.set_title("ADSR Envelopes")
    ax.set_ylabel("Ratio (%)")

    ax = axs[2]
    ax.plot([i/44100 for i in range(len(envelope))], envelope)
    ax.set_title("ADSR Envelope Combination")
    ax.set_ylabel("Ratio (%)")

    ax = axs[3]
    ax.set_title("ASDR")
    ax.set_ylabel("Amplitude")
    ax.set_xlabel("Time (seconds)")

    fig.align_labels()
    fig.set_size_inches(18, 9)
    fig.set_dpi(100)
    fig.suptitle(ADSR_DEMO_TITLE, fontsize=20)
    try:
        fig.savefig("output/" + ADSR_DEMO_TITLE + ".png")
    except:
        fig.savefig(ADSR_DEMO_TITLE + ".png")

    #plt.legend()
    plt.show()

#####################################################################################################
############################################### MAIN ################################################
#####################################################################################################

if __name__ == '__main__':

    if False:
        root = tk.Tk()
        root.title("Sine Note Sequencer")
        root.geometry("600x225")

        tempo_fr = tk.Frame(root)
        tempo_fr.pack(pady=20)
        tempo_entry = tk.Entry(tempo_fr, width = 4, text = "BPM:", justify = tk.CENTER)
        tempo_entry.insert(0, str(TEMPO))
        tempo_entry.pack(side = tk.LEFT, padx = 10)
        tempo_entry.bind("<FocusOut>", lambda event: validate_tempo())

        tempo_up_btn = tk.Button(tempo_fr, text = "increase tempo", command = lambda: update_tempo(1))
        tempo_up_btn.pack(side = tk.LEFT)

        tempo_dn_btn = tk.Button(tempo_fr, text = "decrease tempo", command = lambda: update_tempo(-1))
        tempo_dn_btn.pack(side = tk.LEFT)

        entry_label = tk.Label(root, text = "Enter a melody in tinyNotation format to input.txt and press SUBMIT below.\nNOTE: polyphonic scoring works, but not polyphonic playback. Sorry :(")
        entry_label.pack(pady = 5)

        submit_button = tk.Button(root, text = "SUBMIT", command = submit_score)
        submit_button.pack(pady = 20)

        reset_button = tk.Button(root, text = "Reset", command = reset_window)
        reset_button.pack(pady = 10)

        root.mainloop()

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
        hrm_signal = np.add(hrm_signal, k_harmonics(k=ex_k, amp=ex_amp, freq=f_i, duration=ADSR_duration, sample_rate=ex_sr))
        sin_signal = np.add(sin_signal, generate_sine(note_num=freq2midi(f_i), duration=ADSR_duration))
        tri_signal = np.add(tri_signal, generate_triangle(note_num=freq2midi(f_i), duration=ADSR_duration, num_sinusoids=1000))

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
