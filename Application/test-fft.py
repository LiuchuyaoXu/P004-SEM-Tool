import time
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from matplotlib.colors import LogNorm

class semImage(np.ndarray):
    def __init__(self):
        super().__init__()

    def getFft(self):
        result = np.fft.fft2(self)
        result = np.fft.fftshift(result)
        result = np.abs(result)
        return result

if __name__ == "__main__":
    image1 = Image.open("../Test Images/i3.png").convert('L')
    image1 = np.asarray(image1)
    image1 = image1.view(semImage)

    image2 = Image.open("../Test Images/i4.jpg").convert('L')
    image2 = np.asarray(image2)
    image2 = image2.view(semImage)

    image1Fft = image1.getFft()
    image2Fft = image2.getFft()

    fig, axis = plt.subplots(2, 2)
    axis[0][0].imshow(image1, cmap="gray")
    axis[1][0].imshow(image1Fft, cmap="gray", norm=LogNorm())
    axis[0][1].imshow(image2, cmap="gray")
    axis[1][1].imshow(image2Fft, cmap="gray", norm=LogNorm())
    plt.tight_layout()
    plt.show()
