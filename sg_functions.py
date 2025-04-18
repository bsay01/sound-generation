import numpy as np
import math
import mido, time
from mido import Message, MidiFile, MidiTrack
import re

# functions defined for use in this repository, common to almost every script

def freq2midi(freq: float):
    return int(12 * math.log2(freq/440) + 69) if freq > 0 else -1

def midi2freq(note_num: int):
    return 440 * pow(2, (note_num - 69) / 12) if note_num >= 0 and note_num < 128 else 0

def generate_triangle(note_num: int, duration: float, num_sinusoids: int, sr: int):
    freq = midi2freq(note_num)
    t = np.arange(0, duration, 1.0/sr)
    output = 0*t
    for i in range(num_sinusoids):
        n = 2*i+1
        new_harm = (pow(-1,i)/pow(n,2)) * np.sin(2*np.pi*freq*n*t)
        output = np.add(output, new_harm)
    return np.multiply(output, 8/pow(np.pi,2))

def generate_sine(note_num: int, duration: float, sr: int):
    return np.sin(2*np.pi*midi2freq(note_num)*np.arange(0, duration, 1.0/sr))

def k_harmonics(k, amp, freq, duration, sr):
    silent_seg = 0 * np.arange(0, duration, 1.0/sr)
    output = np.array(silent_seg)
    for n in range(k):
        new_harm = amp/(n+1) * np.sin(2 * np.pi * (n+1)*freq * np.arange(0, duration, 1.0/sr))
        output = np.add(output, new_harm)
    return output

def generate_ADSR_envelope(duration:float, A:float=0.04, D:float=0.06, S:float=0.6, R:float=0.05, sr:int=44100):
    attack  = np.array([             i/A for i in np.arange(0,        A, 1.0/sr)])
    decay   = np.array([ (1-((1-S)/D)*i) for i in np.arange(0,        D, 1.0/sr)])
    sustain = np.array([               S for i in np.arange(0, duration, 1.0/sr)])
    ADS = np.append(np.append(attack, decay), sustain)[0:int(duration*sr)]
    last = ADS[-1]
    release = np.array([(-last/R*i+last) for i in np.arange(0,        R, 1.0/sr)])
    return np.array([i*100 for i in np.append(ADS, release)])

def generate_signals(notes, k=8, amp=1.0, sr=44100):

    hrm = sin = tri = np.array([])
    for note in notes:

        ADSR = generate_ADSR_envelope(note[1], 0.04, 0.06, 0.6, 0.05)
        ADSR_len = len(ADSR)
        ADSR_duration = ADSR_len / sr

        hrm_signal = 0*ADSR
        sin_signal = 0*ADSR
        tri_signal = 0*ADSR
        for f_i in [note[0]]:
            h = k_harmonics(k=k, amp=amp, freq=f_i, duration=ADSR_duration, sr=sr)
            s = generate_sine(note_num=freq2midi(f_i), duration=ADSR_duration, sr=sr)
            t = generate_triangle(note_num=freq2midi(f_i), duration=ADSR_duration, num_sinusoids=1000, sr=sr)
            while len(hrm_signal) < len(h):
                hrm_signal = np.append(hrm_signal, [0])
            while len(sin_signal) < len(s):
                sin_signal = np.append(sin_signal, [0])
            while len(tri_signal) < len(t):
                tri_signal = np.append(tri_signal, [0])
            hrm_signal = np.add(hrm_signal, h)
            sin_signal = np.add(sin_signal, s)
            tri_signal = np.add(tri_signal, t)

        r_ADSR = np.array([i/100 for i in ADSR])
        while len(r_ADSR) < len(hrm_signal):
            r_ADSR = np.append(r_ADSR, [0])
        hrm_signal_ADSR = np.multiply(hrm_signal, r_ADSR)[0:ADSR_len]
        sin_signal_ADSR = np.multiply(sin_signal, r_ADSR)[0:ADSR_len]
        tri_signal_ADSR = np.multiply(tri_signal, r_ADSR)[0:ADSR_len]

        hrm = np.append(hrm, hrm_signal_ADSR)
        sin = np.append(sin, sin_signal_ADSR)
        tri = np.append(tri, tri_signal_ADSR)

    return [hrm, sin, tri, notes]

def create_midi_from_notes(note_list, output_file='output.mid', tempo=500000, time_signature=(4, 4)):
    """
    Create a MIDI file from a list of notes and durations.

    Args:
        note_list: List of tuples in format (note_number, duration_seconds)
        output_file: Name of the output MIDI file
        tempo: Microseconds per quarter note (default 500000 = 120 BPM)
        time_signature: Tuple of (numerator, denominator)
    """
    # Create a new MIDI file and track
    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)

    # Set tempo and time signature
    track.append(mido.MetaMessage('set_tempo', tempo=tempo))
    track.append(mido.MetaMessage('time_signature',
                                 numerator=time_signature[0],
                                 denominator=time_signature[1]))

    # Convert seconds to ticks
    ticks_per_beat = mid.ticks_per_beat
    seconds_per_beat = tempo / 1_000_000  # Convert microseconds to seconds

    for note, duration in note_list:
        # Note on event (velocity=64 is a moderate volume)
        track.append(Message('note_on', note=note, velocity=64, time=0))

        # Calculate duration in ticks
        duration_ticks = int((duration / seconds_per_beat) * ticks_per_beat)

        # Note off event after the duration
        track.append(Message('note_off', note=note, velocity=64, time=duration_ticks))

    # Save the MIDI file
    mid.save(output_file)
    print(f"MIDI file saved as {output_file}")

def read_integers_from_file(filename: str) -> list[int]:
    integers = []
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            contents = file.read()
            tokens = re.split(r'\s+', contents) # Split on any whitespace
            for token in tokens:
                if re.fullmatch(r'-?\d+', token) is not None:
                    integers.append(int(token))
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        raise
    return integers

# converts a list of values into a list of values corresponding to the new range
def lov_to_new_range(l:list, old_min, old_max, new_min=0, new_max=6, format="i"):

    new_min = float(new_min)
    new_max = float(new_max)

    # determine current range
    #old_max = max(l)
    #old_min = min(l)

    # convert to new range
    old_max -= old_min
    r = new_max - new_min
    l_zto_f = [(new_min + float((i-old_min)/old_max)*float(r)) for i in l]

    if format == "i":
        return [round(i) for i in l_zto_f]
    elif format == "f":
        return l_zto_f
    else:
        raise Exception("funky format wdym")
