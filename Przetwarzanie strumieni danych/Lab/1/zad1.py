from scipy import signal
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, RadioButtons, Button
import pandas as pd
import os

#Zad 1

# Konfiguracja wykresu
fig, ax = plt.subplots(figsize=(12, 8))
# right=0.72 zostawia miejsce po prawej na RadioButtons i przycisk Save
plt.subplots_adjust(left=0.1, bottom=0.35, right=0.72, top=0.95)

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

# Slidery
ax_freq = plt.axes([0.15, 0.25, 0.5, 0.03])
slider_freq = Slider(ax_freq, 'Częstotliwość', 0.1, 10.0, valinit=initial_freq, valstep=0.1)

ax_amp = plt.axes([0.15, 0.20, 0.5, 0.03])
slider_amp = Slider(ax_amp, 'Amplituda', 0.1, 3.0, valinit=initial_amp, valstep=0.1)

ax_phase = plt.axes([0.15, 0.15, 0.5, 0.03])
slider_phase = Slider(ax_phase, 'Faza', 0, 2*np.pi, valinit=initial_phase, valstep=0.1)

ax_tmax = plt.axes([0.15, 0.10, 0.5, 0.03]) 
slider_tmax = Slider(ax_tmax, 'Zakres czasu', 1.0, 20.0, valinit=initial_tmax, valstep=0.5)

ax_impulse_pos = plt.axes([0.15, 0.05, 0.5, 0.03])
slider_impulse_pos = Slider(ax_impulse_pos, 'Pozycja impulsu', 0.0, initial_tmax, valinit=initial_impulse_position, valstep=0.1)

ax_samples = plt.axes([0.15, 0.00, 0.5, 0.03])
slider_samples = Slider(ax_samples, 'Liczba sampli', 100, 5000, valinit=initial_samples, valstep=100)

# Radiobuttons dla typu sygnału
ax_radio = plt.axes([0.75, 0.05, 0.2, 0.3])
radio = RadioButtons(ax_radio, ('sinus', 'cosinus', 'prostokątny', 'piłokształtny', 'chirp', 'superpozycja', 'impuls jednostkowy', 'trójkątny', 'szum biały'))

# Przycisk do zapisywania
ax_save_button = plt.axes([0.75, 0.38, 0.1, 0.05])
save_button = Button(ax_save_button, 'Zapisz')

# Funkcja do ładowania parametrów przy zmianie typu sygnału
def on_signal_type_change(label):
    """Ładuje parametry z pliku przy zmianie typu sygnału"""
    loaded_params = load_signal_from_file(label)
    
    if loaded_params:
        # Aktualizuj slidery z załadowanymi parametrami
        slider_freq.set_val(loaded_params['freq'])
        slider_amp.set_val(loaded_params['amp'])
        slider_phase.set_val(loaded_params['phase'])
        slider_tmax.set_val(loaded_params['tmax'])
        slider_impulse_pos.set_val(loaded_params['impulse_pos'])
        print(f"Załadowano parametry dla sygnału: {label}")
    else:
        print(f"Brak zapisanego pliku dla sygnału: {label}, używam bieżących parametrów")
    
    # Wywołaj standardową funkcję update
    update(None)

# Funkcja update
def update(val):
    freq = slider_freq.val
    amp = slider_amp.val  
    phase = slider_phase.val
    tmax = slider_tmax.val
    impulse_pos = slider_impulse_pos.val
    signal_type = radio.value_selected
    
    # Aktualizuj maksymalną wartość suwaka pozycji impulsu
    slider_impulse_pos.valmax = tmax
    if impulse_pos > tmax:
        slider_impulse_pos.set_val(tmax)
        impulse_pos = tmax
    
    # Aktualizuj oś czasu
    samples = int(slider_samples.val)
    t_new = np.linspace(0, tmax, samples)
    
    # Generuj nowy sygnał  
    y_new = generate_signal(t_new, signal_type, freq, amp, phase, impulse_pos)
    
    # Aktualizuj wykres
    line.set_data(t_new, y_new)
    ax.set_xlim(0, tmax)
    
    # Dla impulsu jednostkowego ustaw odpowiednie granice Y
    if signal_type == 'impuls jednostkowy':
        ax.set_ylim(-0.1*amp, amp*1.2)
    else:
        ax.set_ylim(-amp*2.5, amp*2.5)
    
    ax.set_title(f'Wykres sygnału: {signal_type}')
    
    fig.canvas.draw_idle()

# Podłączenie funkcji update do sliderów
slider_freq.on_changed(update)
slider_amp.on_changed(update)
slider_phase.on_changed(update)
slider_tmax.on_changed(update)
slider_impulse_pos.on_changed(update)
slider_samples.on_changed(update)

# Podłączenie radiobuttons do funkcji ładującej parametry
radio.on_clicked(on_signal_type_change)

# Podłączenie przycisku do funkcji zapisywania
save_button.on_clicked(lambda x: save_all())

plt.show()
