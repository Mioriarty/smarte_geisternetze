import multiprocessing
import numpy as np
import matplotlib.pyplot as plt
import cv2
from pyxtf import xtf_read, concatenate_channel, XTFHeaderType

def xtf2png(xtfPath, pngPath, do_bottom_detection, do_cutting, bottom_detection_threshhold = 3.1, processes = 8, slice_width = 450 ):
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
        # bottom detect
        print("Determine bottom size...")
        with multiprocessing.Pool(processes = processes) as pool:
            bottom_pos1 = pool.starmap(detect_bottom, [ (np_chan1[:,i], bottom_detection_threshhold) for i in range(np_chan1.shape[1]) ])
            bottom_pos2 = pool.starmap(detect_bottom_reversed, [ (np_chan2[:,i], bottom_detection_threshhold) for i in range(np_chan2.shape[1]) ])   

        print("Blur bottom sizes...")
        bottom_pos1 = blur(blur(bottom_pos1))
        bottom_pos2 = blur(blur(bottom_pos2))

        print("Write bottom to image...")
        for i in range(np_chan1.shape[1]):
            np_chan1[bottom_pos1[i]:,i] = np.zeros(np_chan1.shape[0] - bottom_pos1[i])
            np_chan2[:bottom_pos2[i],i] = np.zeros(bottom_pos2[i])


    np_chan1 /= np.amax(np_chan1) / 255
    np_chan2 /= np.amax(np_chan2) / 255

    if do_cutting:
        print("Create slices...")

        for i in range(np_chan1.shape[1] // slice_width):
            slice1 = np_chan1[:,i*slice_width:(i+1)*slice_width]
            slice2 = np_chan2[:,i*slice_width:(i+1)*slice_width]
            filename = pngPath[:-4] + "_" + str(i * slice_width)
            
            if not should_discard_slice(slice1):
                cv2.imwrite(filename + "_top.png", slice1)
            
            if not should_discard_slice(slice2):
                cv2.imwrite(filename + "_bot.png", slice2)


    else:
        print("Create image...")
        # create img
        # glue together
        glued_chan = np.vstack((np_chan1, np_chan2))
        
        cv2.imwrite(pngPath, glued_chan)

def blur(values):
    return [values[0], values[1]] + [ int((values[i-2] + values[i-1] + values[i] + values[i+1] + values[i+2]) / 5) for i in range(2, len(values)-2)] + [values[-2], values[-1]]

def detect_bottom(values, threshhold):
    value_length = len(values)
    recheck_jump = int(value_length * 0.1)

    for i in range(int(value_length * 0.2), value_length):
        if values[i] < threshhold:
            if i + recheck_jump >= value_length or values[i + recheck_jump] < threshhold:
                if i + 2*recheck_jump >= value_length or values[i + 2*recheck_jump] < threshhold:
                    return i

        
    return value_length

def detect_bottom_reversed(values, threshhold):
    value_length = len(values)
    recheck_jump = int(value_length * 0.1)


    for i in range(int(value_length * 0.8), 0, -1):
        if values[i] < threshhold:
            if i - recheck_jump < 0 or values[i - recheck_jump] < threshhold:
                if i - 2*recheck_jump < 0 or values[i - 2*recheck_jump] < threshhold:
                    return i

    return 0

def should_discard_slice(slice):
    nonzero = slice[slice != 0]

    # to much black (more than 75%)
    if nonzero.size < slice.size * 0.25:
        return True
    
    # no black at all (cannot be real data, bottom missing)
    if nonzero.size > slice.size * 0.96:
        return True
    
    return False
    

if __name__ == '__main__':
    xtf2png('res\\2019apr04_ecker_sued_10002.xtf', '2019apr04_ecker_sued_10002.png', True, False)