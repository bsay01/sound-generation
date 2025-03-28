import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import soundfile as sf
from sg_functions import *
import math, winsound, time

SAMPLE_RATE = 44100
ns_dur = [50, 300] # note duration range
output_dir = "output/img/"

def RGB_to_HEXstr(R, G, B):
    h_n = [math.floor(R/16), R%16, math.floor(G/16), G%16, math.floor(B/16), B%16]
    h_h = [hex(i)[2:] for i in h_n]
    h_s = ""
    for i in h_h:
        h_s += i
    return "0x" + h_s

def image_to_px_array(image_name:str, format:str="jpg"):

    try:
        img = Image.open(image_name + "." + format) # open image
        px = list(img.getdata()) # get image pixel data
        width, height = img.size # get image height and width in pixels

        # accessible as array[row][col]
        px_a = [px[i*width:(i+1)*width] for i in range(height)] # turn it into an array, with rows and columns y'know?
    except:
        raise Exception("error analyzing image file")

    return px_a

# prints an array of tuples to a text file, input matches the output of "image_to_px_array"
def aot_to_tf(array, file_name:str):
    with open(file_name + ".txt", "w") as tf:
        for row in array:
            row_str = "["
            for t in row:
                row_str += "("
                for i in t:
                    row_str += "{0:3d},".format(i)
                row_str = row_str[:-1]
                row_str += "), "
            row_str = row_str[:-2]
            row_str += "]\n"
            tf.write(row_str)

# prints an array to a text file
def a_to_tf(array, file_name:str):
    with open(file_name + ".txt", "w") as tf:
        for row in array:
            row_str = "["
            for t in row:
                row_str += "{0:5d},".format(t)
            row_str = row_str[:-2]
            row_str += "]\n"
            tf.write(row_str)

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

def main():

    print()

    start_time = time.time()

    # A MAJ
    # A4 (440 Hz), B4 (493.88 Hz), C5 (523.25 Hz), D5 (587.33 Hz), E5 (659.25 Hz), F#5 (739.99 Hz), G5 (783.99 Hz)
    ns_opt2 = [440.00, 493.88, 523.25, 587.33, 659.25, 739.99, 783.99]
    ns_opt1 = [float(i/2) for i in ns_opt2]
    ns_opt0 = [float(i/4) for i in ns_opt2]
    ns_options = ns_opt0 + ns_opt1 + ns_opt2

    with Image.open("josie.jpg") as im:
        # (left, upper, right, lower)
        im_crop = im.crop((220, 700, 800, 720))
        im_crop.save("josie_eyes.jpg")

    px_a = image_to_px_array("josie_eyes") # turn image into an array of pixel colour data

    hexval_a = []
    for px_row in px_a:
        hexval_row = []
        for px in px_row:
            hexval_row.append(int(RGB_to_HEXstr(px[0],px[1],px[2]), 16))
        hexval_a.append(hexval_row)

    brightness_a = []
    for px_row in px_a:
        brightness_row = []
        for px in px_row:
            brightness_row.append(int(px[0] + px[1] + px[2]))
        brightness_a.append(brightness_row)

    print("            pixel array: h={:4d}, w={:4d}".format(len(px_a), len(px_a[0])))
    print("hexadecimal value array: h={:4d}, w={:4d}".format(len(hexval_a), len(hexval_a[0])))
    print(" brightness value array: h={:4d}, w={:4d}".format(len(brightness_a), len(brightness_a[0])))

    aot_to_tf(px_a, output_dir + "image_to_sound_px")
    a_to_tf(hexval_a, output_dir + "image_to_sound_hex")
    a_to_tf(brightness_a, output_dir + "image_to_sound_bri")

    h_max = max([max(r) for r in hexval_a])
    h_min = min([min(r) for r in hexval_a])
    b_max = max([max(r) for r in brightness_a])
    b_min = min([min(r) for r in brightness_a])

    print()
    print("hex: [{},{}]".format(h_min, h_max))
    print("bri: [{},{}]".format(b_min, b_max))

    t_p = time.time() - start_time
    print("\ntime to process image: {:0.2f} sec ({:0.2f} min)".format(t_p, t_p/60))

    print("\nbegin processing {} rows of image data.".format(len(px_a)))

    winsound.Beep(220, 500)
    sound_pt_start = time.time()

    for img_row in range(len(px_a)):

        note_values = lov_to_new_range(hexval_a[img_row], h_min, h_max, 0, len(ns_options)-1)
        dur_values = lov_to_new_range(brightness_a[img_row], b_min, b_max, ns_dur[0], ns_dur[1])

        print("\nbegin processing for row {}...".format(img_row))
        print("    note index: max = {:3d}, min = {:3d}".format(max(note_values), min(note_values)))
        print("duration value: max = {:3d}, min = {:3d}".format(max(dur_values), min(dur_values)))
        pt_start = time.time()

        ns_values = []
        for i in range(len(note_values)):
            ns_values.append([ns_options[note_values[i]], (dur_values[i])/1000])

        ########################################## GEN SIGNAL ###########################################

        out = generate_signals(ns_values, amp=0.5)
        hrm = out[0]
        sin = out[1]
        tri = out[2]

        ######################################## MAKE WAV FILES #########################################

        try:
            sf.write(output_dir + str(img_row) + "_hrm_rand.wav", hrm, SAMPLE_RATE)
        except:
            sf.write(str(img_row) + "_hrm_rand.wav", hrm, SAMPLE_RATE)

        # try:
        #     sf.write(output_dir + str(img_row) + "_sin_rand.wav", sin, SAMPLE_RATE)
        # except:
        #     sf.write(str(img_row) + "_sin_rand.wav", sin, SAMPLE_RATE)

        # try:
        #     sf.write(output_dir + str(img_row) + "_tri_rand.wav", tri, SAMPLE_RATE)
        # except:
        #     sf.write(str(img_row) + "_tri_rand.wav", tri, SAMPLE_RATE)

        t_p = time.time() - pt_start
        print("processing time: {:0.2f} sec ({:0.2f} min)".format(t_p, t_p/60))

    t_p = time.time() - sound_pt_start
    print("\ntime to create sounds: {:0.2f} sec ({:0.2f} min)".format(t_p, t_p/60))

    t_p = time.time() - start_time
    print("\ntotal execution time: {:0.2f} sec ({:0.2f} min)\n".format(t_p, t_p/60))

    for a in range(6):
        for i in range(3):
            for j in range(3):
                winsound.Beep(220*(j+1), 100)
                time.sleep(float(50)/1000)
        time.sleep(1)

if __name__ == "__main__":
    main()
