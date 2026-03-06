import numpy as np
import matplotlib.pyplot as plt

def generate_normal_timeseries():
    """
    Generuje kilka przebiegów czasowych z rozkładu normalnego dla różnych parametrów
    i przedstawia ich histogramy
    """
    
    # Ustawienie seed dla powtarzalności wyników
    np.random.seed(42)
    
    # Parametry dla różnych przebiegów
    parameters = [
        {'mean': 0, 'std': 1, 'size': 1000, 'label': 'μ=0, σ=1'},
        {'mean': 5, 'std': 2, 'size': 1000, 'label': 'μ=5, σ=2'},
        {'mean': -2, 'std': 0.5, 'size': 1000, 'label': 'μ=-2, σ=0.5'},
        {'mean': 10, 'std': 3, 'size': 1500, 'label': 'μ=10, σ=3'}
    ]
    
    # Generowanie przebiegów czasowych
    timeseries = []
    for params in parameters:
        ts = np.random.normal(
            loc=params['mean'], 
            scale=params['std'], 
            size=params['size']
        )
        timeseries.append({
            'data': ts,
            'params': params
        })
        print(f"Wygenerowano przebieg: {params['label']}")
        print(f"  Rzeczywista średnia: {np.mean(ts):.3f}")
        print(f"  Rzeczywiste odchylenie standardowe: {np.std(ts):.3f}")
        print(f"  Min: {np.min(ts):.3f}, Max: {np.max(ts):.3f}")
        print()
    
    return timeseries

def plot_timeseries_and_histograms(timeseries):
    """
    Tworzy wykresy przebiegów czasowych i ich histogramów
    """
    
    n_series = len(timeseries)
    
    # Tworzenie subplotów - przebiegi czasowe
    fig1, axes1 = plt.subplots(n_series, 1, figsize=(12, 3*n_series))
    if n_series == 1:
        axes1 = [axes1]
    
    fig1.suptitle('Przebiegi czasowe z rozkładu normalnego', fontsize=16)
    
    for i, ts_data in enumerate(timeseries):
        time_axis = np.arange(len(ts_data['data']))
        axes1[i].plot(time_axis, ts_data['data'], alpha=0.7, linewidth=0.8)
        axes1[i].set_title(f"Przebieg czasowy: {ts_data['params']['label']}")
        axes1[i].set_xlabel('Czas [próbki]')
        axes1[i].set_ylabel('Amplituda')
        axes1[i].grid(True, alpha=0.3)
        axes1[i].axhline(y=ts_data['params']['mean'], color='red', 
                        linestyle='--', alpha=0.7, label=f"μ={ts_data['params']['mean']}")
        axes1[i].legend()
    
    plt.tight_layout()
    
    # Tworzenie histogramów
    fig2, axes2 = plt.subplots(2, 2, figsize=(12, 10))
    axes2 = axes2.flatten()
    
    fig2.suptitle('Histogramy przebiegów czasowych', fontsize=16)
    
    for i, ts_data in enumerate(timeseries):
        data = ts_data['data']
        params = ts_data['params']
        
        # Histogram
        n_bins = 50
        axes2[i].hist(data, bins=n_bins, density=True, alpha=0.7, 
                     color=f'C{i}', edgecolor='black', linewidth=0.5)
        
        # Teoretyczny rozkład normalny
        x_theory = np.linspace(np.min(data), np.max(data), 100)
        y_theory = (1/(params['std']*np.sqrt(2*np.pi))) * \
                   np.exp(-0.5*((x_theory-params['mean'])/params['std'])**2)
        axes2[i].plot(x_theory, y_theory, 'r-', linewidth=2, 
                     label='Teoretyczny rozkład normalny')
        
        axes2[i].set_title(f"Histogram: {params['label']}")
        axes2[i].set_xlabel('Wartość')
        axes2[i].set_ylabel('Gęstość prawdopodobieństwa')
        axes2[i].grid(True, alpha=0.3)
        axes2[i].legend()
        
        # Dodanie statystyk na wykres
        mean_actual = np.mean(data)
        std_actual = np.std(data)
        axes2[i].axvline(x=mean_actual, color='green', linestyle=':', 
                        label=f'Rzeczywista μ={mean_actual:.2f}')
    
    plt.tight_layout()
    plt.show()

