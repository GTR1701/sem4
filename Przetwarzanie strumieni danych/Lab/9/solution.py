from scipy import signal
import scipy.fft as sp_fft
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, RadioButtons, Button, CheckButtons
import pandas as pd
import os
import tkinter as tk
import tkinter.font as tk_font
from tkinter import filedialog as tk_filedialog
import pywt
import warnings
import emd

# Konfiguracja wykresu
plt.rcParams.update({
    'font.size': 15,
    'axes.titlesize': 14,
    'axes.labelsize': 15,
    'xtick.labelsize': 15,
    'ytick.labelsize': 15,
    'legend.fontsize': 15,
})

fig = plt.figure(figsize=(14, 8))
ax = fig.add_axes([0.05, 0.38, 0.33, 0.57])
ax_psd = fig.add_axes([0.41, 0.38, 0.33, 0.57])

# --- Osie wyświetlania dekompozycji chirp (domyślnie ukryte) ---
# Pas 1 (góra):   sygnał          y = 0.87..0.97
# Pas 2 (skalogramy): y = 0.43..0.84
# Pas 3 (slidery):    y = 0.28..0.39  (3 × suwak)
# Pas 4 (radio):      y = 0.01..0.23
ax_dc_sig = fig.add_axes([0.05,  0.87, 0.69, 0.10])
ax_dc_1   = fig.add_axes([0.05,  0.43, 0.215, 0.41])
ax_dc_2   = fig.add_axes([0.283, 0.43, 0.215, 0.41])
ax_dc_3   = fig.add_axes([0.516, 0.43, 0.215, 0.41])
for _a in (ax_dc_sig, ax_dc_1, ax_dc_2, ax_dc_3):
    _a.set_visible(False)

# --- Osie wyświetlania spektrogramu (domyślnie ukryte) ---
ax_spec_sig = fig.add_axes([0.05, 0.87, 0.69, 0.10])
ax_spec     = fig.add_axes([0.05, 0.43, 0.64, 0.41])
ax_spec_cb  = fig.add_axes([0.705, 0.43, 0.018, 0.41])   # stałe miejsce dla colorbar
for _a in (ax_spec_sig, ax_spec, ax_spec_cb):
    _a.set_visible(False)

# --- Osie wyświetlania miar jakości sygnału (domyślnie ukryte) ---
ax_qual_orig    = fig.add_axes([0.05,  0.38, 0.33,  0.57])  # oryginalny + zaszumiony
ax_qual_diff    = fig.add_axes([0.42,  0.38, 0.33,  0.57])  # szum / błąd
ax_qual_metrics = fig.add_axes([0.05,  0.30, 0.66,  0.04])  # miary SNR/PSNR/MSE
for _a in (ax_qual_orig, ax_qual_diff, ax_qual_metrics):
    _a.set_visible(False)

# --- Osie wyświetlania odszumiania (domyślnie ukryte) ---
ax_den_noisy   = fig.add_axes([0.05, 0.42, 0.33, 0.53])  # oryginalny + zaszumiony
ax_den_clean   = fig.add_axes([0.41, 0.42, 0.33, 0.53])  # odszumiony
ax_den_metrics = fig.add_axes([0.05, 0.37, 0.66, 0.04])  # metryki SNR/MSE wejście→wyjście
for _a in (ax_den_noisy, ax_den_clean, ax_den_metrics):
    _a.set_visible(False)

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

    # 3. Ręczne całkowanie: macierz faz (n_freqs x 2n-1)
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

_current_tab = 'signal'

# Stan załadowanego sygnału z pliku CSV
_loaded_signal = {'t': None, 'y': None, 'label': None}


def _pick_time_amp_columns(df):
    """Heurystycznie wybiera kolumny czasu i amplitudy z DataFrame."""
    cols = list(df.columns)
    time_keywords = ['czas', 'time', 't', 'x', 'sample', 'n', 'index']
    amp_keywords = ['amplituda', 'amplitude', 'y', 'value', 'signal', 'data', 'a', 'v']
    t_col = None
    y_col = None
    for kw in time_keywords:
        for c in cols:
            if kw in c.lower():
                t_col = c
                break
        if t_col:
            break
    for kw in amp_keywords:
        for c in cols:
            if kw in c.lower() and c != t_col:
                y_col = c
                break
        if y_col:
            break
    if t_col is None and len(cols) >= 1:
        t_col = cols[0]
    if y_col is None and len(cols) >= 2:
        y_col = cols[1]
    elif y_col is None and len(cols) == 1:
        y_col = cols[0]
        t_col = None
    return t_col, y_col


def _plot_loaded_spectrum():
    """Rysuje sygnał z pliku (lewy wykres) oraz jego widmo FFT (prawy wykres)."""
    global line, line_env_pos, line_env_neg
    t_data = _loaded_signal['t']
    y_data = _loaded_signal['y']
    label = _loaded_signal['label']
    if y_data is None:
        return

    # Lewy wykres: przebieg sygnału
    ax.cla()
    ax.grid(True, alpha=0.3)
    ax.plot(t_data, y_data, 'b-', linewidth=1.5)
    ax.set_xlabel('Czas [s]' if (t_data[-1] - t_data[0]) < len(t_data) else 'Próbka')
    ax.set_ylabel('Amplituda')
    ax.set_title(f'Sygnał z pliku: {label}')
    # Odtwórz obiekty line żeby update() nie crashował po powrocie do zakładki Sygnał
    line, = ax.plot([], [], visible=False)
    line_env_pos, = ax.plot([], [], visible=False)
    line_env_neg, = ax.plot([], [], visible=False)

    # Prawy wykres: jednostronne widmo amplitudowe FFT (scipy.fft)
    N = len(y_data)
    dt = float(t_data[1] - t_data[0]) if len(t_data) > 1 else 1.0
    fs_csv = 1.0 / dt if dt > 0 else float(N)
    X = sp_fft.rfft(y_data)
    freqs = sp_fft.rfftfreq(N, d=dt)
    amplitude = np.abs(X) * 2.0 / N
    amplitude[0] /= 2.0
    if N % 2 == 0:
        amplitude[-1] /= 2.0
    ax_psd.cla()
    ax_psd.grid(True, alpha=0.3)
    if len(freqs) > 400:
        ax_psd.plot(freqs, amplitude, 'g-', linewidth=1.5)
    else:
        ax_psd.vlines(freqs, 0, amplitude, colors='g', linewidth=1.2)
        ax_psd.plot(freqs, amplitude, 'go', markersize=4)
    ax_psd.set_xlabel('Częstotliwość [Hz]')
    ax_psd.set_ylabel('Amplituda')
    ax_psd.set_xlim(0, fs_csv / 2)
    a_max = float(np.max(amplitude)) if np.max(amplitude) > 0 else 1.0
    ax_psd.set_ylim(0, a_max * 1.15)
    ax_psd.set_title(f'Widmo amplitudowe — scipy.fft | N={N} | fs≈{fs_csv:.1f} Hz')
    fig.canvas.draw_idle()


def load_csv_signal(event=None):
    """Otwiera dialog wyboru pliku CSV i rysuje sygnał + widmo."""
    root = tk.Tk()
    # Skalowanie musi być ustawione PRZED withdraw() i dialogiem
    root.tk.call('tk', 'scaling', 2.0)
    # Powiększ wszystkie named fonts (jedyna metoda działająca na Linuksie)
    _DIALOG_FONT_SIZE = 14
    for fname in ('TkDefaultFont', 'TkTextFont', 'TkFixedFont',
                  'TkMenuFont', 'TkHeadingFont', 'TkCaptionFont',
                  'TkSmallCaptionFont', 'TkIconFont', 'TkTooltipFont'):
        try:
            tk_font.nametofont(fname).configure(size=_DIALOG_FONT_SIZE)
        except Exception:
            pass
    root.withdraw()
    root.attributes('-topmost', True)
    filepath = tk_filedialog.askopenfilename(
        title='Wybierz plik CSV z sygnałem',
        filetypes=[('CSV files', '*.csv'), ('Text files', '*.txt *.tsv'), ('All files', '*.*')]
    )
    root.destroy()
    if not filepath:
        return
    try:
        df = None
        for sep in (',', ';', '\t', ' '):
            try:
                tmp = pd.read_csv(filepath, sep=sep)
                if tmp.shape[1] >= 1:
                    df = tmp
                    break
            except Exception:
                continue
        if df is None:
            print(f'[Załaduj CSV] Nie udało się wczytać pliku: {filepath}')
            return
        df = df.apply(pd.to_numeric, errors='coerce').dropna()
        if df.empty:
            print(f'[Załaduj CSV] Plik {filepath} nie zawiera danych numerycznych.')
            return
        t_col, y_col = _pick_time_amp_columns(df)
        y_data = df[y_col].to_numpy(dtype=float)
        if t_col and t_col != y_col:
            t_data = df[t_col].to_numpy(dtype=float)
        else:
            t_data = np.arange(len(y_data), dtype=float)
        if len(y_data) < 4:
            print('[Załaduj CSV] Za mało próbek (minimum 4).')
            return
        _loaded_signal['t'] = t_data
        _loaded_signal['y'] = y_data
        _loaded_signal['label'] = os.path.basename(filepath)
        print(f'[Załaduj CSV] Załadowano {len(y_data)} próbek z: {filepath}')
        print(f'             Kolumna czasu: {t_col}, kolumna amplitudy: {y_col}')
        _plot_loaded_spectrum()
        # Jeśli dekompozycja ma aktywne źródło 'z pliku CSV', odśwież wykres
        if _current_tab == 'decomp' and radio_dc_source.value_selected == 'z pliku CSV':
            update_decomp_plot()
        if _current_tab == 'quality' and radio_qual_source.value_selected == 'z pliku CSV':
            update_quality_plot()
    except Exception as e:
        print(f'[Załaduj CSV] Błąd wczytywania pliku: {e}')


def quantize(y, bits, amp):
    """Kwantyzacja sygnału do zadanej liczby bitów."""
    n_levels = 2 ** bits
    amp_safe = max(float(amp), 1e-12)
    step = 2.0 * amp_safe / n_levels
    y_clipped = np.clip(y, -amp_safe, amp_safe)
    return np.round(y_clipped / step) * step


def interpolate_piecewise(t_out, t_s, y_s):
    """Odcinkami liniowa interpolacja za pomocą np.piecewise.

    Dla każdego przedziału [t_s[i], t_s[i+1]) wyznacza linię prostą
    przechodzącą przez (t_s[i], y_s[i]) i (t_s[i+1], y_s[i+1]),
    a następnie skleja je funkcją np.piecewise.
    """
    t_out = np.asarray(t_out, dtype=float)
    n = len(t_s)
    if n < 2:
        return np.full_like(t_out, y_s[0] if n == 1 else 0.0)

    # Warunki: punkt należy do i-tego przedziału
    conditions = [
        (t_out >= t_s[i]) & (t_out < t_s[i + 1])
        for i in range(n - 1)
    ]
    # Ostatni punkt dokładnie (t_s[-1])
    conditions.append(t_out >= t_s[-1])

    # Funkcje liniowe dla każdego przedziału; domyślna (poza zakresem) = 0
    functions = [0.0]  # wartość poza zdefiniowanymi przedziałami
    for i in range(n - 1):
        dt = t_s[i + 1] - t_s[i]
        slope = (y_s[i + 1] - y_s[i]) / dt if dt != 0.0 else 0.0
        intercept = y_s[i] - slope * t_s[i]
        functions.append(lambda t, s=slope, b=intercept: s * t + b)
    functions.append(float(y_s[-1]))  # stała dla t >= t_s[-1]

    return np.piecewise(t_out, conditions, functions)


def whittaker_shannon(t_out, t_s, y_s):
    """Interpolacja Whittakera-Shannona (wzór kardynalny) ręcznie ze wzoru.

    Wzór:
        x(t) = sum_{n=0}^{N-1} x[n] * sinc( (t - t_n) / T )

    gdzie T = 1/fs jest okresem próbkowania, a sinc(u) = sin(pi*u)/(pi*u)
    (tj. sinc znormalizowany, identyczny jak np.sinc).

    Obliczenie odbywa się ręcznie przez jawne zbudowanie macierzy jąder:
        kernel[i, n] = sin(pi * u_in) / (pi * u_in),   u_in = (t_i - t_n) / T
    z wyjątkiem u = 0, gdzie sinc(0) = 1 (obsługiwane przez np.divide z where).
    Wynik to iloczyn wektorowy: x(t_out) = kernel @ y_s.
    """
    t_out = np.asarray(t_out, dtype=float)
    t_s = np.asarray(t_s, dtype=float)
    y_s = np.asarray(y_s, dtype=float)
    n = len(t_s)
    if n < 2:
        return np.full(len(t_out), y_s[0] if n == 1 else 0.0)

    T = t_s[1] - t_s[0]  # okres próbkowania (zakładamy równomierne)
    if T == 0.0:
        return np.full(len(t_out), y_s[0])

    # Macierz argumentów sinc: u[i, n] = (t_out[i] - t_s[n]) / T
    u = (t_out[:, np.newaxis] - t_s[np.newaxis, :]) / T  # shape (M, N)

    # Ręczne obliczenie sinc(u) = sin(pi*u) / (pi*u), sinc(0) = 1
    pi_u = np.pi * u
    with np.errstate(invalid='ignore', divide='ignore'):
        kernel = np.where(u == 0.0, 1.0, np.sin(pi_u) / pi_u)

    # Suma po wszystkich próbkach: x(t_out) = kernel @ y_s
    return kernel @ y_s


