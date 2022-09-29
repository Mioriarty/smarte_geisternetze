import multiprocessing
import numpy as np
import matplotlib.pyplot as plt
import cv2
from pyxtf import xtf_read, concatenate_channel, XTFHeaderType

def xtf2png(xtfPath, pngPath, do_bottom_detection, do_cutting, bottom_detection_threshhold = 3.1, bottom_detection_safety_offset = 30, processes = 8, slice_width = 450 ):
    # Read file header and packets
    print("Reading xtf data...")
    (fh, p) = xtf_read(xtfPath)

    # Get sonar if present
    upper_limit = 2 ** 16
    np_chan1 = concatenate_channel(p[XTFHeaderType.sonar], file_header=fh, channel=0, weighted=True)
    np_chan2 = concatenate_channel(p[XTFHeaderType.sonar], file_header=fh, channel=1, weighted=True)

    # Clip to range (max cannot be used due to outliers)
    # More robust methods are possible (through histograms / statistical outlier removal)
    np_chan1.clip(0, upper_limit - 1, out=np_chan1)
    np_chan2.clip(0, upper_limit - 1, out=np_chan2)

    # The sonar data is logarithmic (dB), add small value to avoid log10(0)
    np_chan1 = np.log10(np_chan1 + 1, dtype=np.float32)
    np_chan2 = np.log10(np_chan2 + 1, dtype=np.float32)

    # Transpose so that the largest axis is horizontal
    np_chan1 = np_chan1 if np_chan1.shape[0] < np_chan1.shape[1] else np_chan1.T
    np_chan2 = np_chan2 if np_chan2.shape[0] < np_chan2.shape[1] else np_chan2.T

    if do_bottom_detection:
        # bottom detect multithreaded
        print("Determine bottom size...")
        with multiprocessing.Pool(processes = processes) as pool:
            bottom_pos1 = pool.starmap(detect_bottom, [ (np_chan1[:,i], bottom_detection_threshhold, bottom_detection_safety_offset) for i in range(np_chan1.shape[1]) ])
            bottom_pos2 = pool.starmap(detect_bottom_reversed, [ (np_chan2[:,i], bottom_detection_threshhold, bottom_detection_safety_offset) for i in range(np_chan2.shape[1]) ])   

        # blur the bottom to reduce single errors
        print("Blur bottom sizes...")
        bottom_pos1 = blur(blur(bottom_pos1))
        bottom_pos2 = blur(blur(bottom_pos2))

        # write the sizes to mask files
        print("Write bottom to mask...")
        mask1 = np.full(np_chan1.shape, 255)
        mask2 = np.full(np_chan2.shape, 255)
        for i in range(np_chan1.shape[1]):
            mask1[bottom_pos1[i]:,i] = np.zeros(np_chan1.shape[0] - bottom_pos1[i])
            mask2[:bottom_pos2[i],i] = np.zeros(bottom_pos2[i])

    # map values to fit between 0 and 255
    np_chan1 /= np.amax(np_chan1) / 255
    np_chan2 /= np.amax(np_chan2) / 255

    if do_cutting:
        # slice big image
        print("Create slices...")
        slice_image(np_chan1, pngPath[:-4], "_top", slice_width)
        slice_image(np_chan2, pngPath[:-4], "_bot", slice_width)

        if do_bottom_detection:
            # slice masks if exists
            slice_image(mask1, pngPath[:-4], "_top_mask", slice_width)
            slice_image(mask2, pngPath[:-4], "_bot_mask", slice_width)

    else:
        # create big image 
        print("Create image...")
        glued_chan = np.vstack((np_chan1, np_chan2))
        cv2.imwrite(pngPath, glued_chan)

        if do_bottom_detection:
            # create mask of big image if nexcessary
            glued_mask = np.vstack((mask1, mask2))
            cv2.imwrite(pngPath[:-4] + "_" + "mask" + ".png", glued_mask)


# avarage the 5 values close by and keeps first and last 2
def blur(values):
    return [values[0], values[1]] + [ int((values[i-2] + values[i-1] + values[i] + values[i+1] + values[i+2]) / 5) for i in range(2, len(values)-2)] + [values[-2], values[-1]]

# detects how large the bottom is in a pixel row by a threshhold
def detect_bottom(values, threshhold, safety_offset):
    value_length = len(values)
    # after a pixel blow the threshhold it will jump by this amount to check if this is alsoe below that threshold. This will happen twice
    recheck_jump = int(value_length * 0.1)

    for i in range(int(value_length * 0.2), int(value_length * 0.98)):
        if values[i] < threshhold:
            if i + recheck_jump >= value_length or values[i + recheck_jump] < threshhold:
                if i + 2*recheck_jump >= value_length or values[i + 2*recheck_jump] < threshhold:
                    return max(i - safety_offset, 0)

    # return maximum value if nohting was found
    return 0

# does the same as detect_bottom but it goes through the pixel in reverse order. This is necessary as the other stripe is also reversed
def detect_bottom_reversed(values, threshhold, safety_offset):
    value_length = len(values)
    recheck_jump = int(value_length * 0.1)


    for i in range(int(value_length * 0.8), int(value_length * 0.02), -1):
        if values[i] < threshhold:
            if i - recheck_jump < 0 or values[i - recheck_jump] < threshhold:
                if i - 2*recheck_jump < 0 or values[i - 2*recheck_jump] < threshhold:
                    return min(i + safety_offset, value_length - 1)

    return value_length

# just slices up the images in slices and write it to the file system
def slice_image(image, filename, suffix, slice_width):
    for i in range(image.shape[1] // slice_width):
        slice = image[:,i*slice_width:(i+1)*slice_width]
        this_filename = filename + "_" + str(i * slice_width) + suffix + ".png"
        
        cv2.imwrite(this_filename, slice)

    

if __name__ == '__main__':
    xtf2png('res/2020may29_0001.xtf', 'bla.png', True, False)