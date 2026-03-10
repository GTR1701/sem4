import numpy as np
import matplotlib.pyplot as plt

# Parametry
samples = 10000
# 1. Generowanie szumu białego (rozkład normalny)
white_noise = np.random.normal(0, 1, samples)
# 2. Całkowanie szumu białego, aby uzyskać szum Browna
brown_noise = np.cumsum(white_noise)

# Normalizacja (opcjonalnie, do zakresu -1 do 1)
brown_noise = brown_noise / np.max(np.abs(brown_noise))

# Wizualizacja
plt.plot(brown_noise)
plt.title("Szum Browna (Red Noise)")
plt.show()