def reconstruct(t_out, t_s, y_s, method):
    """Rekonstrukcja sygnału z dyskretnych próbek."""
    if len(t_s) < 2:
        return np.interp(t_out, t_s, y_s)
    if method == 'ZOH':
        indices = np.searchsorted(t_s, t_out, side='right') - 1
        indices = np.clip(indices, 0, len(y_s) - 1)
        return y_s[indices]
    elif method == 'liniowa':
        return interpolate_piecewise(t_out, t_s, y_s)
    elif method == 'sinc':
        T = t_s[1] - t_s[0]
        if len(t_s) > 400:
            return np.interp(t_out, t_s, y_s)
        phase_mat = (t_out[:, None] - t_s[None, :]) / T
        return np.dot(np.sinc(phase_mat), y_s)
    elif method == 'W-S':
        # Whittaker-Shannon: limit liczby próbek żeby uniknąć zbyt długich obliczeń
        if len(t_s) > 600:
            # dla bardzo gęstych siatek używamy bloków 512 próbek ze środka
            mid = len(t_s) // 2
            half = 256
            t_s_w = t_s[max(0, mid - half):mid + half]
            y_s_w = y_s[max(0, mid - half):mid + half]
        else:
            t_s_w, y_s_w = t_s, y_s
        return whittaker_shannon(t_out, t_s_w, y_s_w)
    return np.zeros(len(t_out))


_WINDOW_COLORS = ['tab:blue', 'tab:red', 'tab:green', 'tab:orange']
_WINDOW_NAMES = ['Hamming', 'Hann', 'Blackman', 'Dirichlet']


def _make_window(name, N):
    """Zwraca funkcję okna z SciPy dla zadanej długości N."""
    if name == 'Hamming':
        return signal.windows.hamming(N)
    elif name == 'Hann':
        return signal.windows.hann(N)
    elif name == 'Blackman':
        return signal.windows.blackman(N)
    else:  # Dirichlet (prostokątne)
        return signal.windows.boxcar(N)


_WAVELET_FAMILIES = [
    'Haar', 'Daubechies', 'Symlets', 'Coiflets',
    'Biortogonalna', 'Gaussian', 'Meksykański kapelusz', 'Morleta'
]

_BIOR_VARIANTS = [
    '1.1', '1.3', '1.5', '2.2', '2.4', '2.6', '2.8',
    '3.1', '3.3', '3.5', '3.7', '3.9', '4.4', '5.5', '6.8'
]


def _resolve_wavelet(family, order):
    """Zwraca krotkę (wavelet_name, is_continuous, is_bior)."""
    order = int(order)
    if family == 'Haar':
        return 'haar', False, False
    elif family == 'Daubechies':
        o = max(1, min(order, 38))
        return f'db{o}', False, False
    elif family == 'Symlets':
        o = max(2, min(order, 20))
        return f'sym{o}', False, False
    elif family == 'Coiflets':
        o = max(1, min(order, 17))
        return f'coif{o}', False, False
    elif family == 'Biortogonalna':
        idx = max(0, min(order - 1, len(_BIOR_VARIANTS) - 1))
        return f'bior{_BIOR_VARIANTS[idx]}', False, True
    elif family == 'Gaussian':
        o = max(1, min(order, 8))
        return f'gaus{o}', True, False
    elif family == 'Meksykański kapelusz':
        return 'mexh', True, False
    elif family == 'Morleta':
        return 'morl', True, False
    return 'haar', False, False


def _plot_daubechies():
    """Rysuje falki Daubechies z sub-panelem wariantów i trybem porównania."""
    db_name = radio_db_variant.value_selected      # np. 'db4'
    level = int(slider_db_level.val)
    compare = check_db_compare.get_status()[0]
    current_order = int(db_name[2:])              # 'db4' -> 4

    if compare:
        n = max(current_order, 2)
        colors = plt.cm.tab10(np.linspace(0, 0.9, n))

        ax.cla()
        ax.grid(True, alpha=0.3)
        ax.set_xlabel('Czas')
        ax.set_ylabel('Amplituda')
        ax.set_title(f'Porównanie ψ: db1..{db_name}  (poziom={level})')

        ax_psd.cla()
        ax_psd.grid(True, alpha=0.3)
        ax_psd.set_xlabel('Czas')
        ax_psd.set_ylabel('Amplituda')
        ax_psd.set_title(f'Porównanie φ: db1..{db_name}  (poziom={level})')

        for i, o in enumerate(range(1, n + 1)):
            w = pywt.Wavelet(f'db{o}')
            phi, psi, x = w.wavefun(level=level)
            ax.plot(x, psi, color=colors[i], linewidth=1.8, label=f'db{o}')
            ax_psd.plot(x, phi, color=colors[i], linewidth=1.8, label=f'db{o}')

        ax.axhline(0, color='k', linewidth=0.8, linestyle='--', alpha=0.4)
        ax.legend(fontsize=9, ncol=2)
        ax_psd.axhline(0, color='k', linewidth=0.8, linestyle='--', alpha=0.4)
        ax_psd.legend(fontsize=9, ncol=2)
    else:
        w = pywt.Wavelet(db_name)
        phi, psi, x = w.wavefun(level=level)
        h = w.dec_lo   # niskopasmowy filtr dekompozycji
        g = w.dec_hi   # wysokopasmowy filtr dekompozycji

        ax.cla()
        ax.grid(True, alpha=0.3)
        ax.plot(x, psi, 'b-', linewidth=2)
        ax.axhline(0, color='k', linewidth=0.8, linestyle='--', alpha=0.5)
        ax.set_xlabel('Czas')
        ax.set_ylabel('Amplituda')
        ax.set_title(f'Funkcja falki (ψ): {db_name}  (poziom={level})')

        ax_psd.cla()
        ax_psd.grid(True, alpha=0.3)
        idx = np.arange(len(h))
        ml1, sl1, bl1 = ax_psd.stem(idx, h, linefmt='b-', markerfmt='bo',
                                     basefmt='k-', label='h  (dec_lo)')
        ml2, sl2, bl2 = ax_psd.stem(idx, g, linefmt='r--', markerfmt='rs',
                                     basefmt='k-', label='g  (dec_hi)')
        ml1.set_markersize(6); sl1.set_linewidth(1.5)
        ml2.set_markersize(6); sl2.set_linewidth(1.5)
        ax_psd.axhline(0, color='k', linewidth=0.8, linestyle='--', alpha=0.5)
        ax_psd.set_xlabel('Indeks próbki')
        ax_psd.set_ylabel('Wartość')
        ax_psd.set_title(f'Współczynniki filtrów: {db_name}  (N={len(h)})')
        ax_psd.legend(fontsize=11)


def update_wavelets_plot():
    """Rysuje wybraną falkę: lewy wykres = ψ, prawy = φ / widmo / filtry."""
    global line, line_env_pos, line_env_neg
    family = radio_wavelet_family.value_selected

    try:
        if family == 'Daubechies':
            _plot_daubechies()
        else:
            order = int(slider_wavelet_order.val)
            wavelet_name, is_continuous, is_bior = _resolve_wavelet(family, order)

            if is_continuous:
                w = pywt.ContinuousWavelet(wavelet_name)
                psi, x = w.wavefun(level=10)

                ax.cla()
                ax.grid(True, alpha=0.3)
                ax.plot(x, np.real(psi), 'b-', linewidth=2)
                ax.axhline(0, color='k', linewidth=0.8, linestyle='--', alpha=0.5)
                ax.set_xlabel('Czas')
                ax.set_ylabel('Amplituda')
                ax.set_title(f'Funkcja falki (ψ): {wavelet_name}')

                dt = float(x[1] - x[0]) if len(x) > 1 else 1.0
                psi_fft = np.abs(np.fft.rfft(np.real(psi), n=2048))
                freqs_w = np.fft.rfftfreq(2048, d=dt)
                ax_psd.cla()
                ax_psd.grid(True, alpha=0.3)
                ax_psd.plot(freqs_w, psi_fft, 'r-', linewidth=2)
                ax_psd.set_xlabel('Częstotliwość')
                ax_psd.set_ylabel('|Ψ(f)|')
                ax_psd.set_xlim(0, freqs_w[np.argmax(psi_fft)] * 6 + 0.01)
                ax_psd.set_title(f'Widmo amplitudowe falki: {wavelet_name}')

            elif is_bior:
                w = pywt.Wavelet(wavelet_name)
                phi_d, psi_d, phi_r, psi_r, x = w.wavefun(level=10)

                ax.cla()
                ax.grid(True, alpha=0.3)
                ax.plot(x, psi_d, 'b-', linewidth=2, label='Dekomponująca (ψ_d)')
                ax.plot(x, psi_r, 'r--', linewidth=2, label='Rekonstruująca (ψ_r)')
                ax.axhline(0, color='k', linewidth=0.8, linestyle='--', alpha=0.5)
                ax.set_xlabel('Czas')
                ax.set_ylabel('Amplituda')
                ax.set_title(f'Funkcje falki (ψ): {wavelet_name}')
                ax.legend(fontsize=11)

                ax_psd.cla()
                ax_psd.grid(True, alpha=0.3)
                ax_psd.plot(x, phi_d, 'b-', linewidth=2, label='Dekomponująca (φ_d)')
                ax_psd.plot(x, phi_r, 'r--', linewidth=2, label='Rekonstruująca (φ_r)')
                ax_psd.axhline(0, color='k', linewidth=0.8, linestyle='--', alpha=0.5)
                ax_psd.set_xlabel('Czas')
                ax_psd.set_ylabel('Amplituda')
                ax_psd.set_title(f'Funkcje skalujące (φ): {wavelet_name}')
                ax_psd.legend(fontsize=11)

            else:
                w = pywt.Wavelet(wavelet_name)
                phi, psi, x = w.wavefun(level=10)

                ax.cla()
                ax.grid(True, alpha=0.3)
                ax.plot(x, psi, 'b-', linewidth=2)
                ax.axhline(0, color='k', linewidth=0.8, linestyle='--', alpha=0.5)
                ax.set_xlabel('Czas')
                ax.set_ylabel('Amplituda')
                ax.set_title(f'Funkcja falki (ψ): {wavelet_name}')

                ax_psd.cla()
                ax_psd.grid(True, alpha=0.3)
                ax_psd.plot(x, phi, 'g-', linewidth=2)
                ax_psd.axhline(0, color='k', linewidth=0.8, linestyle='--', alpha=0.5)
                ax_psd.set_xlabel('Czas')
                ax_psd.set_ylabel('Amplituda')
                ax_psd.set_title(f'Funkcja skalująca (φ): {wavelet_name}')

    except Exception as e:
        print(f'[Falki] Błąd dla {family}: {e}')

    fig.canvas.draw_idle()


_DC_WAVELETS = ['haar', 'db2', 'db4', 'db8', 'sym4', 'sym8', 'coif2']


def _get_decomp_signal():
    """Zwraca (t, y, fs, tmax, title) zależnie od wybranego źródła sygnału."""
    source = radio_dc_source.value_selected
    if source == 'z panelu':
        freq = slider_freq.val
        amp = slider_amp.val
        phase = slider_phase.val
        tmax = slider_tmax.val
        impulse_pos = slider_impulse_pos.val
        signal_type = radio.value_selected
        samples = int(slider_samples.val)
        t = np.linspace(0, tmax, samples)
        y = generate_signal(t, signal_type, freq, amp, phase, impulse_pos)
        fs = samples / tmax
        title = f'{signal_type}  (f={freq:.1f} Hz, A={amp:.1f})'
        return t, y, fs, tmax, title
    elif source == 'z pliku CSV':
        t_csv = _loaded_signal['t']
        y_csv = _loaded_signal['y']
        if y_csv is None:
            raise ValueError('Brak załadowanego sygnału CSV. Użyj przycisku "Załaduj CSV" w zakładce Sygnał.')
        t = t_csv.astype(float)
        y = y_csv.astype(float)
        dt = float(t[1] - t[0]) if len(t) > 1 else 1.0
        fs = 1.0 / dt if dt > 0 else float(len(y))
        tmax = float(t[-1])
        title = f'CSV: {_loaded_signal["label"]}'
        return t, y, fs, tmax, title
    else:  # chirp
        f0 = float(slider_dc_f0.val)
        f1 = float(slider_dc_f1.val)
        N = 2048
        t = np.linspace(0, 1.0, N, endpoint=False)
        y = signal.chirp(t, f0=max(f0, 0.5), f1=max(f1, f0 + 1.0), t1=1.0, method='linear')
        fs = float(N)
        tmax = 1.0
        title = f'Sygnał świergotliwy: {f0:.0f} Hz \u2192 {f1:.0f} Hz'
        return t, y, fs, tmax, title


