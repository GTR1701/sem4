import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, RadioButtons
import matplotlib.gridspec as gridspec
from scipy import stats

np.random.seed(42)


def generate_signal(dist_type, scale, offset, n_samples):
    if dist_type == 'rand (jednostajny)':
        return scale * np.random.rand(n_samples) + offset
    else:
        return scale * np.random.randn(n_samples) + offset


def interactive_random_signal():
    initial_dist = 'rand (jednostajny)'
    initial_scale = 1.0
    initial_offset = 0.0
    initial_n_samples = 1000
    initial_n_bins = 50

    fig = plt.figure(figsize=(14, 9))
    # bottom=0.30 zostawia miejsce na suwaki; right=0.72 na RadioButtons po prawej
    gs = gridspec.GridSpec(2, 2, figure=fig,
                           left=0.1, right=0.72, top=0.95, bottom=0.30,
                           height_ratios=[1, 1], hspace=0.48, wspace=0.35)

    ax_timeseries = fig.add_subplot(gs[0, :])
    ax_histogram = fig.add_subplot(gs[1, 0])
    ax_qqplot = fig.add_subplot(gs[1, 1])

    data = generate_signal(initial_dist, initial_scale, initial_offset, initial_n_samples)
    time_axis = np.arange(len(data))

    line, = ax_timeseries.plot(time_axis, data, alpha=0.7, linewidth=0.8, color='blue')
    ax_histogram.hist(data, bins=initial_n_bins, density=True,
                      alpha=0.7, color='skyblue', edgecolor='black', linewidth=0.5)
    stats.probplot(data, dist="norm", plot=ax_qqplot)

    ax_timeseries.set_title('Interaktywny przebieg czasowy sygnału losowego')
    ax_timeseries.set_xlabel('Próbka')
    ax_timeseries.set_ylabel('Amplituda')
    ax_timeseries.grid(True, alpha=0.3)

    ax_histogram.set_title('Histogram')
    ax_histogram.set_xlabel('Wartość')
    ax_histogram.set_ylabel('Gęstość prawdopodobieństwa')
    ax_histogram.grid(True, alpha=0.3)

    ax_qqplot.set_title('Q-Q plot (vs rozkład normalny)')
    ax_qqplot.grid(True, alpha=0.3)

    # Suwaki (poniżej bottom=0.30)
    slider_h = 0.03
    ax_scale_sl = plt.axes([0.1, 0.22, 0.55, slider_h])
    slider_scale = Slider(ax_scale_sl, 'Skala', 0.1, 5.0,
                          valinit=initial_scale, valstep=0.1)

    ax_offset_sl = plt.axes([0.1, 0.17, 0.55, slider_h])
    slider_offset = Slider(ax_offset_sl, 'Przesunięcie', -5.0, 5.0,
                           valinit=initial_offset, valstep=0.1)

    ax_samples_sl = plt.axes([0.1, 0.12, 0.55, slider_h])
    slider_samples = Slider(ax_samples_sl, 'Liczba próbek', 100, 5000,
                            valinit=initial_n_samples, valstep=100)

    ax_bins_sl = plt.axes([0.1, 0.07, 0.55, slider_h])
    slider_bins = Slider(ax_bins_sl, 'Liczba przedziałów', 5, 200,
                         valinit=initial_n_bins, valstep=5)

    # RadioButtons po prawej stronie (poza obszarem wykresów)
    ax_radio = plt.axes([0.75, 0.10, 0.2, 0.14])
    radio = RadioButtons(ax_radio, ('rand (jednostajny)', 'randn (normalny)'), active=0)

    # Box ze statystykami
    stats_text = plt.figtext(0.75, 0.27, '', fontsize=9,
                             bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray"))

    def update(val=None):
        dist_type = radio.value_selected
        scale = slider_scale.val
        offset = slider_offset.val
        n_samples = int(slider_samples.val)
        n_bins = int(slider_bins.val)

        new_data = generate_signal(dist_type, scale, offset, n_samples)

        line.set_data(np.arange(n_samples), new_data)
        ax_timeseries.set_xlim(0, n_samples)
        ax_timeseries.set_ylim(np.min(new_data) - 0.5, np.max(new_data) + 0.5)

        ax_histogram.clear()
        ax_histogram.hist(new_data, bins=n_bins, density=True, alpha=0.7,
                          color='skyblue', edgecolor='black', linewidth=0.5)
        ax_histogram.set_title('Histogram')
        ax_histogram.set_xlabel('Wartość')
        ax_histogram.set_ylabel('Gęstość prawdopodobieństwa')
        ax_histogram.grid(True, alpha=0.3)

        ax_qqplot.clear()
        stats.probplot(new_data, dist="norm", plot=ax_qqplot)
        ax_qqplot.set_title('Q-Q plot (vs rozkład normalny)')
        ax_qqplot.grid(True, alpha=0.3)

        stats_text.set_text(
            f"Statystyki:\n"
            f"Średnia:  {np.mean(new_data):.3f}\n"
            f"Odch. std: {np.std(new_data):.3f}\n"
            f"Min: {np.min(new_data):.3f}\n"
            f"Max: {np.max(new_data):.3f}\n"
            f"Próbki: {n_samples}"
        )

        fig.canvas.draw()

    slider_scale.on_changed(update)
    slider_offset.on_changed(update)
    slider_samples.on_changed(update)
    slider_bins.on_changed(update)
    radio.on_clicked(update)

    update()
    plt.show()


if __name__ == "__main__":
    print("Interaktywny generator sygnałów losowych (rand / randn)")
    print("="*60)
    print("Użyj suwaków i przycisków radiowych do zmiany parametrów:")
    print("  Skala        – mnoży wartości sygnału")
    print("  Przesunięcie – przesuwa sygnał wzdłuż osi Y")
    print("  Liczba próbek / przedziałów histogramu")
    print("="*60)
    interactive_random_signal()


# Parametry
n_samples = 1000  # liczba próbek
time = np.linspace(0, 10, n_samples)  # oś czasu od 0 do 10 sekund

# Generowanie przebiegów czasowych
# 1. Funkcja rand() - rozkład jednostajny [0, 1)
signal_rand = np.random.rand(n_samples)

# 2. Funkcja randn() - rozkład normalny (średnia=0, odchylenie=1)
signal_randn = np.random.randn(n_samples)

# 3. Dodatkowe przykłady - przebiegi czasowe z różnymi parametrami
signal_rand_scaled = 5 * np.random.rand(n_samples) - 2.5  # rozkład jednostajny [-2.5, 2.5]
signal_randn_scaled = 2 * np.random.randn(n_samples) + 1  # rozkład normalny (średnia=1, odchylenie=2)

print("Statystyki przebiegów czasowych:")
print(f"signal_rand: średnia={np.mean(signal_rand):.3f}, odchylenie={np.std(signal_rand):.3f}")
print(f"signal_randn: średnia={np.mean(signal_randn):.3f}, odchylenie={np.std(signal_randn):.3f}")
print(f"signal_rand_scaled: średnia={np.mean(signal_rand_scaled):.3f}, odchylenie={np.std(signal_rand_scaled):.3f}")
print(f"signal_randn_scaled: średnia={np.mean(signal_randn_scaled):.3f}, odchylenie={np.std(signal_randn_scaled):.3f}")

# Tworzenie wykresów
fig, axes = plt.subplots(3, 2, figsize=(15, 12))
fig.suptitle('Przebiegi czasowe i ich histogramy', fontsize=16)

# 1. Signal rand - przebieg czasowy
axes[0, 0].plot(time, signal_rand, 'b-', alpha=0.7, linewidth=0.8)
axes[0, 0].set_title('Przebieg czasowy - rand() [0,1)')
axes[0, 0].set_xlabel('Czas [s]')
axes[0, 0].set_ylabel('Amplituda')
axes[0, 0].grid(True, alpha=0.3)

# 1. Signal rand - histogram
axes[0, 1].hist(signal_rand, bins=50, alpha=0.7, color='blue', edgecolor='black')
axes[0, 1].set_title('Histogram - rand() [0,1)')
axes[0, 1].set_xlabel('Wartość')
axes[0, 1].set_ylabel('Liczba wystąpień')
axes[0, 1].grid(True, alpha=0.3)

# 2. Signal randn - przebieg czasowy
axes[1, 0].plot(time, signal_randn, 'r-', alpha=0.7, linewidth=0.8)
axes[1, 0].set_title('Przebieg czasowy - randn() N(0,1)')
axes[1, 0].set_xlabel('Czas [s]')
axes[1, 0].set_ylabel('Amplituda')
axes[1, 0].grid(True, alpha=0.3)

# 2. Signal randn - histogram
axes[1, 1].hist(signal_randn, bins=50, alpha=0.7, color='red', edgecolor='black')
axes[1, 1].set_title('Histogram - randn() N(0,1)')
axes[1, 1].set_xlabel('Wartość')
axes[1, 1].set_ylabel('Liczba wystąpień')
axes[1, 1].grid(True, alpha=0.3)

# 3. Porównanie przeskalowanych sygnałów
axes[2, 0].plot(time[:200], signal_rand_scaled[:200], 'g-', alpha=0.8, linewidth=1, label='Jednostajny [-2.5,2.5]')
axes[2, 0].plot(time[:200], signal_randn_scaled[:200], 'm-', alpha=0.8, linewidth=1, label='Normalny N(1,2)')
axes[2, 0].set_title('Porównanie przeskalowanych sygnałów (pierwsze 200 próbek)')
axes[2, 0].set_xlabel('Czas [s]')
axes[2, 0].set_ylabel('Amplituda')
axes[2, 0].legend()
axes[2, 0].grid(True, alpha=0.3)

# 3. Porównanie histogramów
axes[2, 1].hist(signal_rand_scaled, bins=50, alpha=0.5, color='green', edgecolor='black', label='Jednostajny [-2.5,2.5]')
axes[2, 1].hist(signal_randn_scaled, bins=50, alpha=0.5, color='magenta', edgecolor='black', label='Normalny N(1,2)')
axes[2, 1].set_title('Porównanie histogramów przeskalowanych sygnałów')
axes[2, 1].set_xlabel('Wartość')
axes[2, 1].set_ylabel('Liczba wystąpień')
axes[2, 1].legend()
axes[2, 1].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# Dodatkowa analiza statystyczna
print("\nDodatkowa analiza:")
print("="*50)

# Analiza rozkładu dla funkcji rand
print(f"Funkcja rand() - rozkład jednostajny [0,1):")
print(f"  Minimum: {np.min(signal_rand):.3f}")
print(f"  Maksimum: {np.max(signal_rand):.3f}")
print(f"  Mediana: {np.median(signal_rand):.3f}")
print(f"  Kwartyl 25%: {np.percentile(signal_rand, 25):.3f}")
print(f"  Kwartyl 75%: {np.percentile(signal_rand, 75):.3f}")

print(f"\nFunkcja randn() - rozkład normalny N(0,1):")
print(f"  Minimum: {np.min(signal_randn):.3f}")
print(f"  Maksimum: {np.max(signal_randn):.3f}")
print(f"  Mediana: {np.median(signal_randn):.3f}")
print(f"  Kwartyl 25%: {np.percentile(signal_randn, 25):.3f}")
print(f"  Kwartyl 75%: {np.percentile(signal_randn, 75):.3f}")

# Tworzenie oddzielnych wykresów dla bardziej szczegółowej analizy
fig2, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 8))
fig2.suptitle('Szczegółowa analiza histogramów', fontsize=14)

