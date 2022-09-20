import numpy as np
import matplotlib.pyplot as plt
import cv2
from pyxtf import xtf_read, concatenate_channel, XTFHeaderType

def xtf2png(xtfPath, pngPath, do_bottom_detection ):
    # Read file header and packets
    (fh, p) = xtf_read(xtfPath)

    print("Reading xtf data...")

    # Get multibeam/bathy data (xyza) if present
    if XTFHeaderType.bathy_xyza in p:
        np_mb = [[y.fDepth for y in x.data] for x in p[XTFHeaderType.bathy_xyza]]

        # Allocate room (with padding in case of varying sizes)
        mb_concat = np.full((len(np_mb), max([len(x) for x in np_mb])), dtype=np.float32, fill_value=np.nan)
        for i, line in enumerate(np_mb):
            mb_concat[i, :len(line)] = line

        # Transpose if the longest axis is vertical
        is_horizontal = mb_concat.shape[0] < mb_concat.shape[1]
        mb_concat = mb_concat if is_horizontal else mb_concat.T
        plt.figure()
        plt.imshow(mb_concat, cmap='hot')
        plt.colorbar(orientation='horizontal')

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
        bottom_pos1 = [ detect_bottom(np_chan1[:,i], False) for i in range(np_chan1.shape[1]) ]
        bottom_pos2 = [ detect_bottom(np_chan2[:,i], True)  for i in range(np_chan2.shape[1]) ]

        print("Blur bottom sizes...")
        bottom_pos1 = blur(bottom_pos1)
        bottom_pos2 = blur(bottom_pos2)

        print("Write bottom to image...")
        for i in range(np_chan1.shape[1]):
            np_chan1[bottom_pos1[i]:,i] = np.zeros(np_chan1.shape[0] - bottom_pos1[i])
            np_chan2[:bottom_pos2[i],i] = np.zeros(bottom_pos2[i])


    print("Create image...")
    # glue together
    glued_chan = np.vstack((np_chan1, np_chan2))

    # create img
    glued_chan /= np.amax(glued_chan) / 255

    cv2.imwrite(pngPath, glued_chan)

def blur(values):
    return [values[0], values[1]] + [ int((values[i-2] + values[i-1] + values[i] + values[i+1] + values[i+2]) / 5) for i in range(2, len(values)-2)] + [values[-2], values[-1]]


def detect_bottom(values, reverse):
    BOTTOM_THRESHHOLD = 3.1
    
    if reverse:
        values = values[::-1]

    for i in range(2, len(values)-2):
        blurred_val = values[i-2] + values[i-1] + values[i] + values[i+1] + values[i+2]
        if blurred_val < BOTTOM_THRESHHOLD * 5:
            if len(values) * 0.9 < i or values[int(i + len(values) * 0.1)] < BOTTOM_THRESHHOLD:
                return len(values) - i if reverse else i
    return len(values)



    

if __name__ == '__main__':
    xtf2png('res\\2020may29_0001.xtf', '2020may29_0001.png', True)