def update_decomp_plot():
    """Dispatcher — wywołuje DWT lub EMD zależnie od wybranej metody."""
    if radio_dc_method.value_selected == 'EMD':
        _decomp_emd_plot()
    else:
        _decomp_dwt_plot()


def _decomp_dwt_plot():
    """Dekompozycja sygnału 3 falkami — skalogram DWT."""
    level = int(slider_dc_lv.val)
    wavelet_names = [
        radio_dc_wv1.value_selected,
        radio_dc_wv2.value_selected,
        radio_dc_wv3.value_selected,
    ]

    try:
        t, chirp_sig, fs, tmax, title = _get_decomp_signal()
    except Exception as e:
        print(f'[DWT] Błąd generowania sygnału: {e}')
        return

    N = len(chirp_sig)

    ax_dc_sig.cla()
    ax_dc_sig.plot(t, chirp_sig, 'b-', linewidth=1.2)
    ax_dc_sig.set_title(title)
    ax_dc_sig.set_ylabel('Amplituda')
    ax_dc_sig.set_xlim(t[0], t[-1])
    ax_dc_sig.grid(True, alpha=0.3)

    _cmaps = ['hot', 'plasma', 'viridis']
    for ax_d, wname, cmap in zip([ax_dc_1, ax_dc_2, ax_dc_3], wavelet_names, _cmaps):
        ax_d.cla()
        try:
            max_lv = pywt.dwt_max_level(N, wname)
            lv = min(level, max_lv)
            coeffs = pywt.wavedec(chirp_sig, wname, level=lv)
            # coeffs[0]=cA_lv, coeffs[1..lv]=cD_lv..cD_1
            # Odwróć detale: wiersz 0 = cD1 (najwyższa częstotliwość)
            details = list(reversed(coeffs[1:]))
            n_lv = len(details)

            scalogram = np.zeros((n_lv, N))
            for j, cD in enumerate(details):
                t_c = np.linspace(0.0, 1.0, len(cD))
                scalogram[j, :] = np.interp(np.linspace(0.0, 1.0, N), t_c, cD)

            energy = np.abs(scalogram)
            vmax = float(np.max(energy)) if energy.max() > 0 else 1.0

            ax_d.imshow(energy, aspect='auto', cmap=cmap,
                        vmin=0, vmax=vmax,
                        extent=[t[0], t[-1], n_lv + 0.5, 0.5],
                        interpolation='bilinear')

            ax_d.set_yticks(range(1, n_lv + 1))
            ax_d.set_yticklabels([f'cD{k}' for k in range(1, n_lv + 1)], fontsize=8)
            ax_d.set_xlabel('Czas [s]', fontsize=9)
            ax_d.set_ylabel('Poziom', fontsize=9)
            ax_d.set_title(f'DWT: {wname}  (L={lv})', fontsize=11)
            ax_d.tick_params(axis='x', labelsize=8)
        except Exception as e:
            ax_d.text(0.5, 0.5, f'Błąd:\n{e}', transform=ax_d.transAxes,
                      ha='center', va='center', color='red', fontsize=10)
            ax_d.set_title(f'DWT: {wname}')

    fig.canvas.draw_idle()


def _decomp_emd_plot():
    """Dekompozycja sygnału metodą EMD (sift/ensemble/mask)."""
    max_imfs = int(slider_dc_lv.val)
    sift_method = radio_dc_emd_sift.value_selected

    try:
        t_emd, chirp_sig, fs_emd, tmax, title = _get_decomp_signal()
    except Exception as e:
        print(f'[EMD] Błąd generowania sygnału: {e}')
        return

    N = len(chirp_sig)
    f_max_vis = fs_emd / 2.0

    # Sygnał na górze
    ax_dc_sig.cla()
    ax_dc_sig.plot(t_emd, chirp_sig, 'b-', linewidth=1.2)
    ax_dc_sig.set_title(title)
    ax_dc_sig.set_ylabel('Amplituda')
    ax_dc_sig.set_xlim(t_emd[0], t_emd[-1])
    ax_dc_sig.grid(True, alpha=0.3)

    # Oblicz IMFs
    try:
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            if sift_method == 'sift':
                imfs = emd.sift.sift(chirp_sig, max_imfs=max_imfs)
            elif sift_method == 'ensemble':
                imfs = emd.sift.ensemble_sift(chirp_sig, max_imfs=max_imfs,
                                              nensembles=4, nprocesses=1)
            else:  # mask
                imfs = emd.sift.mask_sift(chirp_sig, max_imfs=max_imfs)
    except Exception as e:
        for _ax in (ax_dc_1, ax_dc_2, ax_dc_3):
            _ax.cla()
            _ax.text(0.5, 0.5, f'Błąd EMD:\n{e}', transform=_ax.transAxes,
                     ha='center', va='center', color='red', fontsize=10)
        fig.canvas.draw_idle()
        return

    n_imfs = imfs.shape[1]
    colors = plt.cm.tab10(np.linspace(0, 0.9, n_imfs))

    # --- Wykres 1: przebiegi IMF (zestawione z odsunięciem) ---
    ax_dc_1.cla()
    ax_dc_1.grid(True, alpha=0.25)
    scale = float(np.max(np.abs(imfs))) if np.max(np.abs(imfs)) > 0 else 1.0
    step = scale * 2.5
    for k in range(n_imfs):
        ax_dc_1.plot(t_emd, imfs[:, k] + k * step, color=colors[k], linewidth=0.9)
        ax_dc_1.axhline(k * step, color='gray', linewidth=0.4, linestyle='--', alpha=0.5)
    ax_dc_1.set_yticks([k * step for k in range(n_imfs)])
    ax_dc_1.set_yticklabels([f'IMF {k + 1}' for k in range(n_imfs)], fontsize=8)
    ax_dc_1.set_xlabel('Czas [s]', fontsize=9)
    ax_dc_1.set_xlim(t_emd[0], t_emd[-1])
    ax_dc_1.set_title(f'IMFs — {sift_method}  (n={n_imfs})', fontsize=11)
    ax_dc_1.tick_params(axis='x', labelsize=8)

    # --- Wykres 2: widma amplitudowe IMF (znormalizowane, zestawione) ---
    ax_dc_2.cla()
    ax_dc_2.grid(True, alpha=0.25)
    freqs_fft = np.fft.rfftfreq(N, d=1.0 / fs_emd)
    mask_f = freqs_fft <= f_max_vis
    for k in range(n_imfs):
        X = np.abs(np.fft.rfft(imfs[:, k])) * 2.0 / N
        X_norm = X / (np.max(X) + 1e-12)
        ax_dc_2.plot(freqs_fft[mask_f], X_norm[mask_f] + k * 1.3,
                     color=colors[k], linewidth=0.9)
        ax_dc_2.axhline(k * 1.3, color='gray', linewidth=0.4, linestyle='--', alpha=0.5)
    ax_dc_2.set_yticks([k * 1.3 for k in range(n_imfs)])
    ax_dc_2.set_yticklabels([f'IMF {k + 1}' for k in range(n_imfs)], fontsize=8)
    ax_dc_2.set_xlabel('Częstotliwość [Hz]', fontsize=9)
    ax_dc_2.set_xlim(0, f_max_vis)
    ax_dc_2.set_title('Widma amplitudowe IMF', fontsize=11)
    ax_dc_2.tick_params(axis='x', labelsize=8)

    # --- Wykres 3: widmo Hilberta–Huanga (HHT) ---
    ax_dc_3.cla()
    try:
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            IP, IF, IA = emd.spectra.frequency_transform(imfs, int(fs_emd), 'hilbert')
        IF_clipped = np.clip(IF, 0, f_max_vis)
        edges = np.linspace(0, f_max_vis, 129)
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            f_centers, hht = emd.spectra.hilberthuang(
                IF_clipped, IA, edges,
                sum_time=False, sum_imfs=True, mode='energy'
            )
        hht_db = 10.0 * np.log10(np.maximum(hht, 1e-30))
        vmax = float(np.max(hht_db))
        vmin = vmax - 60.0
        ax_dc_3.imshow(hht_db, aspect='auto', origin='lower', cmap='hot',
                       vmin=vmin, vmax=vmax,
                       extent=[t_emd[0], t_emd[-1], 0.0, f_max_vis],
                       interpolation='bilinear')
        ax_dc_3.set_xlabel('Czas [s]', fontsize=9)
        ax_dc_3.set_ylabel('Częst. chwilowa [Hz]', fontsize=9)
        ax_dc_3.set_title('Widmo Hilberta–Huanga (HHT)', fontsize=11)
        ax_dc_3.tick_params(axis='both', labelsize=8)
    except Exception as e:
        ax_dc_3.text(0.5, 0.5, f'Błąd HHT:\n{e}', transform=ax_dc_3.transAxes,
                     ha='center', va='center', color='red', fontsize=10)
        ax_dc_3.set_title('HHT — błąd')

    fig.canvas.draw_idle()


def update_spectrogram_plot():
    """Rysuje spektrogram aktualnego sygnału (STFT via scipy.signal.spectrogram)."""
    freq = slider_freq.val
    amp = slider_amp.val
    phase = slider_phase.val
    tmax = slider_tmax.val
    impulse_pos = slider_impulse_pos.val
    signal_type = radio.value_selected
    samples = int(slider_samples.val)

    nfft = int(slider_spec_nfft.val)
    overlap_pct = float(slider_spec_overlap.val)
    window_name = radio_spec_window.value_selected
    cmap = radio_spec_cmap.value_selected
    scale = radio_spec_scale.value_selected

    t_sig = np.linspace(0, tmax, samples)
    y_sig = generate_signal(t_sig, signal_type, freq, amp, phase, impulse_pos)
    fs_sig = samples / tmax

    noverlap = int(nfft * overlap_pct / 100.0)
    win = _make_window(window_name, nfft)

    # Wyczyść dedykowane osie colorbara (nie naruszamy geometrii ax_spec)
    ax_spec_cb.cla()

    # Górny pasek — przebieg sygnału
    ax_spec_sig.cla()
    ax_spec_sig.plot(t_sig, y_sig, 'b-', linewidth=1.2)
    ax_spec_sig.set_title(f'Sygnał: {signal_type}  (f={freq:.1f} Hz, A={amp:.1f})')
    ax_spec_sig.set_ylabel('Amplituda')
    ax_spec_sig.set_xlim(0, tmax)
    ax_spec_sig.grid(True, alpha=0.3)

    # Spektrogram
    ax_spec.cla()
    try:
        f_s, t_s, Sxx = signal.spectrogram(
            y_sig, fs=fs_sig, window=win,
            nperseg=nfft, noverlap=noverlap,
            scaling='density'
        )
        if scale == 'dB':
            Sxx_plot = 10.0 * np.log10(np.maximum(Sxx, 1e-12))
            vmax = float(np.max(Sxx_plot))
            vmin = vmax - 80.0
            cb_label = 'PSD [dB/Hz]'
        else:
            Sxx_plot = Sxx
            vmax = float(np.max(Sxx_plot)) if np.max(Sxx_plot) > 0 else 1.0
            vmin = 0.0
            cb_label = 'PSD [V²/Hz]'
        im = ax_spec.pcolormesh(t_s, f_s, Sxx_plot, shading='gouraud',
                                cmap=cmap, vmin=vmin, vmax=vmax)
        ax_spec.set_ylabel('Częstotliwość [Hz]')
        ax_spec.set_xlabel('Czas [s]')
        ax_spec.set_xlim(t_s[0] if len(t_s) > 0 else 0,
                         t_s[-1] if len(t_s) > 0 else tmax)
        ax_spec.set_ylim(0, fs_sig / 2)
        ax_spec.set_title(
            f'Spektrogram — okno: {window_name}, NFFT={nfft}, nakładanie={overlap_pct:.0f}%'
        )
        fig.colorbar(im, cax=ax_spec_cb)
        ax_spec_cb.set_ylabel(cb_label, fontsize=11)
    except Exception as e:
        ax_spec.text(0.5, 0.5, f'Błąd spektrogramu:\n{e}',
                     transform=ax_spec.transAxes, ha='center', va='center',
                     color='red', fontsize=12)
        ax_spec.set_title('Spektrogram — błąd')
    fig.canvas.draw_idle()


