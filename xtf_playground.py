import pyxtf
import numpy as np
import matplotlib.pyplot as plt

test_file = 'res\\2019apr04_ecker_sued_10002.xtf'
(fh, p) = pyxtf.xtf_read(test_file)

print(fh)

input()

n_channels = fh.channel_count(verbose=True)
actual_chan_info = [fh.ChanInfo[i] for i in range(0, n_channels)]
print('Number of data channels: {}\n'.format(n_channels))

input()

# Print the first channel
print(actual_chan_info[0])

input()

sonar_ch = p[pyxtf.XTFHeaderType.sonar]  # type: List[pyxtf.XTFPingHeader]

# Each element in the list is a ping (XTFPingHeader)
# This retrieves the first ping in the file of the sonar type
sonar_ch_ping1 = sonar_ch[0]

# The properties in the header defines the attributes common for all subchannels 
# (e.g sonar often has port/stbd subchannels)
print(sonar_ch_ping1)

input()

sonar_subchan0 = sonar_ch_ping1.data[0]  # type: np.ndarray
sonar_subchan1 = sonar_ch_ping1.data[1]  # type: np.ndarray

print(sonar_subchan0.shape)
print(sonar_subchan1.shape)

input()

fig, (ax1, ax2) = plt.subplots(2,1, figsize=(12,8))
ax1.semilogy(np.arange(0, sonar_subchan0.shape[0]), sonar_subchan0)
ax2.semilogy(np.arange(0, sonar_subchan1.shape[0]), sonar_subchan1)

plt.savefig("one_ping.png")

input()

sonar_ping1_ch_header0 = sonar_ch_ping1.ping_chan_headers[0]
print(sonar_ping1_ch_header0)

input()

np_chan1 = pyxtf.concatenate_channel(p[pyxtf.XTFHeaderType.sonar], file_header=fh, channel=0, weighted=True)
np_chan2 = pyxtf.concatenate_channel(p[pyxtf.XTFHeaderType.sonar], file_header=fh, channel=1, weighted=True)

print(np_chan1)
print(np_chan2)

input()

# Clip to range (max cannot be used due to outliers)
# More robust methods are possible (through histograms / statistical outlier removal)
upper_limit = 2 ** 14
np_chan1.clip(0, upper_limit-1, out=np_chan1)
np_chan2.clip(0, upper_limit-1, out=np_chan2)

# The sonar data is logarithmic (dB), add small value to avoid log10(0)
np_chan1 = np.log10(np_chan1 + 0.0001)
np_chan2 = np.log10(np_chan2 + 0.0001)

# Transpose so that the largest axis is horizontal
np_chan1 = np_chan1 if np_chan1.shape[0] < np_chan1.shape[1] else np_chan1.T
np_chan2 = np_chan2 if np_chan2.shape[0] < np_chan2.shape[1] else np_chan2.T

# The following plots the waterfall-view in separate subplots
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 12))
ax1.imshow(np_chan1, cmap='gray', vmin=0, vmax=np.log10(upper_limit))
ax2.imshow(np_chan2, cmap='gray', vmin=0, vmax=np.log10(upper_limit))

plt.savefig("all_pings.png")