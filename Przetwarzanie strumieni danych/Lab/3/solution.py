from scipy import signal
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, RadioButtons, Button
import pandas as pd
import os

#Zad 1

# Konfiguracja wykresu
plt.rcParams.update({
    'font.size': 15,
    'axes.titlesize': 14,
    'axes.labelsize': 13,
    'xtick.labelsize': 11,
    'ytick.labelsize': 11,
    'legend.fontsize': 12,
})

fig = plt.figure(figsize=(14, 8))
ax = fig.add_axes([0.06, 0.35, 0.30, 0.58])
ax_psd = fig.add_axes([0.40, 0.35, 0.30, 0.58])

def load_signal_from_file(signal_type):
    """Ładuje parametry sygnału z pliku CSV jeśli istnieje"""
    filename = f"{signal_type}_params.csv"
    current_dir = os.path.dirname(os.path.abspath(__file__))
    params_dir = os.path.join(current_dir, 'params')
    filepath = os.path.join(params_dir, filename)
    
    if os.path.exists(filepath):
        try:
            df = pd.read_csv(filepath)
            # Sprawdź czy plik zawiera parametry
            if 'Parametr' in df.columns and 'Wartość' in df.columns:
                params = {}
                for _, row in df.iterrows():
                    params[row['Parametr']] = row['Wartość']
                
                # Sprawdź czy wszystkie wymagane parametry są dostępne
                required_params = ['freq', 'amp', 'phase', 'tmax', 'impulse_pos']
                if all(param in params for param in required_params):
                    return {
                        'freq': max(0.1, min(10.0, float(params['freq']))),
                        'amp': max(0.1, min(3.0, float(params['amp']))),
                        'phase': max(0, min(2*np.pi, float(params['phase']))),
                        'tmax': max(1.0, min(20.0, float(params['tmax']))),
                        'impulse_pos': float(params['impulse_pos'])
                    }
        except Exception as e:
            print(f"Błąd podczas ładowania pliku {filename}: {e}")
    
    return None

# Parametry początkowe - próbuj załadować z pliku, jeśli nie ma - użyj domyślnych
initial_signal_type = 'sinus'
loaded_params = load_signal_from_file(initial_signal_type)

if loaded_params:
    initial_freq = loaded_params['freq']
    initial_amp = loaded_params['amp']
    initial_phase = loaded_params['phase']
    initial_tmax = loaded_params['tmax']
    initial_impulse_position = loaded_params['impulse_pos']
    print(f"Załadowano parametry początkowe dla sygnału: {initial_signal_type}")
else:
    # Parametry domyślne
    initial_freq = 1.0
    initial_amp = 1.0
    initial_phase = 0.0
    initial_tmax = 5.0
    initial_impulse_position = 2.5  # Pozycja impulsu jednostkowego

initial_samples = 1000  # Liczba sampli

# Oś czasu
t = np.linspace(0, initial_tmax, initial_samples)

def psd_definition(x, fs):
    """WGM z definicji:
       S_XX(f) = int_{-inf}^{inf} R_XX(tau) * e^{-j2pi*f*tau} dtau
    Numerycznie:
       S_XX(f) ≈ dt * sum_k R_XX[k] * e^{-j2pi * f * tau_k}
    """
    n = len(x)
    dt = 1.0 / fs

    # 1. Autokorelacja R_XX[k] dla opóźnień k = -(n-1)...(n-1)
    rxx = np.correlate(x, x, mode='full') / n
    lags = np.arange(-(n - 1), n)
    taus = lags * dt  # opóźnienia w sekundach

    # 2. Jednostronna oś częstotliwości: 0 ... fs/2
    n_freqs = n // 2 + 1
    freqs = np.linspace(0, fs / 2, n_freqs)

    # 3. Ręczne całkowanie: macierz faz (n_freqs x 2n-1), bez FFT
    #    kernel[i, k] = e^{-j2pi * freqs[i] * taus[k]}
    kernel = np.exp(-1j * 2 * np.pi * np.outer(freqs, taus))

    # 4. Całka jako suma Riemanna: S(f) = dt * sum_k R[k] * kernel[f, k]
    S = dt * (kernel @ rxx)

    # 5. Bierzemy część rzeczywistą (R_XX symetryczna → S_XX rzeczywiste)
    psd = np.real(S)

    # 6. Podwojenie składowych jednostronnych (zachowanie energii), poza DC
    psd[1:] *= 2
    psd = np.abs(psd)

    return freqs, psd