def update_windows_plot():
    """Rysuje okna nałożone na aktualny sygnał oraz ich widma amplitudowe."""
    N = int(slider_window_N.val)
    selected = check_windows.get_status()  # [Hamming, Hann, Blackman, Dirichlet]
    n_fft = 4096

    # Pobierz aktualny sygnał z suwaków (przycięty do N próbek)
    freq = slider_freq.val
    amp = slider_amp.val
    phase = slider_phase.val
    tmax = slider_tmax.val
    impulse_pos = slider_impulse_pos.val
    signal_type = radio.value_selected
    t_win = np.linspace(0, tmax, N)
    y_sig = generate_signal(t_win, signal_type, freq, amp, phase, impulse_pos)
    fs_win = N / tmax

    ax.cla()
    ax.set_title(f'Sygnał z nałożonym oknem (N={N}, sygnał: {signal_type})')
    ax.set_xlabel('Czas [s]')
    ax.set_ylabel('Amplituda')
    ax.set_xlim(0, tmax)
    ax.grid(True, alpha=0.3)
    # Sygnał oryginalny (tło)
    ax.plot(t_win, y_sig, color='gray', linewidth=1.2, alpha=0.45, label='Sygnał')

    ax_psd.cla()
    ax_psd.set_title('Widmo amplitudowe sygnału z oknem')
    ax_psd.set_xlabel('Częstotliwość [Hz]')
    ax_psd.set_ylabel('Amplituda [dB]')
    freqs_hz = np.fft.rfftfreq(n_fft, d=1.0 / fs_win)
    ax_psd.set_xlim(0, min(fs_win / 2, float(slider_freq_zoom.val) * 5))
    ax_psd.set_ylim(-120, 5)
    ax_psd.grid(True, alpha=0.3)

    any_visible = False
    for i, name in enumerate(_WINDOW_NAMES):
        if not selected[i]:
            continue
        any_visible = True
        win = _make_window(name, N)
        y_windowed = y_sig * win
        ax.plot(t_win, y_windowed, color=_WINDOW_COLORS[i], linewidth=1.8, label=name)
        W = np.fft.rfft(y_windowed, n=n_fft)
        W_max = np.max(np.abs(W))
        amp_db = 20.0 * np.log10(np.abs(W) / max(W_max, 1e-12) + 1e-15)
        ax_psd.plot(freqs_hz, amp_db, color=_WINDOW_COLORS[i], linewidth=1.5, label=name)

    if any_visible:
        ax.legend(loc='upper right', fontsize=11)
        ax_psd.legend(loc='upper right', fontsize=11)

    fig.canvas.draw_idle()


def update_sampling_plot():
    """Aktualizuje prawy wykres w trybie próbkowania."""
    freq = slider_freq.val
    amp = slider_amp.val
    phase = slider_phase.val
    tmax = slider_tmax.val
    impulse_pos = slider_impulse_pos.val
    signal_type = radio.value_selected
    samples = int(slider_samples.val)
    fs_s = float(slider_fs_sample.val)
    bits = int(slider_bits.val)
    fc_lp = float(slider_lp_cutoff.val)
    recon_method = radio_recon.value_selected
    view_mode = radio_sampling_view.value_selected

    t_cont = np.linspace(0, tmax, samples)
    y_cont = generate_signal(t_cont, signal_type, freq, amp, phase, impulse_pos)

    # Filtr anty-aliasingowy (LP) przed próbkowaniem
    nyquist_cont = samples / (2.0 * tmax)
    fc_safe = min(fc_lp, nyquist_cont * 0.99, fs_s / 2.0 * 0.99)
    if fc_safe > 0.5:
        b_lp, a_lp = signal.butter(4, fc_safe / nyquist_cont, btype='low')
        try:
            y_filtered = signal.filtfilt(b_lp, a_lp, y_cont)
        except Exception:
            y_filtered = y_cont.copy()
    else:
        y_filtered = y_cont.copy()

    # Dyskretne próbki
    n_samp = max(2, int(fs_s * tmax))
    t_s = np.linspace(0, tmax, n_samp)
    y_s_raw = np.interp(t_s, t_cont, y_filtered)
    y_s = quantize(y_s_raw, bits, amp)

    nyquist = fs_s / 2.0
    ax_psd.cla()
    ax_psd.grid(True, alpha=0.3)

    nyquist_ok = freq > 0 and fs_s >= 2.0 * freq
    status = 'Nyquist OK' if nyquist_ok else 'ALIASING!'

    if view_mode == 'przebieg':
        ax_psd.plot(t_cont, y_cont, 'b--', linewidth=2.0, alpha=0.55, label='Oryginalny')
        if fc_safe < nyquist_cont * 0.97:
            ax_psd.plot(t_cont, y_filtered, 'c-', linewidth=1.8, alpha=0.7,
                        label=f'Po filtrze LP ({fc_lp:.1f} Hz)')
        ml, sl, bl = ax_psd.stem(t_s, y_s, linefmt='g-', markerfmt='go', basefmt='k-')
        ml.set_label('Próbki')
        ml.set_markersize(6)
        sl.set_linewidth(1.6)
        if recon_method != 'brak':
            y_recon = reconstruct(t_cont, t_s, y_s, recon_method)
            ax_psd.plot(t_cont, y_recon, 'r-', linewidth=2.5, alpha=0.9,
                        label=f'Rekonstrukcja ({recon_method})')
        ax_psd.set_xlim(0, tmax)
        ymax = max(float(np.max(np.abs(y_cont))), 1e-6)
        ax_psd.set_ylim(-ymax * 1.35, ymax * 1.35)
        ax_psd.set_xlabel('Czas [s]')
        ax_psd.set_ylabel('Amplituda')
        ax_psd.set_title(
            f'Próbkowanie: fs={fs_s:.0f} Hz | Nyquist={nyquist:.0f} Hz | {bits} bit | {status}')
        ax_psd.legend(loc='upper right', fontsize=8)

    elif view_mode == 'błąd':
        # Błąd wybranej metody rekonstrukcji względem sygnału oryginalnego
        if recon_method == 'brak':
            # gdy brak rekonstrukcji, pokaż błąd ZOH jako punkt odniesienia
            y_recon_err = reconstruct(t_cont, t_s, y_s, 'ZOH')
            err_label = 'Błąd ZOH (brak wybranej rekonstrukcji)'
        else:
            y_recon_err = reconstruct(t_cont, t_s, y_s, recon_method)
            err_label = f'Błąd interpolacji ({recon_method})'
        error = y_recon_err - y_cont
        ax_psd.axhline(0, color='k', linewidth=1.2, linestyle='--', alpha=0.5)
        ax_psd.plot(t_cont, error, color='crimson', linewidth=2.2, label=err_label)
        ax_psd.fill_between(t_cont, error, alpha=0.18, color='crimson')
        # Węzły interpolacji — błąd = 0 dla metod interpolujących (nie aproksymujących)
        error_at_nodes = np.interp(t_s, t_cont, error)
        ax_psd.scatter(t_s, error_at_nodes, color='green', s=25, zorder=5,
                       label='Węzły próbkowania')
        rmse = np.sqrt(np.mean(error ** 2))
        max_err = np.max(np.abs(error))
        ax_psd.set_xlim(0, tmax)
        err_range = max(max_err * 1.35, 1e-9)
        ax_psd.set_ylim(-err_range, err_range)
        ax_psd.set_xlabel('Czas [s]')
        ax_psd.set_ylabel('Błąd [jedn. amplitudy]')
        ax_psd.set_title(
            f'Błąd ({recon_method}) | RMSE={rmse:.4f} | Max={max_err:.4f} | {status}')
        ax_psd.legend(loc='upper right', fontsize=8)

    else:  # widmo
        fs_cont = samples / tmax
        f_orig, psd_orig = signal.periodogram(y_cont, fs_cont)
        if n_samp >= 4:
            f_samp, psd_samp = signal.periodogram(y_s, fs_s)
        else:
            f_samp, psd_samp = np.array([0.0]), np.array([0.0])
        ax_psd.plot(f_orig, psd_orig, 'b-', linewidth=2.0, alpha=0.7, label='Oryginalny')
        ax_psd.plot(f_samp, psd_samp, 'r-', linewidth=2.2, alpha=0.88,
                    label=f'Spróbkowany ({fs_s:.0f} Hz)')
        ax_psd.axvline(x=nyquist, color='orange', linestyle='--', linewidth=2.0,
                       label=f'Nyquist ({nyquist:.0f} Hz)')
        ax_psd.set_xlabel('Częstotliwość [Hz]')
        ax_psd.set_ylabel('PSD [V²/Hz]')
        ax_psd.set_title(f'Widmo próbkowania: fs={fs_s:.0f} Hz | {bits} bit | {status}')
        ax_psd.legend(loc='upper right', fontsize=8)


def update_psd_plot(y_new, fs_current):
    """Aktualizuje prawy wykres PSD/widma."""
    psd_method = radio_psd.value_selected
    psd_scale = radio_psd_scale.value_selected
    ax_psd.cla()
    ax_psd.grid(True, alpha=0.3)

    if psd_method == 'widmo ampl.':
        # Widmo amplitudowe: |X(f)| znormalizowane do amplitudy sygnału
        N = len(y_new)
        X = np.fft.rfft(y_new)
        freqs_fft = np.fft.rfftfreq(N, d=1.0 / fs_current)
        amplitude = np.abs(X) * 2.0 / N
        amplitude[0] /= 2.0  # składowa DC nie jest podwajana
        f_max = float(slider_freq_zoom.val)
        mask = freqs_fft <= f_max
        f_vis = freqs_fft[mask]
        a_vis = amplitude[mask]
        if psd_scale == 'dB':
            a_vis_db = 20.0 * np.log10(np.maximum(a_vis, 1e-12))
            y_data = a_vis_db
            y_label = 'Amplituda [dB]'
            y_min = float(np.max(a_vis_db)) - 80.0
            y_max = float(np.max(a_vis_db)) + 6.0
        else:
            y_data = a_vis
            y_label = 'Amplituda'
            amp_max = float(np.max(a_vis)) if len(a_vis) > 0 and np.max(a_vis) > 0 else 1.0
            y_min = 0
            y_max = amp_max * 1.15
        ax_psd.set_xlabel('Częstotliwość [Hz]')
        ax_psd.set_ylabel(y_label)
        ax_psd.set_xlim(0, f_max)
        if psd_scale == 'logarytmiczna':
            amp_max = float(np.max(a_vis)) if len(a_vis) > 0 and np.max(a_vis) > 0 else 1.0
            ax_psd.set_yscale('log')
            ax_psd.set_ylim(max(amp_max * 1e-6, 1e-12), amp_max * 10)
            if len(f_vis) > 200:
                ax_psd.plot(f_vis, y_data, 'b-', linewidth=1.5)
            else:
                ml, sl, bl = ax_psd.stem(f_vis, y_data, linefmt='b-', markerfmt='bo', basefmt='k-')
                ml.set_markersize(4)
                sl.set_linewidth(1.2)
        elif psd_scale == 'dB':
            ax_psd.set_yscale('linear')
            ax_psd.set_ylim(y_min, y_max)
            if len(f_vis) > 200:
                ax_psd.plot(f_vis, y_data, 'b-', linewidth=1.5)
            else:
                # vlines z bazą na dole – słupki wskazują w górę
                ax_psd.vlines(f_vis, y_min, y_data, colors='b', linewidth=1.2)
                ax_psd.plot(f_vis, y_data, 'bo', markersize=4)
                ax_psd.axhline(y_min, color='k', linewidth=0.8)
        else:
            ax_psd.set_yscale('linear')
            ax_psd.set_ylim(y_min, y_max)
            if len(f_vis) > 200:
                ax_psd.plot(f_vis, y_data, 'b-', linewidth=1.5)
            else:
                ml, sl, bl = ax_psd.stem(f_vis, y_data, linefmt='b-', markerfmt='bo', basefmt='k-')
                ml.set_markersize(4)
                sl.set_linewidth(1.2)
        ax_psd.set_title(f'Widmo amplitudowe (FFT) | N={N}')
        return

    if psd_method == 'widmo faz.':
        N = len(y_new)
        X = np.fft.rfft(y_new)
        freqs_fft = np.fft.rfftfreq(N, d=1.0 / fs_current)
        amplitude = np.abs(X) * 2.0 / N
        amplitude[0] /= 2.0
        f_max = float(slider_freq_zoom.val)
        mask = freqs_fft <= f_max
        f_vis = freqs_fft[mask]
        amp_vis = amplitude[mask]
        phase_deg = np.degrees(np.angle(X[mask]))
        # Maskuj fazy dla składowych poniżej 1% maksimum (szum numeryczny)
        thresh = np.max(amp_vis) * 0.01 if len(amp_vis) > 0 and np.max(amp_vis) > 0 else 1e-9
        valid = amp_vis >= thresh
        phase_clean = np.where(valid, phase_deg, np.nan)
        f_valid = f_vis[valid]
        p_valid = phase_clean[valid]
        ax_psd.scatter(f_valid, p_valid, color='purple', s=25, zorder=5)
        ax_psd.vlines(f_valid, 0, p_valid, colors='purple', linewidth=1.2, alpha=0.7)
        ax_psd.axhline(0, color='k', linewidth=0.9, linestyle='--', alpha=0.5)
        ax_psd.set_xlabel('Częstotliwość [Hz]')
        ax_psd.set_ylabel('Faza [°]')
        ax_psd.set_xlim(0, f_max)
        ax_psd.set_ylim(-195, 195)
        ax_psd.set_yticks([-180, -90, 0, 90, 180])
        ax_psd.set_title(f'Widmo fazowe (FFT) | N={N}')
        return

    if psd_method == 'FFT':
        # Jednostronne widmo amplitudowe: scipy.fft.rfft (tylko f >= 0)
        N = len(y_new)
        X = sp_fft.rfft(y_new)              # N//2+1 próbek, f >= 0
        freqs_pos = sp_fft.rfftfreq(N, d=1.0 / fs_current)
        amplitude = np.abs(X) * 2.0 / N    # podwojenie dla zachowania energii
        amplitude[0] /= 2.0                 # DC — nie podwajamy
        if N % 2 == 0:
            amplitude[-1] /= 2.0            # składowa Nyquista — nie podwajamy
        f_max = float(slider_freq_zoom.val)
        mask = freqs_pos <= f_max
        f_vis = freqs_pos[mask]
        a_vis = amplitude[mask]
        ax_psd.set_xlabel('Częstotliwość [Hz]')
        ax_psd.set_xlim(0, f_max)
        a_max = float(np.max(a_vis)) if len(a_vis) > 0 and np.max(a_vis) > 0 else 1.0
        if psd_scale == 'dB':
            a_db = 20.0 * np.log10(np.maximum(a_vis, 1e-12))
            db_max = float(np.max(a_db))
            ax_psd.plot(f_vis, a_db, 'g-', linewidth=1.5)
            ax_psd.set_ylabel('Amplituda [dB]')
            ax_psd.set_yscale('linear')
            ax_psd.set_ylim(db_max - 80.0, db_max + 6.0)
        elif psd_scale == 'logarytmiczna':
            ax_psd.plot(f_vis, a_vis, 'g-', linewidth=1.5)
            ax_psd.set_ylabel('Amplituda')
            ax_psd.set_yscale('log')
            ax_psd.set_ylim(max(a_max * 1e-6, 1e-12), a_max * 10)
        else:
            if len(f_vis) > 200:
                ax_psd.plot(f_vis, a_vis, 'g-', linewidth=1.5)
            else:
                ax_psd.vlines(f_vis, 0, a_vis, colors='g', linewidth=1.2)
                ax_psd.plot(f_vis, a_vis, 'go', markersize=4)
            ax_psd.set_ylabel('Amplituda')
            ax_psd.set_yscale('linear')
            ax_psd.set_ylim(0, a_max * 1.15)
        ax_psd.set_title(f'Widmo amplitudowe — scipy.fft (jednostronne) | N={N}')
        return

    if psd_method == 'periodogram':
        freqs, psd = signal.periodogram(y_new, fs_current)
    elif psd_method == 'welch':
        freqs, psd = signal.welch(y_new, fs_current)
    else:
        freqs, psd = psd_definition(y_new, fs_current)
    ax_psd.set_xlabel('Częstotliwość [Hz]')
    ax_psd.set_xlim(0, freqs[-1] if len(freqs) > 0 else 1)
    psd_max = np.max(psd) if len(psd) > 0 and np.max(psd) > 0 else 1
    if psd_scale == 'dB':
        psd_db = 10.0 * np.log10(np.maximum(psd, 1e-30))
        ax_psd.plot(freqs, psd_db, 'r-', linewidth=1.5)
        ax_psd.set_ylabel('PSD [dB/Hz]')
        ax_psd.set_yscale('linear')
        db_max = float(np.max(psd_db))
        ax_psd.set_ylim(db_max - 80.0, db_max + 6.0)
    elif psd_scale == 'logarytmiczna':
        ax_psd.plot(freqs, psd, 'r-', linewidth=1.5)
        ax_psd.set_ylabel('PSD [V²/Hz]')
        ax_psd.set_yscale('log')
        ax_psd.set_ylim(max(psd_max * 1e-6, 1e-12), psd_max * 10)
    else:
        ax_psd.plot(freqs, psd, 'r-', linewidth=1.5)
        ax_psd.set_ylabel('PSD [V²/Hz]')
        ax_psd.set_yscale('linear')
        ax_psd.set_ylim(0, psd_max * 1.1)
    ax_psd.set_title(f'Gęstość mocy widmowej ({psd_method})' + (' [dB]' if psd_scale == 'dB' else ''))


