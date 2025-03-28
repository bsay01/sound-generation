import numpy as np
from PIL import Image
import winsound, time

arr = np.array([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16]])

with Image.open("josie.jpg") as im:
    # (left, upper, right, lower)
    im_crop = im.crop((220, 700, 800, 720))
    im_crop.save("josie_eyes.jpg")