# Funkcja do generowania sygnału
def generate_signal(t, signal_type, freq, amp, phase, impulse_pos=None):
    if signal_type == 'sinus':
        return amp * np.sin(2 * np.pi * freq * t + phase)
    elif signal_type == 'cosinus':
        return amp * np.cos(2 * np.pi * freq * t + phase)
    elif signal_type == 'prostokątny':
        return amp * signal.square(2 * np.pi * freq * t + phase)
    elif signal_type == 'piłokształtny':
        return amp * signal.sawtooth(2 * np.pi * freq * t + phase)
    elif signal_type == 'trójkątny':
        return amp * signal.sawtooth(2 * np.pi * freq * t + phase, width=0.5)
    elif signal_type == 'szum biały':
        np.random.seed(42)  # Dla powtarzalności
        return amp * np.random.normal(0, 1, len(t))
    elif signal_type == 'chirp':
        return amp * signal.chirp(t, f0=freq, f1=freq*10, t1=t[-1], method='linear')
    elif signal_type == 'superpozycja':
        sin_part = amp * np.sin(2 * np.pi * freq * t + phase)
        cos_part = amp * np.cos(2 * np.pi * freq * 1.5 * t + phase)
        return sin_part + cos_part
    elif signal_type == 'impuls jednostkowy':
        # Impuls jednostkowy - wartość amp w pozycji impulse_pos, 0 wszędzie indziej
        impulse_signal = np.zeros_like(t)
        if impulse_pos is not None:
            # Znajdź najbliższy punkt w czasie do pozycji impulsu
            closest_idx = np.argmin(np.abs(t - impulse_pos))
            impulse_signal[closest_idx] = amp
        return impulse_signal
    elif signal_type == 'szum browna':
        np.random.seed(42)
        white = np.random.normal(0, 1, len(t))
        brown = np.cumsum(white)
        brown -= brown.mean()
        return amp * brown / (np.std(brown) + 1e-12)
    elif signal_type == 'szum fioletowy':
        np.random.seed(42)
        white = np.random.normal(0, 1, len(t))
        violet = np.diff(white, prepend=white[0])
        violet -= violet.mean()
        return amp * violet / (np.std(violet) + 1e-12)

def save_signal_parameters():
    """Zapisuje parametry z suwaków do pliku CSV"""
    # Pobierz aktualne parametry z sliderów
    freq = slider_freq.val
    amp = slider_amp.val  
    phase = slider_phase.val
    tmax = slider_tmax.val
    impulse_pos = slider_impulse_pos.val
    signal_type = radio.value_selected
    
    # Przygotuj dane parametrów do zapisu
    data = {
        'Parametr': ['freq', 'amp', 'phase', 'tmax', 'impulse_pos'],
        'Wartość': [freq, amp, phase, tmax, impulse_pos]
    }
    
    # Utwórz nazwę pliku tylko z nazwą sygnału (bez timestamp)
    filename = f"{signal_type}_params.csv"
    
    # Utwórz folder params jeśli nie istnieje
    current_dir = os.path.dirname(os.path.abspath(__file__))
    params_dir = os.path.join(current_dir, 'params')
    os.makedirs(params_dir, exist_ok=True)
    
    # Zapisz do pliku (nadpisz jeśli istnieje)
    df = pd.DataFrame(data)
    filepath = os.path.join(params_dir, filename)
    df.to_csv(filepath, index=False)
    
    print(f"Zapisano parametry sygnału do pliku: params/{filename}")
    return filename

def save_signal_data():
    """Zapisuje dane sygnału do pliku CSV"""
    # Pobierz aktualne parametry z sliderów
    freq = slider_freq.val
    amp = slider_amp.val  
    phase = slider_phase.val
    tmax = slider_tmax.val
    impulse_pos = slider_impulse_pos.val
    signal_type = radio.value_selected
    
    # Wygeneruj aktualny sygnał
    samples = int(slider_samples.val)
    t_current = np.linspace(0, tmax, samples)
    if signal_type == 'impuls jednostkowy':
        y_current = generate_signal(t_current, signal_type, freq, amp, phase, impulse_pos)
    else:
        y_current = generate_signal(t_current, signal_type, freq, amp, phase)
    
    # Przygotuj dane sygnału do zapisu
    data = {
        'Czas': t_current,
        'Amplituda': y_current
    }
    
    # Utwórz nazwę pliku z danymi sygnału
    filename = f"{signal_type}_data.csv"
    
    # Utwórz folder data jeśli nie istnieje
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    # Zapisz do pliku (nadpisz jeśli istnieje)
    df = pd.DataFrame(data)
    filepath = os.path.join(data_dir, filename)
    df.to_csv(filepath, index=False)
    
    print(f"Zapisano dane sygnału do pliku: data/{filename}")
    return filename