# Początkowy wykres
y = generate_signal(t, initial_signal_type, initial_freq, initial_amp, initial_phase, initial_impulse_position)
line, = ax.plot(t, y, 'b-', linewidth=2)
line_env_pos, = ax.plot([], [], 'r--', linewidth=1.5, alpha=0.75)
line_env_neg, = ax.plot([], [], 'r--', linewidth=1.5, alpha=0.75)
ax.set_xlim(0, initial_tmax)
ax.set_ylim(-3, 3)
ax.set_xlabel('Czas [s]')
ax.set_ylabel('Amplituda')
ax.set_title(f'Interaktywny wykres sygnału: {initial_signal_type}')
ax.grid(True, alpha=0.3)

# Inicjalizacja wykresu PSD (redrawn on first update via show_signal_panel)
psd_line = None

# --- Panel sygnału: slidery ---
ax_freq = plt.axes([0.20, 0.25, 0.45, 0.03])
slider_freq = Slider(ax_freq, 'Częstotliwość', 0.1, 10.0, valinit=initial_freq, valstep=0.1)

ax_amp = plt.axes([0.20, 0.20, 0.45, 0.03])
slider_amp = Slider(ax_amp, 'Amplituda', 0.1, 3.0, valinit=initial_amp, valstep=0.1)

ax_phase = plt.axes([0.20, 0.15, 0.45, 0.03])
slider_phase = Slider(ax_phase, 'Faza', 0, 2*np.pi, valinit=initial_phase, valstep=0.1)

ax_tmax = plt.axes([0.20, 0.10, 0.45, 0.03])
slider_tmax = Slider(ax_tmax, 'Zakres czasu', 1.0, 20.0, valinit=initial_tmax, valstep=0.5)

ax_impulse_pos = plt.axes([0.20, 0.05, 0.45, 0.03])
slider_impulse_pos = Slider(ax_impulse_pos, 'Pozycja impulsu', 0.0, initial_tmax, valinit=initial_impulse_position, valstep=0.1)

ax_samples = plt.axes([0.20, 0.00, 0.45, 0.03])
slider_samples = Slider(ax_samples, 'Liczba sampli', 100, 5000, valinit=initial_samples, valstep=100)

# --- Panel sygnału: typ sygnału ---
# Radio at right, below right strip, y=0.02..0.30 (no x overlap with sliders 0.06..0.69)
ax_radio = plt.axes([0.70, 0.02, 0.24, 0.28])
radio = RadioButtons(ax_radio, ('sinus', 'cosinus', 'prostokątny', 'piłokształtny', 'chirp', 'superpozycja', 'impuls jednostkowy', 'trójkątny', 'szum biały', 'szum browna', 'szum fioletowy'))

# --- Panel widma (domyślnie ukryty) ---
# Metoda: x=0.06..0.28  (left column)
ax_psd_method = plt.axes([0.06, 0.01, 0.22, 0.28])
ax_psd_method.set_title('Metoda', fontsize=15)
radio_psd = RadioButtons(ax_psd_method, ('periodogram', 'welch', 'definicja', 'widmo ampl.', 'widmo faz.', 'FFT'))
ax_psd_method.set_visible(False)

# Skala: x=0.31..0.53  (center, above zoom)
ax_psd_scale = plt.axes([0.31, 0.14, 0.22, 0.14])
ax_psd_scale.set_title('Skala osi Y', fontsize=15)
radio_psd_scale = RadioButtons(ax_psd_scale, ('liniowa', 'logarytmiczna', 'dB'))
ax_psd_scale.set_visible(False)

# Zoom slider: x=0.31..0.71  (center-right, below Skala)
ax_freq_zoom = plt.axes([0.40, 0.05, 0.40, 0.03])
slider_freq_zoom = Slider(ax_freq_zoom, 'Zoom częst. [Hz]', 0.5, 200.0, valinit=10.0, valstep=0.5)
ax_freq_zoom.set_visible(False)

# --- Panel próbkowania (domyślnie ukryty) ---
ax_fs_sample = plt.axes([0.20, 0.22, 0.45, 0.03])
slider_fs_sample = Slider(ax_fs_sample, 'Częst. próbkowania [Hz]', 1.0, 500.0,
                           valinit=50.0, valstep=1.0)
ax_fs_sample.set_visible(False)

ax_bits = plt.axes([0.20, 0.16, 0.45, 0.03])
slider_bits = Slider(ax_bits, 'Bity kwantyzacji', 1, 16, valinit=8, valstep=1)
ax_bits.set_visible(False)

ax_lp_cutoff = plt.axes([0.20, 0.10, 0.45, 0.03])
slider_lp_cutoff = Slider(ax_lp_cutoff, 'Filtr anty-aliasingowy [Hz]', 0.5, 250.0,
                           valinit=25.0, valstep=0.5)
ax_lp_cutoff.set_visible(False)

ax_recon_method = plt.axes([0.70, 0.04, 0.14, 0.24])
ax_recon_method.set_title('Rekonstrukcja', fontsize=13)
radio_recon = RadioButtons(ax_recon_method, ('brak', 'ZOH', 'liniowa', 'sinc', 'W-S'))
ax_recon_method.set_visible(False)

ax_sampling_view = plt.axes([0.86, 0.04, 0.12, 0.24])
ax_sampling_view.set_title('Widok', fontsize=13)
radio_sampling_view = RadioButtons(ax_sampling_view, ('przebieg', 'widmo', 'błąd'))
ax_sampling_view.set_visible(False)

# --- Przyciski przełączające panele ---
_TAB_X = 0.770
_TAB_W = 0.215
_TAB_H = 0.045
_TAB_GAP = 0.008
_TAB_TOP = 0.944

ax_tab_signal = plt.axes([_TAB_X, _TAB_TOP - 0 * (_TAB_H + _TAB_GAP), _TAB_W, _TAB_H])
btn_tab_signal = Button(ax_tab_signal, 'Sygnał', color='lightblue', hovercolor='deepskyblue')

ax_tab_spectral = plt.axes([_TAB_X, _TAB_TOP - 1 * (_TAB_H + _TAB_GAP), _TAB_W, _TAB_H])
btn_tab_spectral = Button(ax_tab_spectral, 'Widmo', color='lightgray', hovercolor='silver')

ax_tab_sampling = plt.axes([_TAB_X, _TAB_TOP - 2 * (_TAB_H + _TAB_GAP), _TAB_W, _TAB_H])
btn_tab_sampling = Button(ax_tab_sampling, 'Próbkowanie', color='lightgray', hovercolor='silver')

ax_tab_windows = plt.axes([_TAB_X, _TAB_TOP - 3 * (_TAB_H + _TAB_GAP), _TAB_W, _TAB_H])
btn_tab_windows = Button(ax_tab_windows, 'Okna', color='lightgray', hovercolor='silver')

ax_tab_wavelets = plt.axes([_TAB_X, _TAB_TOP - 4 * (_TAB_H + _TAB_GAP), _TAB_W, _TAB_H])
btn_tab_wavelets = Button(ax_tab_wavelets, 'Falki', color='lightgray', hovercolor='silver')

ax_tab_decomp = plt.axes([_TAB_X, _TAB_TOP - 5 * (_TAB_H + _TAB_GAP), _TAB_W, _TAB_H])
btn_tab_decomp = Button(ax_tab_decomp, 'Dekompozycja', color='lightgray', hovercolor='silver')

ax_tab_spectrogram = plt.axes([_TAB_X, _TAB_TOP - 6 * (_TAB_H + _TAB_GAP), _TAB_W, _TAB_H])
btn_tab_spectrogram = Button(ax_tab_spectrogram, 'Spektrogram', color='lightgray', hovercolor='silver')

ax_tab_quality = plt.axes([_TAB_X, _TAB_TOP - 7 * (_TAB_H + _TAB_GAP), _TAB_W, _TAB_H])
btn_tab_quality = Button(ax_tab_quality, 'Jakość sygnału', color='lightgray', hovercolor='silver')

ax_tab_denoise = plt.axes([_TAB_X, _TAB_TOP - 8 * (_TAB_H + _TAB_GAP), _TAB_W, _TAB_H])
btn_tab_denoise = Button(ax_tab_denoise, 'Odszumianie', color='lightgray', hovercolor='silver')

ax_envelope_check = plt.axes([_TAB_X, _TAB_TOP - 9 * (_TAB_H + _TAB_GAP), _TAB_W, _TAB_H])
check_envelope = CheckButtons(ax_envelope_check, ['Obwiednia'], [False])

# --- Przycisk ładowania CSV (prawy dolny róg, zawsze widoczny) ---
ax_load_button = plt.axes([_TAB_X, _TAB_TOP - 10 * (_TAB_H + _TAB_GAP), _TAB_W, _TAB_H])
load_button = Button(ax_load_button, 'Załaduj CSV', color='lightyellow', hovercolor='khaki')

# --- Przycisk zapisywania (prawy dolny róg, zawsze widoczny) ---
ax_save_button = plt.axes([_TAB_X, _TAB_TOP - 11 * (_TAB_H + _TAB_GAP), _TAB_W, _TAB_H])
save_button = Button(ax_save_button, 'Zapisz')

# --- Panel okien (domyślnie ukryty) ---
ax_window_N = plt.axes([0.20, 0.22, 0.45, 0.03])
slider_window_N = Slider(ax_window_N, 'Długość okna N', 16, 1024, valinit=256, valstep=16)
ax_window_N.set_visible(False)

ax_window_check = plt.axes([0.70, 0.03, 0.24, 0.26])
ax_window_check.set_title('Okna', fontsize=15)
check_windows = CheckButtons(ax_window_check, ['Hamming', 'Hann', 'Blackman', 'Dirichlet'],
                             [True, True, True, True])
