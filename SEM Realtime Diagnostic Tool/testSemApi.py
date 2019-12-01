import time
import SEM_API
from imageio import imread
from matplotlib import pyplot as plt

if __name__ == "__main__":
    with SEM_API.SEM_API("remote") as sem:
        sem.UpdateImage_Start()
        time.sleep(1)
        sem.UpdateImage_Pause()
        plt.imshow(sem.img_array, cmap="gray")
        plt.show()
        sem.__exit__()
        