def analyze_statistics(timeseries):
    """
    Analizuje statystyki przebiegów czasowych
    """
    
    print("="*60)
    print("ANALIZA STATYSTYCZNA PRZEBIEGÓW CZASOWYCH")
    print("="*60)
    
    for i, ts_data in enumerate(timeseries):
        data = ts_data['data']
        params = ts_data['params']
        
        print(f"\nPrzebieg {i+1}: {params['label']}")
        print("-" * 40)
        print(f"Parametry teoretyczne:")
        print(f"  Średnia (μ): {params['mean']}")
        print(f"  Odchylenie standardowe (σ): {params['std']}")
        print(f"  Liczba próbek: {params['size']}")
        
        print(f"\nStatystyki rzeczywiste:")
        print(f"  Średnia: {np.mean(data):.6f}")
        print(f"  Odchylenie standardowe: {np.std(data):.6f}")
        print(f"  Mediana: {np.median(data):.6f}")
        print(f"  Skośność: {calculate_skewness(data):.6f}")
        print(f"  Kurtoza: {calculate_kurtosis(data):.6f}")
        print(f"  Wartość minimalna: {np.min(data):.6f}")
        print(f"  Wartość maksymalna: {np.max(data):.6f}")
        
        # Percentyle
        percentiles = [5, 25, 50, 75, 95]
        print(f"  Percentyle: ", end="")
        for p in percentiles:
            print(f"{p}%={np.percentile(data, p):.3f} ", end="")
        print()

def calculate_skewness(data):
    """Oblicza skośność rozkładu"""
    mean = np.mean(data)
    std = np.std(data)
    n = len(data)
    return (n/((n-1)*(n-2))) * np.sum(((data - mean)/std)**3)

def calculate_kurtosis(data):
    """Oblicza kurtozę rozkładu"""
    mean = np.mean(data)
    std = np.std(data)
    n = len(data)
    return (n*(n+1)/((n-1)*(n-2)*(n-3))) * np.sum(((data - mean)/std)**4) - \
           (3*(n-1)**2/((n-2)*(n-3)))

def compare_distributions():
    """
    Porównuje różne rozkłady normalne na jednym wykresie
    """
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Różne średnie, stałe odchylenie standardowe
    means = [0, 2, -1]
    std = 1
    x = np.linspace(-5, 6, 1000)
    
    for mean in means:
        y = (1/(std*np.sqrt(2*np.pi))) * np.exp(-0.5*((x-mean)/std)**2)
        ax1.plot(x, y, label=f'μ={mean}, σ={std}', linewidth=2)
    
    ax1.set_title('Rozkłady normalne - różne średnie')
    ax1.set_xlabel('x')
    ax1.set_ylabel('Gęstość prawdopodobieństwa')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Stała średnia, różne odchylenia standardowe
    mean = 0
    stds = [0.5, 1, 2]
    x = np.linspace(-6, 6, 1000)
    
    for std in stds:
        y = (1/(std*np.sqrt(2*np.pi))) * np.exp(-0.5*((x-mean)/std)**2)
        ax2.plot(x, y, label=f'μ={mean}, σ={std}', linewidth=2)
    
    ax2.set_title('Rozkłady normalne - różne odchylenia standardowe')
    ax2.set_xlabel('x')
    ax2.set_ylabel('Gęstość prawdopodobieństwa')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    print("Generowanie przebiegów czasowych z rozkładu normalnego")
    print("="*60)
    
    # Generowanie przebiegów czasowych
    timeseries = generate_normal_timeseries()
    
    # Tworzenie wykresów
    plot_timeseries_and_histograms(timeseries)
    
    # Analiza statystyczna
    analyze_statistics(timeseries)
    
    # Porównanie różnych rozkładów
    print("\nPorównanie różnych rozkładów normalnych:")
    compare_distributions()
    
    print("\nAnalizę ukończono!")