ax_window_check.set_visible(False)

# --- Panel falek (domyślnie ukryty) ---
ax_wavelet_family = plt.axes([0.06, 0.01, 0.22, 0.28])
ax_wavelet_family.set_title('Rodzina falek', fontsize=15)
radio_wavelet_family = RadioButtons(ax_wavelet_family, _WAVELET_FAMILIES)
ax_wavelet_family.set_visible(False)

ax_wavelet_order = plt.axes([0.40, 0.05, 0.40, 0.03])
slider_wavelet_order = Slider(ax_wavelet_order, 'Rząd / wariant', 1, 20, valinit=4, valstep=1)
ax_wavelet_order.set_visible(False)

# --- Daubechies sub-panel (ukryty; widoczny tylko gdy wybrana rodzina Daubechies) ---
ax_db_variant = plt.axes([0.30, 0.01, 0.14, 0.28])
ax_db_variant.set_title('Wariant db', fontsize=15)
radio_db_variant = RadioButtons(ax_db_variant, [f'db{i}' for i in range(1, 11)])
ax_db_variant.set_visible(False)

ax_db_level = plt.axes([0.53, 0.22, 0.40, 0.03])
slider_db_level = Slider(ax_db_level, 'Rozdzielczość', 1, 12, valinit=8, valstep=1)
ax_db_level.set_visible(False)

ax_db_compare = plt.axes([0.47, 0.07, 0.22, 0.13])
ax_db_compare.set_title('Tryb', fontsize=13)
check_db_compare = CheckButtons(ax_db_compare, ['Porównaj warianty'], [False])
ax_db_compare.set_visible(False)

# --- Panel dekompozycji chirp (domyślnie ukryty) ---
# Pas 4 — RadioButtons (Falka 1/2/3) wyrównane z osiami skalogramów
ax_dc_wv1 = plt.axes([0.05,  0.01, 0.21, 0.22])
ax_dc_wv1.set_title('Falka 1', fontsize=13)
radio_dc_wv1 = RadioButtons(ax_dc_wv1, _DC_WAVELETS)
radio_dc_wv1.set_active(2)   # domyślnie db4
ax_dc_wv1.set_visible(False)

ax_dc_wv2 = plt.axes([0.283, 0.01, 0.21, 0.22])
ax_dc_wv2.set_title('Falka 2', fontsize=13)
radio_dc_wv2 = RadioButtons(ax_dc_wv2, _DC_WAVELETS)
radio_dc_wv2.set_active(4)   # domyślnie sym4
ax_dc_wv2.set_visible(False)

ax_dc_wv3 = plt.axes([0.516, 0.01, 0.21, 0.22])
ax_dc_wv3.set_title('Falka 3', fontsize=13)
radio_dc_wv3 = RadioButtons(ax_dc_wv3, _DC_WAVELETS)
radio_dc_wv3.set_active(6)   # domyślnie coif2
ax_dc_wv3.set_visible(False)

# Pas 3 — slidery (f0, f1, poziom), od dołu do góry, y = 0.28..0.39
ax_dc_f0 = plt.axes([0.20, 0.28, 0.53, 0.03])
slider_dc_f0 = Slider(ax_dc_f0, 'Częst. startowa [Hz]', 1.0, 100.0, valinit=5.0, valstep=1.0)
ax_dc_f0.set_visible(False)

ax_dc_f1 = plt.axes([0.20, 0.32, 0.53, 0.03])
slider_dc_f1 = Slider(ax_dc_f1, 'Częst. końcowa [Hz]', 10.0, 500.0, valinit=200.0, valstep=5.0)
ax_dc_f1.set_visible(False)

ax_dc_lv = plt.axes([0.20, 0.36, 0.53, 0.03])
slider_dc_lv = Slider(ax_dc_lv, 'Poziom dekompozycji', 2, 10, valinit=6, valstep=1)
ax_dc_lv.set_visible(False)

# Selektor metody dekompozycji DWT / EMD (zawsze widoczny w zakładce Dekompozycja)
ax_dc_method = plt.axes([0.75, 0.24, 0.22, 0.05])
ax_dc_method.set_title('Metoda', fontsize=13)
radio_dc_method = RadioButtons(ax_dc_method, ['DWT', 'EMD'])
ax_dc_method.set_visible(False)

# Selektor źródła sygnału (chirp z suwaków / dowolny sygnał z panelu / z pliku CSV)
ax_dc_source = plt.axes([0.75, 0.09, 0.22, 0.10])
ax_dc_source.set_title('Źródło sygnału', fontsize=13)
radio_dc_source = RadioButtons(ax_dc_source, ['chirp', 'z panelu', 'z pliku CSV'])
ax_dc_source.set_visible(False)

# Metoda prosiewania EMD (w pozycji ax_dc_wv1, widoczna tylko w trybie EMD)
ax_dc_emd_sift = plt.axes([0.05, 0.01, 0.21, 0.22])
ax_dc_emd_sift.set_title('Sift EMD', fontsize=13)
radio_dc_emd_sift = RadioButtons(ax_dc_emd_sift, ['sift', 'ensemble', 'mask'])
ax_dc_emd_sift.set_visible(False)

# --- Panel spektrogramu (domyślnie ukryty) ---
ax_spec_nfft = plt.axes([0.20, 0.36, 0.53, 0.03])
slider_spec_nfft = Slider(ax_spec_nfft, 'NFFT', 32, 1024, valinit=256, valstep=32)
ax_spec_nfft.set_visible(False)

ax_spec_overlap = plt.axes([0.20, 0.32, 0.53, 0.03])
slider_spec_overlap = Slider(ax_spec_overlap, 'Nakładanie [%]', 0, 95, valinit=75, valstep=5)
ax_spec_overlap.set_visible(False)

ax_spec_window = plt.axes([0.06, 0.01, 0.18, 0.22])
ax_spec_window.set_title('Okno', fontsize=15)
radio_spec_window = RadioButtons(ax_spec_window, ['Hamming', 'Hann', 'Blackman', 'Dirichlet'])
ax_spec_window.set_visible(False)

ax_spec_cmap = plt.axes([0.30, 0.01, 0.16, 0.22])
ax_spec_cmap.set_title('Mapa kolorów', fontsize=15)
radio_spec_cmap = RadioButtons(ax_spec_cmap, ['hot', 'viridis', 'plasma', 'jet'])
ax_spec_cmap.set_visible(False)

ax_spec_scale = plt.axes([0.52, 0.01, 0.16, 0.22])
ax_spec_scale.set_title('Skala', fontsize=15)
radio_spec_scale = RadioButtons(ax_spec_scale, ['liniowa', 'dB'])
radio_spec_scale.set_active(1)  # domyślnie dB
ax_spec_scale.set_visible(False)

# --- Panel jakości sygnału (domyślnie ukryty) ---
ax_qual_noise_std = plt.axes([0.20, 0.27, 0.50, 0.03])
slider_qual_noise_std = Slider(ax_qual_noise_std, 'Odch. std. szumu \u03c3', 0.0, 3.0, valinit=0.5, valstep=0.05)
ax_qual_noise_std.set_visible(False)

ax_qual_noise_type = plt.axes([0.05, 0.03, 0.18, 0.21])
ax_qual_noise_type.set_title('Typ szumu', fontsize=15)
radio_qual_noise_type = RadioButtons(ax_qual_noise_type, ['Gaussowski', 'Jednostajny', "Laplace'a"])
ax_qual_noise_type.set_visible(False)

ax_qual_source = plt.axes([0.26, 0.06, 0.18, 0.15])
ax_qual_source.set_title('Źródło sygnału', fontsize=15)
radio_qual_source = RadioButtons(ax_qual_source, ['z panelu', 'z pliku CSV'])
ax_qual_source.set_visible(False)

# --- Panel odszumiania (domyślnie ukryty) ---
ax_den_snr = plt.axes([0.20, 0.31, 0.40, 0.03])
slider_den_snr = Slider(ax_den_snr, 'SNR celu [dB]', -10.0, 40.0, valinit=10.0, valstep=1.0)
ax_den_snr.set_visible(False)

# Subpanel Savitzky-Golay
ax_den_sg_win = plt.axes([0.20, 0.25, 0.40, 0.03])
slider_den_sg_win = Slider(ax_den_sg_win, 'Okno SG (próbki)', 5, 101, valinit=11, valstep=2)
ax_den_sg_win.set_visible(False)

ax_den_sg_ord = plt.axes([0.20, 0.19, 0.40, 0.03])
slider_den_sg_ord = Slider(ax_den_sg_ord, 'Rząd SG', 1, 7, valinit=2, valstep=1)
ax_den_sg_ord.set_visible(False)

# Subpanel EMD (ta sama pozycja co sg_win — nie współistnieją)
ax_den_emd_imf = plt.axes([0.20, 0.25, 0.40, 0.03])
slider_den_emd_imf = Slider(ax_den_emd_imf, 'Odrzucone IMF (szum)', 1, 8, valinit=2, valstep=1)
ax_den_emd_imf.set_visible(False)

ax_den_noise_type = plt.axes([0.05, 0.02, 0.14, 0.12])
ax_den_noise_type.set_title('Typ szumu', fontsize=15)
radio_den_noise_type = RadioButtons(ax_den_noise_type, ['biały', 'brązowy'])
ax_den_noise_type.set_visible(False)

# Metoda odszumiania — umieszczona w prawej kolumnie (x=0.60) aby nie nakładać się ze suwakami
ax_den_method = plt.axes([0.65, 0.01, 0.15, 0.27])
ax_den_method.set_title('Metoda odszumiania', fontsize=15)
radio_den_method = RadioButtons(ax_den_method, ['Wiener', 'Savitzky-Golay', 'EMD'])
ax_den_method.set_visible(False)

ax_den_source = plt.axes([0.23, 0.02, 0.16, 0.12])
ax_den_source.set_title('\u0179r\u00f3d\u0142o sygna\u0142u', fontsize=15)
radio_den_source = RadioButtons(ax_den_source, ['z panelu', 'z pliku CSV'])
ax_den_source.set_visible(False)

_signal_panel_axes = [ax_freq, ax_amp, ax_phase, ax_tmax, ax_impulse_pos, ax_samples, ax_radio]
_spectral_panel_axes = [ax_psd_method, ax_psd_scale, ax_freq_zoom]
_sampling_panel_axes = [ax_fs_sample, ax_bits, ax_lp_cutoff, ax_recon_method, ax_sampling_view]
_windows_panel_axes = [ax_window_N, ax_window_check]
# ax_db_* są zarządzane osobno — NIE wchodzą do _wavelet_panel_axes
_wavelet_panel_axes = [ax_wavelet_family, ax_wavelet_order]
_db_subpanel_axes   = [ax_db_variant, ax_db_level, ax_db_compare]
_decomp_panel_axes  = [ax_dc_wv1, ax_dc_wv2, ax_dc_wv3, ax_dc_f0, ax_dc_f1, ax_dc_lv, ax_dc_method, ax_dc_source]
_decomp_emd_axes    = [ax_dc_emd_sift]   # zarządzane osobno (DWT/EMD toggle)
_decomp_display_axes = [ax_dc_sig, ax_dc_1, ax_dc_2, ax_dc_3]
_spectrogram_panel_axes = [ax_spec_nfft, ax_spec_overlap, ax_spec_window, ax_spec_cmap, ax_spec_scale]
_spectrogram_display_axes = [ax_spec_sig, ax_spec, ax_spec_cb]
_quality_panel_axes   = [ax_qual_noise_std, ax_qual_noise_type, ax_qual_source]
_quality_display_axes = [ax_qual_orig, ax_qual_diff, ax_qual_metrics]
_denoise_panel_axes   = [ax_den_snr, ax_den_noise_type, ax_den_method, ax_den_source]
_denoise_sub_axes     = [ax_den_sg_win, ax_den_sg_ord, ax_den_emd_imf]   # widoczne warunkowo
_denoise_display_axes = [ax_den_noisy, ax_den_clean, ax_den_metrics]

# Zapamiętaj oryginalne pozycje (przed jakimkolwiek przesunięciem)
_offscreen = [-2.0, -2.0, 0.01, 0.01]
_signal_positions    = {a: list(a.get_position().bounds) for a in _signal_panel_axes}
_spectral_positions  = {a: list(a.get_position().bounds) for a in _spectral_panel_axes}
_sampling_positions  = {a: list(a.get_position().bounds) for a in _sampling_panel_axes}
_windows_positions   = {a: list(a.get_position().bounds) for a in _windows_panel_axes}
_wavelet_positions   = {a: list(a.get_position().bounds) for a in _wavelet_panel_axes}
_db_subpanel_positions = {a: list(a.get_position().bounds) for a in _db_subpanel_axes}
_decomp_positions    = {a: list(a.get_position().bounds) for a in _decomp_panel_axes}
_decomp_emd_positions = {a: list(a.get_position().bounds) for a in _decomp_emd_axes}
_spectrogram_positions = {a: list(a.get_position().bounds) for a in _spectrogram_panel_axes}
_quality_positions     = {a: list(a.get_position().bounds) for a in _quality_panel_axes}
_denoise_positions     = {a: list(a.get_position().bounds) for a in _denoise_panel_axes}
_denoise_sub_positions = {a: list(a.get_position().bounds) for a in _denoise_sub_axes}

