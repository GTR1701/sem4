import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button

# Parametry
samples = 10000

# Inicjalizacja wykresu
fig, ax = plt.subplots()
plt.subplots_adjust(bottom=0.2)

# Funkcja do generowania szumu Browna
def generate_brown_noise():
    # 1. Generowanie szumu białego (rozkład normalny)
    white_noise = np.random.normal(0, 1, samples)
    # 2. Całkowanie szumu białego, aby uzyskać szum Browna
    brown_noise = np.cumsum(white_noise)
    # Normalizacja (opcjonalnie, do zakresu -1 do 1)
    brown_noise = brown_noise / np.max(np.abs(brown_noise))
    return brown_noise

# Początkowe generowanie szumu
brown_noise = generate_brown_noise()
line, = ax.plot(brown_noise)
ax.set_title("Szum Browna (Red Noise)")
ax.set_xlabel("Próbka")
ax.set_ylabel("Amplituda")

# Funkcja obsługująca kliknięcie przycisku
def regenerate_noise(event):
    new_brown_noise = generate_brown_noise()
    line.set_ydata(new_brown_noise)
    # Aktualizacja zakresu osi Y jeśli potrzeba
    ax.relim()
    ax.autoscale_view()
    plt.draw()

# Dodanie przycisku
ax_button = plt.axes([0.45, 0.05, 0.15, 0.04])
button = Button(ax_button, 'Regeneruj')
button.on_clicked(regenerate_noise)

plt.show()
