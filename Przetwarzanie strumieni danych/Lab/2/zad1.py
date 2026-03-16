import cv2
import os

filename = "obraz2.jpg"
current_dir = os.path.dirname(os.path.abspath(__file__))
filepath = os.path.join(current_dir, filename)
image1 = cv2.imread(filepath)

cv2.imshow('Obraz', image1)
cv2.waitKey(0)

filepath2 = os.path.join(current_dir, 'obraz_kopiowany.png')
cv2.imwrite(filepath2, image1)

cv2.destroyAllWindows()

#Zad 2 - Histogram obrazu

from matplotlib import pyplot as plt
import numpy as np

# Generowanie histogramu dla załadowanego obrazu z zadania 1
def generate_histogram(image):
    # Rozdzielenie kanałów BGR
    colors = ['b', 'g', 'r']  # Blue, Green, Red
    channel_names = ['Blue', 'Green', 'Red']
    
    # Histogram wszystkich kanałów na jednym wykresie
    plt.figure(figsize=(12, 6))
    for i in range(3):
        hist = cv2.calcHist([image], [i], None, [256], [0, 256])
        plt.hist(hist, bins=256, color=colors[i], label=channel_names[i], histtype='step', linewidth=2)
        
    plt.title('Histogram wszystkich kanałów BGR')
    plt.xlabel('Wartość piksela')
    plt.ylabel('Liczba pikseli')
    plt.xlim([0, 256])
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.show()

# Sprawdzenie czy obraz został poprawnie załadowany
if image1 is not None:
    print(f"Wymiary obrazu: {image1.shape}")
    generate_histogram(image1)
else:
    print("Błąd: Nie udało się załadować obrazu!")