def _apply_panel(show_list, show_pos):
    """Ukrywa wszystkie panele kontrolne i pokazuje tylko żądany.
    Przy okazji przywraca główne osie (ax/ax_psd) i ukrywa osie dekomp/spektrogram."""
    all_axes = (_signal_panel_axes + _spectral_panel_axes + _sampling_panel_axes
                + _windows_panel_axes + _wavelet_panel_axes + _db_subpanel_axes
                + _decomp_panel_axes + _decomp_emd_axes + _spectrogram_panel_axes
                + _quality_panel_axes + _denoise_panel_axes + _denoise_sub_axes)
    for a in all_axes:
        a.set_position(_offscreen)
        a.set_visible(False)
    for a in show_list:
        a.set_position(show_pos[a])
        a.set_visible(True)
    ax.set_visible(True)
    ax_psd.set_visible(True)
    for a in _decomp_display_axes:
        a.set_visible(False)
    for a in _spectrogram_display_axes:
        a.set_visible(False)
    for a in _quality_display_axes:
        a.set_visible(False)
    for a in _denoise_display_axes:
        a.set_visible(False)

def _set_tab_colors(active_btn):
    for btn in (btn_tab_signal, btn_tab_spectral, btn_tab_sampling,
                btn_tab_windows, btn_tab_wavelets, btn_tab_decomp,
                btn_tab_spectrogram, btn_tab_quality, btn_tab_denoise):
        color = 'lightblue' if btn is active_btn else 'lightgray'
        btn.color = color
        btn.ax.set_facecolor(color)

def show_signal_panel(event=None):
    global _current_tab
    _current_tab = 'signal'
    _apply_panel(_signal_panel_axes, _signal_positions)
    _set_tab_colors(btn_tab_signal)
    update(None)
    fig.canvas.draw_idle()

def show_spectral_panel(event=None):
    global _current_tab
    _current_tab = 'spectral'
    _apply_panel(_spectral_panel_axes, _spectral_positions)
    _set_tab_colors(btn_tab_spectral)
    update(None)
    fig.canvas.draw_idle()

def show_sampling_panel(event=None):
    global _current_tab
    _current_tab = 'sampling'
    _apply_panel(_sampling_panel_axes, _sampling_positions)
    _set_tab_colors(btn_tab_sampling)
    update(None)
    fig.canvas.draw_idle()

def show_windows_panel(event=None):
    global _current_tab
    _current_tab = 'windows'
    _apply_panel(_windows_panel_axes, _windows_positions)
    _set_tab_colors(btn_tab_windows)
    update_windows_plot()
    fig.canvas.draw_idle()

def _update_db_subpanel_visibility():
    """Pokazuje/ukrywa kontrolki Daubechies przez zmianę pozycji i widoczności."""
    is_db = (radio_wavelet_family.value_selected == 'Daubechies')
    # ax_wavelet_order: pokaż tylko gdy NIE Daubechies
    if is_db:
        ax_wavelet_order.set_position(_offscreen)
        ax_wavelet_order.set_visible(False)
    else:
        ax_wavelet_order.set_position(_wavelet_positions[ax_wavelet_order])
        ax_wavelet_order.set_visible(True)
    # db sub-panel: pokaż tylko gdy Daubechies
    for a in _db_subpanel_axes:
        if is_db:
            a.set_position(_db_subpanel_positions[a])
            a.set_visible(True)
        else:
            a.set_position(_offscreen)
            a.set_visible(False)


def _update_decomp_subpanel_visibility():
    """Pokazuje/ukrywa kontrolki DWT vs EMD oraz chirp vs z panelu."""
    is_emd = (radio_dc_method.value_selected == 'EMD')
    is_chirp = (radio_dc_source.value_selected == 'chirp')
    # Falki DWT — widoczne tylko w trybie DWT
    for a in (ax_dc_wv1, ax_dc_wv2, ax_dc_wv3):
        if is_emd:
            a.set_position(_offscreen)
            a.set_visible(False)
        else:
            a.set_position(_decomp_positions[a])
            a.set_visible(True)
    # Sift EMD — widoczny tylko w trybie EMD
    if is_emd:
        ax_dc_emd_sift.set_position(_decomp_emd_positions[ax_dc_emd_sift])
        ax_dc_emd_sift.set_visible(True)
    else:
        ax_dc_emd_sift.set_position(_offscreen)
        ax_dc_emd_sift.set_visible(False)
    # Slidery chirp f0/f1 — widoczne tylko gdy źródło = chirp
    for a in (ax_dc_f0, ax_dc_f1):
        if is_chirp:
            a.set_position(_decomp_positions[a])
            a.set_visible(True)
        else:
            a.set_position(_offscreen)
            a.set_visible(False)
    # Etykieta suwaka zależy od trybu
    slider_dc_lv.label.set_text('Max. IMFs' if is_emd else 'Poziom dekompozycji')


def show_wavelets_panel(event=None):
    global _current_tab
    _current_tab = 'wavelets'
    _apply_panel(_wavelet_panel_axes, _wavelet_positions)
    _update_db_subpanel_visibility()
    _set_tab_colors(btn_tab_wavelets)
    update_wavelets_plot()
    fig.canvas.draw_idle()

def show_decomp_panel(event=None):
    global _current_tab
    _current_tab = 'decomp'
    _apply_panel(_decomp_panel_axes, _decomp_positions)  # przywraca ax/ax_psd, ukrywa dekomp display
    _update_decomp_subpanel_visibility()
    # nadpisanie: ukryj główne osie, pokaż osie dekompozycji
    ax.set_visible(False)
    ax_psd.set_visible(False)
    for a in _decomp_display_axes:
        a.set_visible(True)
    _set_tab_colors(btn_tab_decomp)
    update_decomp_plot()
    fig.canvas.draw_idle()

def show_spectrogram_panel(event=None):
    global _current_tab
    _current_tab = 'spectrogram'
    _apply_panel(_spectrogram_panel_axes, _spectrogram_positions)
    ax.set_visible(False)
    ax_psd.set_visible(False)
    for a in _spectrogram_display_axes:
        a.set_visible(True)
    _set_tab_colors(btn_tab_spectrogram)
    update_spectrogram_plot()
    fig.canvas.draw_idle()


def compute_quality_metrics(y_orig, y_noisy):
    """Oblicza MSE, SNR i PSNR między sygnałem oryginalnym a zaszumionym.

    MSE  = mean((y_orig - y_noisy)^2)
    SNR  = 10 * log10(P_signal / P_noise)  [dB]
    PSNR = 10 * log10(MAX^2 / MSE)         [dB],  MAX = max|y_orig|
    """
    noise = y_noisy - y_orig
    mse = float(np.mean(noise ** 2))
    p_signal = float(np.mean(y_orig ** 2))
    p_noise = float(np.mean(noise ** 2))
    if p_signal <= 0:
        snr = float('-inf')
    elif p_noise < 1e-20:
        snr = float('inf')
    else:
        snr = 10.0 * np.log10(p_signal / p_noise)
    max_val = float(np.max(np.abs(y_orig)))
    if mse < 1e-20:
        psnr = float('inf')
    elif max_val < 1e-20:
        psnr = float('-inf')
    else:
        psnr = 20.0 * np.log10(max_val/np.sqrt(mse))
    return mse, snr, psnr


def update_quality_plot():
    """Rysuje sygnał oryginalny z szumem, błąd oraz wyświetla miary SNR/PSNR/MSE."""
    source = radio_qual_source.value_selected
    if source == 'z pliku CSV':
        if _loaded_signal['y'] is None:
            ax_qual_orig.cla()
            ax_qual_orig.text(0.5, 0.5,
                              'Brak załadowanego sygnału CSV.\n'
                              'Użyj przycisku "Załaduj CSV" w zakładce Sygnał.',
                              ha='center', va='center',
                              transform=ax_qual_orig.transAxes, fontsize=13)
            ax_qual_diff.cla()
            ax_qual_metrics.cla()
            ax_qual_metrics.axis('off')
            fig.canvas.draw_idle()
            return
        t = _loaded_signal['t'].astype(float)
        y_orig = _loaded_signal['y'].astype(float)
    else:  # z panelu
        freq = slider_freq.val
        amp = slider_amp.val
        phase = slider_phase.val
        tmax = slider_tmax.val
        impulse_pos = slider_impulse_pos.val
        signal_type = radio.value_selected
        samples = int(slider_samples.val)
        t = np.linspace(0, tmax, samples)
        y_orig = generate_signal(t, signal_type, freq, amp, phase, impulse_pos)

    N = len(y_orig)
    noise_std = float(slider_qual_noise_std.val)
    noise_type = radio_qual_noise_type.value_selected
    # Ustalony ziarno — stabilne wartości miar przy tych samych parametrach
    rng = np.random.default_rng(42)
    if noise_type == 'Gaussowski':
        noise = rng.normal(0.0, noise_std, N)
    elif noise_type == 'Jednostajny':
        half = noise_std * np.sqrt(3.0)
        noise = rng.uniform(-half, half, N)
    else:  # Laplace'a
        scale = noise_std / np.sqrt(2.0)
        noise = rng.laplace(0.0, scale, N)
    y_noisy = y_orig + noise

    mse, snr, psnr = compute_quality_metrics(y_orig, y_noisy)

    # Wykres: oryginalny + zaszumiony
    ax_qual_orig.cla()
    ax_qual_orig.plot(t, y_orig, 'b-', linewidth=1.5, label='Oryginalny')
    ax_qual_orig.plot(t, y_noisy, 'r-', linewidth=1.0, alpha=0.7, label='Zaszumiony')
    ax_qual_orig.set_title('Sygnał oryginalny i zaszumiony')
    ax_qual_orig.set_xlabel('Czas [s]')
    ax_qual_orig.set_ylabel('Amplituda')
    ax_qual_orig.legend(fontsize=12, loc='upper right')
    ax_qual_orig.grid(True, alpha=0.3)
    ax_qual_orig.set_xlim(t[0], t[-1])

    # Wykres: szum / błąd
    ax_qual_diff.cla()
    ax_qual_diff.plot(t, y_noisy - y_orig, 'g-', linewidth=1.0)
    ax_qual_diff.axhline(0, color='k', linewidth=0.8, linestyle='--')
    ax_qual_diff.set_title('Szum / błąd  (zaszumiony \u2212 oryginalny)')
    ax_qual_diff.set_xlabel('Czas [s]')
    ax_qual_diff.set_ylabel('Błąd')
    ax_qual_diff.grid(True, alpha=0.3)
    ax_qual_diff.set_xlim(t[0], t[-1])

    # Wy\u015bwietl miary jako\u015bci
    ax_qual_metrics.cla()
    ax_qual_metrics.axis('off')
    snr_str  = (f'{snr:.2f} dB'  if np.isfinite(snr)  else ('\u221e dB'  if snr  > 0 else '\u2212\u221e dB'))
    psnr_str = (f'{psnr:.2f} dB' if np.isfinite(psnr) else ('\u221e dB'  if psnr > 0 else '\u2212\u221e dB'))
    mse_str  = f'{mse:.6g}'
    metrics_text = (f'MSE = {mse_str}          '
                    f'SNR = {snr_str}          '
                    f'PSNR = {psnr_str}')
    ax_qual_metrics.text(
        0.5, 0.5, metrics_text,
        ha='center', va='center',
        transform=ax_qual_metrics.transAxes, fontsize=16,
        bbox=dict(boxstyle='round,pad=0.5', facecolor='lightyellow',
                  edgecolor='goldenrod', alpha=0.9))
    fig.canvas.draw_idle()


def show_quality_panel(event=None):
    global _current_tab
    _current_tab = 'quality'
    _apply_panel(_quality_panel_axes, _quality_positions)
    ax.set_visible(False)
    ax_psd.set_visible(False)
    for a in _quality_display_axes:
        a.set_visible(True)
    _set_tab_colors(btn_tab_quality)
    update_quality_plot()
    fig.canvas.draw_idle()


def _update_denoise_subpanel_visibility():
    """Pokazuje/ukrywa suwaki specyficzne dla Savitzky-Golay i EMD."""
    method = radio_den_method.value_selected
    is_sg  = (method == 'Savitzky-Golay')
    is_emd = (method == 'EMD')
    for a in (ax_den_sg_win, ax_den_sg_ord):
        if is_sg:
            a.set_position(_denoise_sub_positions[a])
            a.set_visible(True)
        else:
            a.set_position(_offscreen)
            a.set_visible(False)
    if is_emd:
        ax_den_emd_imf.set_position(_denoise_sub_positions[ax_den_emd_imf])
        ax_den_emd_imf.set_visible(True)
    else:
        ax_den_emd_imf.set_position(_offscreen)
        ax_den_emd_imf.set_visible(False)


