import time
import numpy as np
import cupy as cp
import matplotlib.pyplot as plt

# size
# complexity
# repeat by 10 times

N = np.asarray([1, 10, 100, 200, 400, 600, 800, 1000, 2000, 3000, 4000])
# N = np.asarray([1, 10, 100, 1000, 10000, 100000, 200000, 400000, 600000, 800000, 1000000, 2000000, 4000000, 6000000, 8000000, 10000000])
TNp = np.asarray([])
TCp = np.asarray([])

# for n in N:
#     tNp = np.asarray([])
#     tCp = np.asarray([])
#     for i in range(10):
#         v1 = np.random.rand(n)
#         v2 = np.random.rand(n)
#         start = time.time()
#         v3 = np.add(v1, v2)
#         end = time.time()
#         tNp = np.append(tNp, end-start)

#         v1 = cp.random.rand(n)
#         v2 = cp.random.rand(n)
#         start = time.time()
#         v3 = cp.add(v1, v2)
#         end = time.time()
#         tCp = np.append(tCp, end-start)
#     TNp = np.append(TNp, np.average(tNp))
#     TCp = np.append(TCp, np.average(tCp))
# TNp = 1000 * TNp
# TCp = 1000 * TCp
# TNp = TNp.astype(int)
# TCp = TCp.astype(int)

for n in N:
    tNp = np.asarray([])
    tCp = np.asarray([])
    for i in range(10):
        m1 = np.random.rand(n, n)
        m2 = np.random.rand(n, n)
        start = time.time()
        m3 = np.matmul(m1, m2)
        end = time.time()
        tNp = np.append(tNp, end-start)

        m1 = cp.random.rand(n, n)
        m2 = cp.random.rand(n, n)
        start = time.time()
        m3 = cp.matmul(m1, m2)
        end = time.time()
        tCp = np.append(tCp, end-start)
    TNp = np.append(TNp, np.average(tNp))
    TCp = np.append(TCp, np.average(tCp))
TNp = 1000 * TNp
TCp = 1000 * TCp
TNp = TNp.astype(int)
TCp = TCp.astype(int)

plt.rcParams.update({'font.size': 12})
fig = plt.figure()
ax = fig.add_subplot(111)
ax.set_ylabel("Time taken (ms)")
ax.set_xlabel("Matrix dimension parameter (N)")
ax.scatter(N, TNp, c='b', marker='o', label='CPU')
ax.scatter(N, TCp, c='r', marker='^', label='CUDA')
ax.legend()
plt.show()
