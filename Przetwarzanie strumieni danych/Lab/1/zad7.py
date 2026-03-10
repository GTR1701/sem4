import numpy as np
import matplotlib.pyplot as plt

def generate_2d_brown_noise(n_points, step_size=1.0, seed=None):
    """
    Generuje dwuwymiarowy szum czerwony (Browna)
    
    Parametry:
    - n_points: liczba punktów do wygenerowania
    - step_size: wielkość kroku (odchylenie standardowe losowych przyrostów)
    - seed: ziarno dla generatora liczb losowych (dla powtarzalności)
    
    Zwraca:
    - x, y: tablice numpy z współrzędnymi ścieżki ruchu Browna
    """
    if seed is not None:
        np.random.seed(seed)
    
    # Generowanie losowych przyrostów z rozkładu normalnego
    dx = np.random.normal(0, step_size, n_points)
    dy = np.random.normal(0, step_size, n_points)
    
    # Całkowanie przyrostów (suma kumulatywna) - to tworzy szum czerwony
    x = np.cumsum(dx)
    y = np.cumsum(dy)
    
    # Dodanie punktu startowego (0, 0)
    x = np.insert(x, 0, 0)
    y = np.insert(y, 0, 0)
    
    return x, y

def plot_brown_noise_2d(x, y, title="Dwuwymiarowy szum czerwony (Browna)"):
    """
    Wizualizacja dwuwymiarowego szumu czerwonego
    """
    plt.figure(figsize=(12, 5))
    
    # Wykres 1: Ścieżka ruchu Browna
    plt.subplot(1, 2, 1)
    plt.plot(x, y, 'b-', linewidth=0.8, alpha=0.7, label='Ścieżka')
    plt.scatter(x[0], y[0], color='green', s=100, label='Start', zorder=5)
    plt.scatter(x[-1], y[-1], color='red', s=100, label='Koniec', zorder=5)
    plt.grid(True, alpha=0.3)
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title('Ścieżka ruchu Browna 2D')
    plt.legend()
    plt.axis('equal')
    
    # Wykres 2: Mapa ciepła gęstości punktów
    plt.subplot(1, 2, 2)
    plt.hist2d(x, y, bins=50, cmap='Blues', alpha=0.7)
    plt.colorbar(label='Gęstość punktów')
    plt.scatter(x[0], y[0], color='green', s=100, label='Start', zorder=5)
    plt.scatter(x[-1], y[-1], color='red', s=100, label='Koniec', zorder=5)
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title('Rozkład gęstości punktów')
    plt.legend()
    
    plt.tight_layout()
    plt.suptitle(title, fontsize=14, y=1.02)
    plt.show()

def analyze_brown_noise_properties(x, y):
    """
    Analiza właściwości wygenerowanego szumu czerwonego
    """
    print("=== ANALIZA WŁAŚCIWOŚCI SZUMU CZERWONEGO 2D ===")
    print(f"Liczba punktów: {len(x)}")
    print(f"Zakres X: [{x.min():.2f}, {x.max():.2f}]")
    print(f"Zakres Y: [{y.min():.2f}, {y.max():.2f}]")
    print(f"Odchylenie standardowe X: {x.std():.2f}")
    print(f"Odchylenie standardowe Y: {y.std():.2f}")
    
    # Odległość od punktu startowego
    distances = np.sqrt(x**2 + y**2)
    print(f"Maksymalna odległość od startu: {distances.max():.2f}")
    print(f"Końcowa odległość od startu: {distances[-1]:.2f}")
    
    # Przyrosty
    dx = np.diff(x)
    dy = np.diff(y)
    steps = np.sqrt(dx**2 + dy**2)
    print(f"Średnia wielkość kroku: {steps.mean():.2f}")
    print(f"Odchylenie standardowe kroków: {steps.std():.2f}")

# Główna część programu
if __name__ == "__main__":
    print("Generowanie dwuwymiarowego szumu czerwonego (Browna)")
    print("=" * 50)
    
    # Parametry generowania
    n_points = 2000      # liczba kroków
    step_size = 1.0      # wielkość kroku
    seed = 42           # dla powtarzalności wyników
    
    # Generowanie szumu czerwonego 2D
    x, y = generate_2d_brown_noise(n_points, step_size, seed)
    
    # Analiza właściwości
    analyze_brown_noise_properties(x, y)
    
    # Wizualizacja
    plot_brown_noise_2d(x, y)
    
    # Przykład z różnymi parametrami
    print("\n" + "=" * 50)
    print("Porównanie różnych wielkości kroków")
    
    plt.figure(figsize=(15, 5))
    
    step_sizes = [0.5, 1.0, 2.0]
    colors = ['blue', 'red', 'green']
    
    for i, step in enumerate(step_sizes):
        plt.subplot(1, 3, i+1)
        x_temp, y_temp = generate_2d_brown_noise(1000, step, seed=42+i)
        plt.plot(x_temp, y_temp, color=colors[i], linewidth=0.8, alpha=0.7)
        plt.scatter(x_temp[0], y_temp[0], color='green', s=50, zorder=5)
        plt.scatter(x_temp[-1], y_temp[-1], color='red', s=50, zorder=5)
        plt.title(f'Krok = {step}')
        plt.xlabel('X')
        plt.ylabel('Y')
        plt.grid(True, alpha=0.3)
        plt.axis('equal')
    
    plt.tight_layout()
    plt.suptitle('Porównanie szumu Browna dla różnych wielkości kroków', fontsize=14, y=1.02)
    plt.show()
    
    print("\nGenerowanie zakończone!")