# Histogram rand() z krzywą gęstości teoretycznej
ax1.hist(signal_rand, bins=30, density=True, alpha=0.7, color='skyblue', edgecolor='black')
x_uniform = np.linspace(0, 1, 100)
y_uniform = np.ones_like(x_uniform)  # gęstość rozkładu jednostajnego
ax1.plot(x_uniform, y_uniform, 'r-', linewidth=2, label='Teoretyczna gęstość')
ax1.set_title('Histogram znormalizowany - rand()')
ax1.set_xlabel('Wartość')
ax1.set_ylabel('Gęstość')
ax1.legend()
ax1.grid(True, alpha=0.3)

# Histogram randn() z krzywą gęstości teoretycznej
ax2.hist(signal_randn, bins=30, density=True, alpha=0.7, color='lightcoral', edgecolor='black')
x_normal = np.linspace(-4, 4, 100)
y_normal = (1/np.sqrt(2*np.pi)) * np.exp(-0.5 * x_normal**2)  # gęstość rozkładu normalnego N(0,1)
ax2.plot(x_normal, y_normal, 'b-', linewidth=2, label='Teoretyczna gęstość N(0,1)')
ax2.set_title('Histogram znormalizowany - randn()')
ax2.set_xlabel('Wartość')
ax2.set_ylabel('Gęstość')
ax2.legend()
ax2.grid(True, alpha=0.3)

# Box plot dla porównania rozkładów
data_to_plot = [signal_rand, signal_randn]
ax3.boxplot(data_to_plot, labels=['rand()', 'randn()'])
ax3.set_title('Box plot - porównanie rozkładów')
ax3.set_ylabel('Wartość')
ax3.grid(True, alpha=0.3)

# Q-Q plot dla sprawdzenia normalności randn()
from scipy import stats
stats.probplot(signal_randn, dist="norm", plot=ax4)
ax4.set_title('Q-Q plot dla randn() vs rozkład normalny')
ax4.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

print(f"\nAnaliza zakończona. Wygenerowano {n_samples} próbek dla każdego sygnału.")
