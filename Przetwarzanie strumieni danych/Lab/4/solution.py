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
    """WGM z definicji Wienera-Chinczyna (ręczne całkowanie bez FFT):
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

_current_tab = 'signal'


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
    if psd_method == 'periodogram':
        freqs, psd = signal.periodogram(y_new, fs_current)
    elif psd_method == 'welch':
        freqs, psd = signal.welch(y_new, fs_current)
    else:
        freqs, psd = psd_definition(y_new, fs_current)
    ax_psd.cla()
    ax_psd.grid(True, alpha=0.3)
    ax_psd.plot(freqs, psd, 'r-', linewidth=1.5)
    ax_psd.set_xlabel('Częstotliwość [Hz]')
    ax_psd.set_ylabel('PSD [V²/Hz]')
    ax_psd.set_xlim(0, freqs[-1] if len(freqs) > 0 else 1)
    psd_max = np.max(psd) if len(psd) > 0 and np.max(psd) > 0 else 1
    if psd_scale == 'logarytmiczna':
        ax_psd.set_yscale('log')
        ax_psd.set_ylim(max(psd_max * 1e-6, 1e-12), psd_max * 10)
    else:
        ax_psd.set_yscale('linear')
        ax_psd.set_ylim(0, psd_max * 1.1)
    ax_psd.set_title(f'Gęstość mocy widmowej ({psd_method})')


# Początkowy wykres
y = generate_signal(t, initial_signal_type, initial_freq, initial_amp, initial_phase, initial_impulse_position)
line, = ax.plot(t, y, 'b-', linewidth=2)
ax.set_xlim(0, initial_tmax)
ax.set_ylim(-3, 3)
ax.set_xlabel('Czas [s]')
ax.set_ylabel('Amplituda')
ax.set_title(f'Interaktywny wykres sygnału: {initial_signal_type}')
ax.grid(True, alpha=0.3)

# Inicjalizacja wykresu PSD (redrawn on first update via show_signal_panel)
psd_line = None

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

# --- Panel próbkowania (domyślnie ukryty) ---
ax_fs_sample = plt.axes([0.15, 0.25, 0.50, 0.03])
slider_fs_sample = Slider(ax_fs_sample, 'Częst. próbkowania [Hz]', 1.0, 500.0,
                           valinit=50.0, valstep=1.0)
ax_fs_sample.set_visible(False)

ax_bits = plt.axes([0.15, 0.20, 0.50, 0.03])
slider_bits = Slider(ax_bits, 'Bity kwantyzacji', 1, 16, valinit=8, valstep=1)
ax_bits.set_visible(False)

ax_lp_cutoff = plt.axes([0.15, 0.15, 0.50, 0.03])
slider_lp_cutoff = Slider(ax_lp_cutoff, 'Filtr anty-aliasingowy [Hz]', 0.5, 250.0,
                           valinit=25.0, valstep=0.5)
ax_lp_cutoff.set_visible(False)

ax_recon_method = plt.axes([0.73, 0.02, 0.13, 0.25])
ax_recon_method.set_title('Rekonstrukcja', fontsize=13)
radio_recon = RadioButtons(ax_recon_method, ('brak', 'ZOH', 'liniowa', 'sinc', 'W-S'))
ax_recon_method.set_visible(False)

ax_sampling_view = plt.axes([0.87, 0.02, 0.12, 0.25])
ax_sampling_view.set_title('Widok', fontsize=13)
radio_sampling_view = RadioButtons(ax_sampling_view, ('przebieg', 'widmo', 'błąd'))
ax_sampling_view.set_visible(False)

# --- Przyciski przełączające panele ---
ax_tab_signal = plt.axes([0.73, 0.29, 0.08, 0.04])
btn_tab_signal = Button(ax_tab_signal, 'Sygnał', color='lightblue', hovercolor='deepskyblue')

ax_tab_spectral = plt.axes([0.82, 0.29, 0.08, 0.04])
btn_tab_spectral = Button(ax_tab_spectral, 'Widmo', color='lightgray', hovercolor='silver')

ax_tab_sampling = plt.axes([0.91, 0.29, 0.08, 0.04])
btn_tab_sampling = Button(ax_tab_sampling, 'Próbkowanie', color='lightgray', hovercolor='silver')

# --- Przycisk zapisywania (zawsze widoczny) ---
ax_save_button = plt.axes([0.73, 0.38, 0.10, 0.04])
save_button = Button(ax_save_button, 'Zapisz')

_signal_panel_axes = [ax_freq, ax_amp, ax_phase, ax_tmax, ax_impulse_pos, ax_samples, ax_radio]
_spectral_panel_axes = [ax_psd_method, ax_psd_scale]
_sampling_panel_axes = [ax_fs_sample, ax_bits, ax_lp_cutoff, ax_recon_method, ax_sampling_view]

# Zapamiętaj oryginalne pozycje (przed jakimkolwiek przesunięciem)
_offscreen = [-2.0, -2.0, 0.01, 0.01]
_signal_positions = {a: list(a.get_position().bounds) for a in _signal_panel_axes}
_spectral_positions = {a: list(a.get_position().bounds) for a in _spectral_panel_axes}
_sampling_positions = {a: list(a.get_position().bounds) for a in _sampling_panel_axes}

def _apply_panel(show_list, show_pos):
    all_axes = _signal_panel_axes + _spectral_panel_axes + _sampling_panel_axes
    for a in all_axes:
        a.set_position(_offscreen)
        a.set_visible(False)
    for a in show_list:
        a.set_position(show_pos[a])
        a.set_visible(True)

def _set_tab_colors(active_btn):
    for btn in (btn_tab_signal, btn_tab_spectral, btn_tab_sampling):
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

    if _current_tab == 'sampling':
        update_sampling_plot()
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
btn_tab_signal.on_clicked(show_signal_panel)
btn_tab_spectral.on_clicked(show_spectral_panel)
btn_tab_sampling.on_clicked(show_sampling_panel)

slider_fs_sample.on_changed(update)
slider_bits.on_changed(update)
slider_lp_cutoff.on_changed(update)
radio_recon.on_clicked(update)
radio_sampling_view.on_clicked(update)

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
