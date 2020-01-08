import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

def get_histogram(image, bins):
    # array with size of bins, set to zeros
    histogram = np.zeros(bins)
    
    # loop through pixels and sum up counts of pixels
    for pixel in image:
        histogram[pixel] += 1
    
    # return our final result
    return histogram

def cumsum(a):
    a = iter(a)
    b = [next(a)]
    for i in a:
        b.append(b[-1] + i)
    return np.array(b)

if __name__ == "__main__":
    img     = Image.open("../SEM Images/Armin241.tif")
    img     = np.asarray(img)
    flat    = img.flatten()

    hist    = get_histogram(flat, 256)
    cs      = cumsum(hist)
    nj      = (cs - cs.min()) * 255
    N       = cs.max() - cs.min()
    cs      = nj / N
    cs      = cs.astype('uint8')
    img_new = cs[flat]
    img_new = np.reshape(img_new, img.shape)

    fig     = plt.figure()

    fig.add_subplot(1, 2, 1)
    plt.imshow(img, cmap='gray')

    fig.add_subplot(1, 2, 2)
    plt.imshow(img_new, cmap='gray')

    plt.show()