import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from scipy.linalg import circulant

def createTestImage():
    image = np.linspace(-100, 100, 1000)
    image = np.sin(image) + np.sin(image / 2)
    # image = np.tile(image, (image.size, 1))
    image = circulant(image)

    # image = np.rot90(image)
    # image = image + np.rot90(image)
    image = 255 * image

    im = Image.fromarray(image)
    im = im.convert("L")
    im.save("Images for FFT Testing/xy5.tif")

    # plt.axis("off")
    # plt.imshow(image, cmap="gray")
    # plt.show()

def createTestImage2():
    image = np.array([0, 0, 0, 0, 0, 255, 255, 255, 255, 255])
    image = np.tile(image, (1000, 100))
    image = np.rot90(image)

    image = Image.fromarray(image)
    image = image.convert("L")
    image.save("Images for FFT Testing/V3.tif")

if __name__ == "__main__":
    createTestImage2()
