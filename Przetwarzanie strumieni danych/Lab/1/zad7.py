import numpy as np
import matplotlib.pyplot as plt

def generate_2d_brown_noise_image(height, width, step_size=1.0, seed=None):
    """
    Generuje obraz 2D z szumu z podwójnym całkowaniem (podwójne cumsum)
    
    Parametry:
    - height: wysokość obrazu (liczba wierszy)
    - width: szerokość obrazu (liczba kolumn)
    - step_size: wielkość kroku (odchylenie standardowe losowych przyrostów)
    - seed: ziarno dla generatora liczb losowych (dla powtarzalności)
    
    Zwraca:
    - image: macierz 2D reprezentująca obraz wygenerowany z podwójnego cumsum
    """
    if seed is not None:
        np.random.seed(seed)
    
    # Generowanie losowych przyrostów z rozkładu normalnego
    noise = np.random.normal(0, step_size, (height, width))
    
    # Podwójne całkowanie - najpierw w poziomie, potem w pionie
    integrated_horizontal = np.cumsum(noise, axis=1)  # cumsum w kierunku X (wiersze)
    image = np.cumsum(integrated_horizontal, axis=0)  # cumsum w kierunku Y (kolumny)
    
    return image

def plot_brown_noise_image(image, title="Obraz z podwójnego cumsum 2D"):
    """
    Wyświetla obraz wygenerowany z podwójnego cumsum za pomocą imshow
    """
    plt.imshow(image, cmap='plasma', aspect='auto')
    plt.colorbar(label='Wartość')
    plt.title('Szum browna 2D')
    plt.xlabel('X (szerokość)')
    plt.ylabel('Y (wysokość)')
    
    plt.tight_layout()
    plt.suptitle(title, fontsize=14, y=1.02)
    plt.show()

# Główna część programu
if __name__ == "__main__":
    print("Generowanie obrazu 2D z podwójnego cumsum")
    print("=" * 50)
    
    # Parametry generowania obrazu
    height = 200         # wysokość obrazu
    width = 300          # szerokość obrazu
    step_size = 1.0      # wielkość kroku
    seed = 42            # dla powtarzalności wyników
    
    # Generowanie obrazu z podwójnego cumsum 2D
    image = generate_2d_brown_noise_image(height, width, step_size, seed)
    
    # Wizualizacja
    plot_brown_noise_image(image)
    
    print("\nGenerowanie zakończone!")