def _add_noise_at_snr(y_orig, snr_db, noise_type):
    """Dodaje szum biały lub brązowy do sygnału z zadanym SNR [dB]."""
    N = len(y_orig)
    rng = np.random.default_rng(42)
    p_signal = max(float(np.mean(y_orig ** 2)), 1e-20)
    snr_lin   = 10.0 ** (snr_db / 10.0)
    noise_pow = p_signal / snr_lin
    if noise_type == 'biały':
        noise = rng.normal(0.0, np.sqrt(noise_pow), N)
    else:  # brązowy (całka szumu białego)
        white = rng.normal(0.0, 1.0, N)
        brown = np.cumsum(white)
        brown -= np.mean(brown)
        p_brown = max(float(np.mean(brown ** 2)), 1e-20)
        noise = brown * np.sqrt(noise_pow / p_brown)
    return y_orig + noise


def update_denoise_plot():
    """Zaszumia sygnał z zadanym SNR i wyświetla oryginalny, zaszumiony i odszumiony."""
    source = radio_den_source.value_selected
    if source == 'z pliku CSV':
        if _loaded_signal['y'] is None:
            ax_den_noisy.cla()
            ax_den_noisy.text(0.5, 0.5,
                              'Brak załadowanego sygnału CSV.\n'
                              'Użyj przycisku "Załaduj CSV".',
                              ha='center', va='center',
                              transform=ax_den_noisy.transAxes, fontsize=13)
            ax_den_clean.cla()
            ax_den_metrics.cla()
            ax_den_metrics.axis('off')
            fig.canvas.draw_idle()
            return
        t      = _loaded_signal['t'].astype(float)
        y_orig = _loaded_signal['y'].astype(float)
    else:
        freq        = slider_freq.val
        amp         = slider_amp.val
        phase       = slider_phase.val
        tmax        = slider_tmax.val
        impulse_pos = slider_impulse_pos.val
        signal_type = radio.value_selected
        samples     = int(slider_samples.val)
        t      = np.linspace(0, tmax, samples)
        y_orig = generate_signal(t, signal_type, freq, amp, phase, impulse_pos)

    snr_db     = float(slider_den_snr.val)
    noise_type = radio_den_noise_type.value_selected
    y_noisy    = _add_noise_at_snr(y_orig, snr_db, noise_type)

    method = radio_den_method.value_selected
    try:
        if method == 'Wiener':
            y_clean = signal.wiener(y_noisy)
        elif method == 'Savitzky-Golay':
            win  = int(slider_den_sg_win.val)
            ord_ = int(slider_den_sg_ord.val)
            if win % 2 == 0:
                win += 1
            win  = max(win, ord_ + 2)
            ord_ = min(ord_, win - 2)
            y_clean = signal.savgol_filter(y_noisy, win, ord_)
        else:  # EMD
            n_discard = int(slider_den_emd_imf.val)
            max_imfs  = min(10, max(n_discard + 2, 4))
            with warnings.catch_warnings():
                warnings.simplefilter('ignore')
                imfs = emd.sift.sift(y_noisy, max_imfs=max_imfs)
            n_discard = min(n_discard, imfs.shape[1] - 1)
            y_clean   = np.sum(imfs[:, n_discard:], axis=1)
    except Exception as e:
        print(f'[Odszumianie] Błąd metody {method}: {e}')
        y_clean = y_noisy.copy()

    mse_in,  snr_in,  _ = compute_quality_metrics(y_orig, y_noisy)
    mse_out, snr_out, _ = compute_quality_metrics(y_orig, y_clean)

    def _fmt(v):
        return (f'{v:.2f}\u00a0dB' if np.isfinite(v)
                else ('\u221e\u00a0dB' if v > 0 else '\u2212\u221e\u00a0dB'))

    # Wykres 1: oryginalny + zaszumiony
    ax_den_noisy.cla()
    ax_den_noisy.plot(t, y_orig,  'b-', linewidth=1.5, label='Oryginalny')
    ax_den_noisy.plot(t, y_noisy, color='tomato', linewidth=0.8, alpha=0.8,
                      label=f'Zaszumiony ({noise_type}, {snr_db:.0f}\u00a0dB)')
    ax_den_noisy.set_title('Sygnał oryginalny i zaszumiony')
    ax_den_noisy.set_xlabel('Czas [s]')
    ax_den_noisy.set_ylabel('Amplituda')
    ax_den_noisy.legend(fontsize=11, loc='upper right')
    ax_den_noisy.grid(True, alpha=0.3)
    ax_den_noisy.set_xlim(t[0], t[-1])

    # Wykres 2: oryginalny + odszumiony
    ax_den_clean.cla()
    ax_den_clean.plot(t, y_orig,  'b-', linewidth=1.5, alpha=0.5, label='Oryginalny')
    ax_den_clean.plot(t, y_clean, 'g-', linewidth=1.5, label=f'Odszumiony — {method}')
    ax_den_clean.set_title(f'Wynik odszumiania: {method}')
    ax_den_clean.set_xlabel('Czas [s]')
    ax_den_clean.set_ylabel('Amplituda')
    ax_den_clean.legend(fontsize=11, loc='upper right')
    ax_den_clean.grid(True, alpha=0.3)
    ax_den_clean.set_xlim(t[0], t[-1])

    # Pasek metryk
    ax_den_metrics.cla()
    ax_den_metrics.axis('off')
    txt = (f'Wejście:  SNR = {_fmt(snr_in)},  MSE = {mse_in:.4g}'
           f'     \u2502     '
           f'Wyjście:  SNR = {_fmt(snr_out)},  MSE = {mse_out:.4g}'
           f'     \u2502     '
           f'\u0394SNR = {snr_out - snr_in:+.2f}\u00a0dB')
    ax_den_metrics.text(
        0.5, 0.5, txt,
        ha='center', va='center',
        transform=ax_den_metrics.transAxes, fontsize=14,
        bbox=dict(boxstyle='round,pad=0.4', facecolor='lightcyan',
                  edgecolor='steelblue', alpha=0.9))
    fig.canvas.draw_idle()


def show_denoise_panel(event=None):
    global _current_tab
    _current_tab = 'denoise'
    _apply_panel(_denoise_panel_axes, _denoise_positions)
    _update_denoise_subpanel_visibility()
    ax.set_visible(False)
    ax_psd.set_visible(False)
    for a in _denoise_display_axes:
        a.set_visible(True)
    _set_tab_colors(btn_tab_denoise)
    update_denoise_plot()
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
    global line, line_env_pos, line_env_neg
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

    if _current_tab not in ('windows', 'wavelets', 'decomp', 'spectrogram', 'quality', 'denoise'):
        if line.axes is None:
            ax.cla()
            ax.grid(True, alpha=0.3)
            line, = ax.plot([], [], 'b-', linewidth=2)
            line_env_pos, = ax.plot([], [], 'r--', linewidth=1.5, alpha=0.75)
            line_env_neg, = ax.plot([], [], 'r--', linewidth=1.5, alpha=0.75)
        line.set_data(t_new, y_new)
        ax.set_xlim(0, tmax)
        if signal_type == 'impuls jednostkowy':
            ax.set_ylim(-0.1 * amp, amp * 1.2)
        else:
            ax.set_ylim(-amp * 2.5, amp * 2.5)
        ax.set_title(f'Wykres sygnału: {signal_type}')

        show_env = check_envelope.get_status()[0]
        if show_env:
            env = np.abs(signal.hilbert(y_new))
            line_env_pos.set_data(t_new, env)
            line_env_neg.set_data(t_new, -env)
            line_env_pos.set_visible(True)
            line_env_neg.set_visible(True)
        else:
            line_env_pos.set_visible(False)
            line_env_neg.set_visible(False)

    if _current_tab == 'sampling':
        update_sampling_plot()
    elif _current_tab == 'windows':
        update_windows_plot()
    elif _current_tab == 'spectrogram':
        update_spectrogram_plot()
    elif _current_tab == 'quality':
        update_quality_plot()
    elif _current_tab == 'denoise':
        update_denoise_plot()
    elif _current_tab in ('wavelets', 'decomp'):
        pass  # obsługiwane przez własne funkcje update
    else:
        update_psd_plot(y_new, samples / tmax)
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
load_button.on_clicked(load_csv_signal)
btn_tab_signal.on_clicked(show_signal_panel)
btn_tab_spectral.on_clicked(show_spectral_panel)
btn_tab_sampling.on_clicked(show_sampling_panel)
btn_tab_windows.on_clicked(show_windows_panel)
btn_tab_wavelets.on_clicked(show_wavelets_panel)
btn_tab_decomp.on_clicked(show_decomp_panel)
btn_tab_spectrogram.on_clicked(show_spectrogram_panel)
btn_tab_quality.on_clicked(show_quality_panel)
btn_tab_denoise.on_clicked(show_denoise_panel)

slider_den_snr.on_changed(lambda val: update_denoise_plot())
slider_den_sg_win.on_changed(lambda val: update_denoise_plot())
slider_den_sg_ord.on_changed(lambda val: update_denoise_plot())
slider_den_emd_imf.on_changed(lambda val: update_denoise_plot())
radio_den_noise_type.on_clicked(lambda label: update_denoise_plot())
radio_den_source.on_clicked(lambda label: update_denoise_plot())

def _on_den_method_changed(label):
    _update_denoise_subpanel_visibility()
    update_denoise_plot()
    fig.canvas.draw_idle()
radio_den_method.on_clicked(_on_den_method_changed)

slider_qual_noise_std.on_changed(lambda val: update_quality_plot())
radio_qual_noise_type.on_clicked(lambda label: update_quality_plot())
radio_qual_source.on_clicked(lambda label: update_quality_plot())

radio_spec_window.on_clicked(lambda label: update_spectrogram_plot())
radio_spec_cmap.on_clicked(lambda label: update_spectrogram_plot())
radio_spec_scale.on_clicked(lambda label: update_spectrogram_plot())
slider_spec_nfft.on_changed(lambda val: update_spectrogram_plot())
slider_spec_overlap.on_changed(lambda val: update_spectrogram_plot())

radio_dc_wv1.on_clicked(lambda label: update_decomp_plot())
radio_dc_wv2.on_clicked(lambda label: update_decomp_plot())
radio_dc_wv3.on_clicked(lambda label: update_decomp_plot())
slider_dc_f0.on_changed(lambda val: update_decomp_plot())
slider_dc_f1.on_changed(lambda val: update_decomp_plot())
slider_dc_lv.on_changed(lambda val: update_decomp_plot())

def _on_dc_method_changed(label):
    _update_decomp_subpanel_visibility()
    update_decomp_plot()
    fig.canvas.draw_idle()

radio_dc_method.on_clicked(_on_dc_method_changed)
radio_dc_emd_sift.on_clicked(lambda label: update_decomp_plot())
radio_dc_source.on_clicked(lambda label: (_update_decomp_subpanel_visibility(), update_decomp_plot(), fig.canvas.draw_idle()))

slider_window_N.on_changed(lambda val: update_windows_plot())
check_windows.on_clicked(lambda label: update_windows_plot())

def _on_wavelet_family_changed(label):
    _update_db_subpanel_visibility()
    update_wavelets_plot()
    fig.canvas.draw_idle()

radio_wavelet_family.on_clicked(_on_wavelet_family_changed)
slider_wavelet_order.on_changed(lambda val: update_wavelets_plot())
radio_db_variant.on_clicked(lambda label: update_wavelets_plot())
slider_db_level.on_changed(lambda val: update_wavelets_plot())
check_db_compare.on_clicked(lambda label: update_wavelets_plot())

slider_fs_sample.on_changed(update)
slider_freq_zoom.on_changed(update)
slider_bits.on_changed(update)
slider_lp_cutoff.on_changed(update)
radio_recon.on_clicked(update)
radio_sampling_view.on_clicked(update)
check_envelope.on_clicked(update)

# Inicjalizacja: pokaż panel sygnału, ukryj pozostałe
show_signal_panel()

fig.canvas.manager.set_window_title('Interaktywny generator sygnałów')
# Próbuj zmaksymalizować okno (nie pełny ekran). Testujemy popularne API backendów.
try:
    mgr = plt.get_current_fig_manager()
    # Jeśli manager expose 'window', spróbuj typowych metod maximize
    if hasattr(mgr, 'window'):
        w = mgr.window
        try:
            if hasattr(w, 'showMaximized'):
                w.showMaximized()
            elif hasattr(w, 'maximize'):
                w.maximize()
            elif hasattr(w, 'state'):
                # TkAgg: state('zoomed') często działa
                try:
                    w.state('zoomed')
                except Exception:
                    # Tk: wm_attributes fallback
                    if hasattr(w, 'wm_attributes'):
                        try:
                            w.wm_attributes('-zoomed', True)
                        except Exception:
                            pass
        except Exception:
            pass
    else:
        # Fallback: try manager-level window access
        m2 = fig.canvas.manager
        if hasattr(m2, 'window'):
            w = m2.window
            try:
                if hasattr(w, 'showMaximized'):
                    w.showMaximized()
                elif hasattr(w, 'maximize'):
                    w.maximize()
                elif hasattr(w, 'state'):
                    try:
                        w.state('zoomed')
                    except Exception:
                        if hasattr(w, 'wm_attributes'):
                            try:
                                w.wm_attributes('-zoomed', True)
                            except Exception:
                                pass
            except Exception:
                pass
except Exception:
    # Jeśli wszystko zawiedzie, nie przerywamy działania programu
    pass

plt.show()
