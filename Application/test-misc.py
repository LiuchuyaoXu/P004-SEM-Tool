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
    im.save("Test Images/xy5.tif")

    # plt.axis("off")
    # plt.imshow(image, cmap="gray")
    # plt.show()

if __name__ == "__main__":
    createTestImage()
