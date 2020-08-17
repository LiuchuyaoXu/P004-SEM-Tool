#   File:   MatrixWindows.py
#
#   Author: Liuchuyao Xu, 2020

import cupy

def hann(width, height, returnCupy=False):
    row = cupy.hanning(width)
    col = cupy.hanning(height)
    window = cupy.outer(row, col)
    window = cupy.sqrt(window)
    if returnCupy:
        return window
    else:
        return cupy.asnumpy(window)

def hannMask(width, height, threshold, returnCupy=False):
    row = cupy.hanning(width)
    col = cupy.hanning(height)
    window = cupy.outer(row, col)
    window = cupy.sqrt(window)
    window = window > threshold
    window = window.astype(int)
    if returnCupy:
        return window
    else:
        return cupy.asnumpy(window)

def discMask(width, height, radius, returnCupy=False):
    xOrigin = (width - 1) / 2
    yOrigin = (height - 1) / 2
    xIndices, yIndices = cupy.ogrid[0:width, 0:height]
    window = (xIndices - xOrigin)**2 + (yIndices - yOrigin)**2
    window = window <= (radius * radius)
    window = window.astype(int)
    if returnCupy:
        return window
    else:
        return cupy.asnumpy(window)

def segmentMasks(width, height, returnCupy=False):
    xOrigin = (width - 1) / 2
    yOrigin = (height - 1) / 2
    xIndices, yIndices = cupy.ogrid[0:width, 0:height]
    xIndices = xIndices - xOrigin
    yIndices = yIndices - yOrigin
    window = yIndices / xIndices
    window = cupy.arctan(window)
    window = window * 180 / cupy.pi
    q1 = (window > -22.5) & (window <= 22.5)
    q2 = (window > 22.5) & (window <= 67.5)
    q3 = (window > 67.5) | (window <= -67.5)
    q4 = (window > -67.5) & (window <= -22.5)
    q1 = q1.astype(int)
    q2 = q2.astype(int)
    q3 = q3.astype(int)
    q4 = q4.astype(int)
    if returnCupy:
        return (q1, q2, q3, q4)
    else:
        return (cupy.asnumpy(q1), cupy.asnumpy(q2), cupy.asnumpy(q3), cupy.asnumpy(q4))
