import numpy as np
import matplotlib.pyplot as plt
import cv2
from pyxtf import xtf_read, concatenate_channel, XTFHeaderType

def xtf2png(xtfPath, pngPath):
    # Read file header and packets
    (fh, p) = xtf_read(xtfPath)

    print('The following (supported) packets are present (XTFHeaderType:count): \n\t' +
        str([key.name + ':{}'.format(len(v)) for key, v in p.items()]))

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

    # The following plots the waterfall-view in separate subplots
    fig, (ax1, ax2) = plt.subplots(2, 1)
    ax1.imshow(np_chan1, cmap='gray', vmin=0, vmax=np.log10(upper_limit))
    ax2.imshow(np_chan2, cmap='gray', vmin=0, vmax=np.log10(upper_limit))
    fig.tight_layout()

    # glue together
    glued_chan = np.vstack((np_chan1, np_chan2))

    # create img
    glued_chan /= np.amax(glued_chan) / 255
    cv2.imwrite(pngPath, glued_chan)

if __name__ == '__main__':
    xtf2png('res\\2019apr04_ecker_sued_10002.xtf', '2019apr04_ecker_sued_10002.png')