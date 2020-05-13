image = SemImage(data)
image.applyHamming()
fft = image.fft
image.applyHistogramEqualisation()