import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import matplotlib.gridspec as gridspec

def interactive_normal_timeseries():
    """
    Tworzy interaktywny wykres przebiegu czasowego z rozkładu normalnego
    z suwakami do zmiany parametrów w czasie rzeczywistym
    """
    
    # Zwiększenie rozmiaru czcionki
    plt.rcParams.update({'font.size': 13})

    # Parametry początkowe
    initial_mean = 0.0
    initial_std = 1.0
    initial_size = 1000
    
    # Ustawienie seed dla powtarzalności
    np.random.seed(42)
    
    # Tworzenie layoutu z GridSpec
    fig = plt.figure(figsize=(14, 10))
    gs = gridspec.GridSpec(2, 2, figure=fig,
                           left=0.1, right=0.95, top=0.95, bottom=0.46,
                           height_ratios=[1, 1], hspace=0.48, wspace=0.35)
    
    # Główne wykresy
    ax_timeseries = fig.add_subplot(gs[0, :])
    ax_histogram = fig.add_subplot(gs[1, 0])
    ax_pdf = fig.add_subplot(gs[1, 1])
    
    # Generowanie początkowych danych
    data = np.random.normal(initial_mean, initial_std, initial_size)
    time_axis = np.arange(len(data))
    
    # Początkowe wykresy
    line_timeseries, = ax_timeseries.plot(time_axis, data, alpha=0.7, linewidth=0.8, color='blue')
    mean_line = ax_timeseries.axhline(y=initial_mean, color='red', linestyle='--', alpha=0.7)
    
    # Histogram
    n_bins = 50
    n, bins, patches = ax_histogram.hist(data, bins=n_bins, density=True, alpha=0.7, 
                                        color='skyblue', edgecolor='black', linewidth=0.5)
    
    # Teoretyczny rozkład normalny
    x_theory = np.linspace(np.min(data), np.max(data), 200)
    y_theory = (1/(initial_std*np.sqrt(2*np.pi))) * \
               np.exp(-0.5*((x_theory-initial_mean)/initial_std)**2)
    line_pdf, = ax_pdf.plot(x_theory, y_theory, 'r-', linewidth=2, label='Teoretyczny PDF')
    
    # Ustawienia wykresów
    ax_timeseries.set_title('Interaktywny przebieg czasowy z rozkładu normalnego')
    ax_timeseries.set_xlabel('Czas [próbki]')
    ax_timeseries.set_ylabel('Amplituda')
    ax_timeseries.grid(True, alpha=0.3)
    
    ax_histogram.set_title('Histogram danych')
    ax_histogram.set_xlabel('Wartość')
    ax_histogram.set_ylabel('Gęstość prawdopodobieństwa')
    ax_histogram.grid(True, alpha=0.3)
    
    ax_pdf.set_title('Funkcja gęstości prawdopodobieństwa')
    ax_pdf.set_xlabel('Wartość')
    ax_pdf.set_ylabel('Gęstość prawdopodobieństwa')
    ax_pdf.grid(True, alpha=0.3)
    ax_pdf.legend()
    
    # Tworzenie suwaków – ułożone jeden pod drugim (lewa/środkowa część)
    slider_height = 0.03
    slider_left = 0.25
    slider_width = 0.54

    # Suwak dla średniej (górny)
    ax_mean_slider = plt.axes([slider_left, 0.36, slider_width, slider_height])
    slider_mean = Slider(ax_mean_slider, 'Średnia (μ)', -5.0, 5.0,
                        valinit=initial_mean, valstep=0.1)

    # Suwak dla odchylenia standardowego (środkowy)
    ax_std_slider = plt.axes([slider_left, 0.27, slider_width, slider_height])
    slider_std = Slider(ax_std_slider, 'Odchylenie standardowe (σ)', 0.1, 5.0,
                       valinit=initial_std, valstep=0.1)

    # Suwak dla liczby próbek (dolny)
    ax_size_slider = plt.axes([slider_left, 0.18, slider_width, slider_height])
    slider_size = Slider(ax_size_slider, 'Liczba próbek', 100, 5000,
                        valinit=initial_size, valstep=100)

    # Text box dla statystyk – po prawej stronie, obok suwaków
    stats_text = plt.figtext(0.45, 0.03, '', fontsize=12,
                           verticalalignment='bottom',
                           bbox=dict(boxstyle="round,pad=0.4", facecolor="lightgray"))
    
    def update_plots(val=None):
        """Aktualizuje wszystkie wykresy po zmianie parametrów"""
        
        # Pobieranie aktualnych wartości z suwaków
        mean = slider_mean.val
        std = slider_std.val
        size = int(slider_size.val)
        
        # Generowanie nowych danych
        new_data = np.random.normal(mean, std, size)
        new_time_axis = np.arange(len(new_data))
        
        # Aktualizacja przebiegu czasowego
        line_timeseries.set_data(new_time_axis, new_data)
        ax_timeseries.set_xlim(0, len(new_data))
        ax_timeseries.set_ylim(np.min(new_data) - 0.5*std, np.max(new_data) + 0.5*std)
        mean_line.set_ydata([mean, mean])
        
        # Aktualizacja histogramu
        ax_histogram.clear()
        ax_histogram.hist(new_data, bins=n_bins, density=True, alpha=0.7, 
                         color='skyblue', edgecolor='black', linewidth=0.5)
        ax_histogram.set_title('Histogram danych')
        ax_histogram.set_xlabel('Wartość')
        ax_histogram.set_ylabel('Gęstość prawdopodobieństwa')
        ax_histogram.grid(True, alpha=0.3)
        
        # Aktualizacja PDF
        x_theory_new = np.linspace(np.min(new_data), np.max(new_data), 200)
        y_theory_new = (1/(std*np.sqrt(2*np.pi))) * \
                       np.exp(-0.5*((x_theory_new-mean)/std)**2)
        line_pdf.set_data(x_theory_new, y_theory_new)
        ax_pdf.set_xlim(np.min(new_data) - std, np.max(new_data) + std)
        ax_pdf.set_ylim(0, np.max(y_theory_new) * 1.1)
        
        # Aktualizacja statystyk
        actual_mean = np.mean(new_data)
        actual_std = np.std(new_data)
        actual_min = np.min(new_data)
        actual_max = np.max(new_data)
        
        stats_str = f"""Statystyki rzeczywiste:
Średnia: {actual_mean:.3f}
Odch. std: {actual_std:.3f}
Min: {actual_min:.3f}
Max: {actual_max:.3f}
Liczba próbek: {size}"""
        
        stats_text.set_text(stats_str)
        
        # Odświeżenie wykresu
        fig.canvas.draw()
    
    # Podłączenie funkcji update do suwaków
    slider_mean.on_changed(update_plots)
    slider_std.on_changed(update_plots)
    slider_size.on_changed(update_plots)

    # Początkowa aktualizacja statystyk
    update_plots()

    fig.canvas.manager.set_window_title('Rozkład normalny – interaktywny przebieg czasowy')
    plt.show()

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
    fig.canvas.manager.set_window_title('Rozkłady normalne – porównanie')
    plt.show()

if __name__ == "__main__":
    print("Generowanie przebiegów czasowych z rozkładu normalnego")
    print("="*60)
    
    interactive_normal_timeseries()