def save_all():
    """Zapisuje zarówno parametry jak i dane sygnału"""
    print("Zapisywanie...")
    params_file = save_signal_parameters()
    data_file = save_signal_data()
    print(f"Zakończono zapisywanie dla sygnału: {radio.value_selected}")
    return params_file, data_file

# Początkowy wykres
y = generate_signal(t, initial_signal_type, initial_freq, initial_amp, initial_phase, initial_impulse_position)
line, = ax.plot(t, y, 'b-', linewidth=2)
ax.set_xlim(0, initial_tmax)
ax.set_ylim(-3, 3)
ax.set_xlabel('Czas [s]')
ax.set_ylabel('Amplituda')
ax.set_title(f'Interaktywny wykres sygnału: {initial_signal_type}')
ax.grid(True, alpha=0.3)

# Inicjalizacja wykresu PSD
initial_fs = initial_samples / initial_tmax
initial_freqs, initial_psd = signal.periodogram(y, initial_fs)
psd_line, = ax_psd.plot(initial_freqs, initial_psd, 'r-', linewidth=1.5)
ax_psd.set_xlabel('Częstotliwość [Hz]')
ax_psd.set_ylabel('PSD [V²/Hz]')
ax_psd.set_title('Gęstość mocy widmowej (periodogram)')
ax_psd.grid(True, alpha=0.3)

# --- Panel sygnału: slidery ---
ax_freq = plt.axes([0.15, 0.25, 0.50, 0.03])
slider_freq = Slider(ax_freq, 'Częstotliwość', 0.1, 10.0, valinit=initial_freq, valstep=0.1)

ax_amp = plt.axes([0.15, 0.20, 0.50, 0.03])
slider_amp = Slider(ax_amp, 'Amplituda', 0.1, 3.0, valinit=initial_amp, valstep=0.1)

ax_phase = plt.axes([0.15, 0.15, 0.50, 0.03])
slider_phase = Slider(ax_phase, 'Faza', 0, 2*np.pi, valinit=initial_phase, valstep=0.1)

ax_tmax = plt.axes([0.15, 0.10, 0.50, 0.03])
slider_tmax = Slider(ax_tmax, 'Zakres czasu', 1.0, 20.0, valinit=initial_tmax, valstep=0.5)

ax_impulse_pos = plt.axes([0.15, 0.05, 0.50, 0.03])
slider_impulse_pos = Slider(ax_impulse_pos, 'Pozycja impulsu', 0.0, initial_tmax, valinit=initial_impulse_position, valstep=0.1)

ax_samples = plt.axes([0.15, 0.00, 0.50, 0.03])
slider_samples = Slider(ax_samples, 'Liczba sampli', 100, 5000, valinit=initial_samples, valstep=100)

# --- Panel sygnału: typ sygnału ---
ax_radio = plt.axes([0.74, 0.02, 0.21, 0.25])
radio = RadioButtons(ax_radio, ('sinus', 'cosinus', 'prostokątny', 'piłokształtny', 'chirp', 'superpozycja', 'impuls jednostkowy', 'trójkątny', 'szum biały', 'szum browna', 'szum fioletowy'))

# --- Panel widma (domyślnie ukryty) ---
ax_psd_method = plt.axes([0.10, 0.13, 0.28, 0.12])
ax_psd_method.set_title('Metoda PSD', fontsize=9)
radio_psd = RadioButtons(ax_psd_method, ('periodogram', 'welch', 'definicja'))
ax_psd_method.set_visible(False)

ax_psd_scale = plt.axes([0.43, 0.13, 0.24, 0.12])
ax_psd_scale.set_title('Skala osi Y', fontsize=9)
radio_psd_scale = RadioButtons(ax_psd_scale, ('liniowa', 'logarytmiczna'))
ax_psd_scale.set_visible(False)

# --- Przyciski przełączające panele ---
ax_tab_signal = plt.axes([0.74, 0.29, 0.10, 0.04])
btn_tab_signal = Button(ax_tab_signal, 'Sygnał', color='lightblue', hovercolor='deepskyblue')

ax_tab_spectral = plt.axes([0.85, 0.29, 0.10, 0.04])
btn_tab_spectral = Button(ax_tab_spectral, 'Widmo', color='lightgray', hovercolor='silver')

# --- Przycisk zapisywania (zawsze widoczny) ---
ax_save_button = plt.axes([0.74, 0.38, 0.10, 0.04])
save_button = Button(ax_save_button, 'Zapisz')

_signal_panel_axes = [ax_freq, ax_amp, ax_phase, ax_tmax, ax_impulse_pos, ax_samples, ax_radio]
_spectral_panel_axes = [ax_psd_method, ax_psd_scale]

