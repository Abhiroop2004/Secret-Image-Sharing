import numpy as np
from PIL import Image

matrix = np.random.randint(0, 256, (1, 1, 3), dtype=np.uint8)
print("Matrix:\n", matrix)

image = Image.fromarray(matrix, mode='RGB')

image.save("test_1.png")
image.show()