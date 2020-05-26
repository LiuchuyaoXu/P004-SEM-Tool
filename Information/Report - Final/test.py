import time
import numpy as np
import cupy as cp
import matplotlib.pyplot as plt

# N = np.asarray([1, 10, 100, 1000, 10000, 100000, 200000, 400000, 600000, 800000, 1000000, 2000000, 4000000, 6000000, 8000000, 10000000])
N = np.linspace(100000, 140960, 128).astype(int)
TNp = np.asarray([])
TCp = np.asarray([])
for n in N:
    tNp = np.asarray([])
    tCp = np.asarray([])
    for i in range(10):
        v1 = np.random.rand(n)
        v2 = np.random.rand(n)
        start = time.time_ns()
        v3 = np.add(v1, v2)
        end = time.time_ns()
        tNp = np.append(tNp, end-start)

        v1 = cp.array(v1)
        v2 = cp.array(v2)
        start = time.time_ns()
        v3 = cp.add(v1, v2)
        end = time.time_ns()
        tCp = np.append(tCp, end-start)
    TNp = np.append(TNp, np.average(tNp))
    TCp = np.append(TCp, np.average(tCp))
TNp = TNp / 1000000
TCp = TCp / 1000000
# TNp = TNp.astype(int)
# TCp = TCp.astype(int)
N = np.delete(N, 0)
TNp = np.delete(TNp, 0)
TCp = np.delete(TCp, 0)

plt.rcParams.update({'font.size': 12})
fig = plt.figure()
ax = fig.add_subplot(111)
ax.set_ylabel("Time taken (ms)")
ax.set_xlabel("Vector size (N)")
ax.scatter(N, TNp, c='b', marker='o', label='CPU')
ax.scatter(N, TCp, c='r', marker='^', label='CUDA')
ax.legend()
ax.ticklabel_format(style='sci', axis='x', scilimits=(0,0))
plt.show()

# N = np.asarray([1, 10, 100, 200, 400, 600, 800, 1000, 2000])
# TNp = np.asarray([])
# TCp = np.asarray([])
# for n in N:
#     tNp = np.asarray([])
#     tCp = np.asarray([])
#     for i in range(10):
#         m1 = np.random.rand(n, n)
#         m2 = np.random.rand(n, n)
#         start = time.time()
#         m3 = np.matmul(m1, m2)
#         end = time.time()
#         tNp = np.append(tNp, end-start)

#         m1 = cp.random.rand(n, n)
#         m2 = cp.random.rand(n, n)
#         start = time.time()
#         m3 = cp.matmul(m1, m2)
#         end = time.time()
#         tCp = np.append(tCp, end-start)
#     TNp = np.append(TNp, np.average(tNp))
#     TCp = np.append(TCp, np.average(tCp))
# TNp = 1000 * TNp
# TCp = 1000 * TCp
# TNp = TNp.astype(int)
# TCp = TCp.astype(int)

# plt.rcParams.update({'font.size': 12})
# fig = plt.figure()
# ax = fig.add_subplot(111)
# ax.set_ylabel("Time taken (ms)")
# ax.set_xlabel("Matrix dimension parameter (N)")
# ax.scatter(N, TNp, c='b', marker='o', label='CPU')
# ax.scatter(N, TCp, c='r', marker='^', label='CUDA')
# ax.legend()
# plt.show()

 
 
# samplingFrequency = 100
# samplingInterval = 1 / samplingFrequency

# beginTime = 0
# endTime = 5

# signal1Frequency = 1
# signal2Frequency = 10
# time = np.arange(beginTime, endTime, samplingInterval)
# amplitude1 = np.sin(2*np.pi*signal1Frequency*time)
# amplitude2 = np.sin(2*np.pi*signal2Frequency*time)
# figure, axis = plt.subplots(4, 1)
# plt.subplots_adjust(hspace=1)

# axis[1].set_title('1 Hz sine wave')
# axis[1].plot(time, amplitude1)
# axis[1].set_xlabel('Time')
# axis[1].set_ylabel('Amplitude')

# axis[2].set_title('10 Hz sine wave')
# axis[2].plot(time, amplitude2)
# axis[2].set_xlabel('Time')
# axis[2].set_ylabel('Amplitude')

# amplitude = amplitude1 + amplitude2
# axis[0].set_title('Composite wave')
# axis[0].plot(time, amplitude)
# axis[0].set_xlabel('Time')
# axis[0].set_ylabel('Amplitude')

# fourierTransform = np.fft.fft(amplitude)/len(amplitude)           # Normalize amplitude
# fourierTransform = fourierTransform[range(int(len(amplitude)/2))] # Exclude sampling frequency

# tpCount     = len(amplitude)
# values      = np.arange(int(tpCount/2))
# timePeriod  = tpCount/samplingFrequency
# frequencies = values/timePeriod

# axis[3].set_title('Fourier transform of the composite wave')
# axis[3].plot(frequencies, abs(fourierTransform))
# axis[3].set_xlabel('Frequency')
# axis[3].set_ylabel('Amplitude')

# plt.show()




# from numpy.fft import fft, fftshift
# window = np.hamming(51)
# plt.plot(window)
# plt.title("Hamming window")
# plt.ylabel("Amplitude")
# plt.xlabel("Sample")
# plt.show()