# Zapamiętaj oryginalne pozycje (przed jakimkolwiek przesunięciem)
_offscreen = [-2.0, -2.0, 0.01, 0.01]
_signal_positions = {a: list(a.get_position().bounds) for a in _signal_panel_axes}
_spectral_positions = {a: list(a.get_position().bounds) for a in _spectral_panel_axes}

def _apply_panel(show_list, show_pos, hide_list):
    for a in show_list:
        a.set_position(show_pos[a])
        a.set_visible(True)
    for a in hide_list:
        a.set_position(_offscreen)
        a.set_visible(False)

def show_signal_panel(event=None):
    _apply_panel(_signal_panel_axes, _signal_positions, _spectral_panel_axes)
    btn_tab_signal.color = 'lightblue'
    btn_tab_signal.ax.set_facecolor('lightblue')
    btn_tab_spectral.color = 'lightgray'
    btn_tab_spectral.ax.set_facecolor('lightgray')
    fig.canvas.draw_idle()

def show_spectral_panel(event=None):
    _apply_panel(_spectral_panel_axes, _spectral_positions, _signal_panel_axes)
    btn_tab_spectral.color = 'lightblue'
    btn_tab_spectral.ax.set_facecolor('lightblue')
    btn_tab_signal.color = 'lightgray'
    btn_tab_signal.ax.set_facecolor('lightgray')
    fig.canvas.draw_idle()

# Funkcja do ładowania parametrów przy zmianie typu sygnału
def on_signal_type_change(label):
    loaded_params = load_signal_from_file(label)
    if loaded_params:
        slider_freq.set_val(loaded_params['freq'])
        slider_amp.set_val(loaded_params['amp'])
        slider_phase.set_val(loaded_params['phase'])
        slider_tmax.set_val(loaded_params['tmax'])
        slider_impulse_pos.set_val(loaded_params['impulse_pos'])
        print(f"Załadowano parametry dla sygnału: {label}")
    else:
        print(f"Brak zapisanego pliku dla sygnału: {label}, używam bieżących parametrów")
    update(None)

# Funkcja update
def update(val):
    freq = slider_freq.val
    amp = slider_amp.val
    phase = slider_phase.val
    tmax = slider_tmax.val
    impulse_pos = slider_impulse_pos.val
    signal_type = radio.value_selected

    slider_impulse_pos.valmax = tmax
    if impulse_pos > tmax:
        slider_impulse_pos.set_val(tmax)
        impulse_pos = tmax

    samples = int(slider_samples.val)
    t_new = np.linspace(0, tmax, samples)
    y_new = generate_signal(t_new, signal_type, freq, amp, phase, impulse_pos)

    line.set_data(t_new, y_new)
    ax.set_xlim(0, tmax)
    if signal_type == 'impuls jednostkowy':
        ax.set_ylim(-0.1 * amp, amp * 1.2)
    else:
        ax.set_ylim(-amp * 2.5, amp * 2.5)
    ax.set_title(f'Wykres sygnału: {signal_type}')

    psd_method = radio_psd.value_selected
    psd_scale = radio_psd_scale.value_selected
    fs_current = samples / tmax
    if psd_method == 'periodogram':
        freqs, psd = signal.periodogram(y_new, fs_current)
    elif psd_method == 'welch':
        freqs, psd = signal.welch(y_new, fs_current)
    else:
        freqs, psd = psd_definition(y_new, fs_current)

    psd_line.set_data(freqs, psd)
    ax_psd.set_xlim(0, freqs[-1] if len(freqs) > 0 else 1)
    psd_max = np.max(psd) if len(psd) > 0 and np.max(psd) > 0 else 1

    if psd_scale == 'logarytmiczna':
        ax_psd.set_yscale('log')
        ax_psd.set_ylim(max(psd_max * 1e-6, 1e-12), psd_max * 10)
    else:
        ax_psd.set_yscale('linear')
        ax_psd.set_ylim(0, psd_max * 1.1)

    ax_psd.set_title(f'Gęstość mocy widmowej ({psd_method})')
    fig.canvas.draw_idle()

slider_freq.on_changed(update)
slider_amp.on_changed(update)
slider_phase.on_changed(update)
slider_tmax.on_changed(update)
slider_impulse_pos.on_changed(update)
slider_samples.on_changed(update)

radio.on_clicked(on_signal_type_change)
radio_psd.on_clicked(update)
radio_psd_scale.on_clicked(update)

save_button.on_clicked(save_all)
btn_tab_signal.on_clicked(show_signal_panel)
btn_tab_spectral.on_clicked(show_spectral_panel)

# Inicjalizacja: pokaż panel sygnału, ukryj panel widma
show_signal_panel()

fig.canvas.manager.set_window_title('Interaktywny generator sygnałów')
plt.show()
