from scipy import signal
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, RadioButtons
import pandas as pd
import os

#Zad 1
# a)

t = np.linspace(0, 5, 1000)
sin_y = np.sin(2 * np.pi * 1 * t)

plt.subplots_adjust(hspace=1)
plt.subplot(3, 2, 1)
plt.plot(t, sin_y, label='sinus')
plt.title('Sinus')

# b)

square_y = signal.square(2 * np.pi * 1 * t)

plt.subplot(3, 2, 2)
plt.plot(t, square_y, label='prostokątny')
plt.title('Prostokątny')

# c)
sawtooth_y = signal.sawtooth(2 * np.pi * 1 * t)

plt.subplot(3, 2, 3)
plt.plot(t, sawtooth_y, label='piłokształtny')
plt.title('Piłokształtny')

# d)
chirp_y = signal.chirp(t, f0=1, f1=10, t1=5, method='linear')

plt.subplot(3, 2, 4)
plt.plot(t, chirp_y, label='chirp')
plt.title('Świergotliwy')

# e)

cos_y = np.cos(2 * np.pi * 1 * t)

plt.subplot(3, 2, 5)
plt.plot(t, cos_y, label='cosinus')
plt.plot(t, sin_y, label='sinus')
plt.title('Cosinus i Sinus')
plt.legend()

# f)

jednostkowy_y = signal.unit_impulse(1000, 500)

plt.subplot(3, 2, 6)
plt.plot(t, jednostkowy_y, label='impuls jednostkowy')
plt.title('Impuls jednostkowy')
plt.show()

# Konfiguracja wykresu
fig, ax = plt.subplots(figsize=(12, 8))
plt.subplots_adjust(left=0.1, bottom=0.35)

# Parametry początkowe
initial_freq = 1.0
initial_amp = 1.0
initial_phase = 0.0
initial_tmax = 5.0
initial_signal_type = 'sinus'

# Oś czasu
t = np.linspace(0, initial_tmax, 1000)

# Funkcja do generowania sygnału
def generate_signal(t, signal_type, freq, amp, phase):
    if signal_type == 'sinus':
        return amp * np.sin(2 * np.pi * freq * t + phase)
    elif signal_type == 'cosinus':
        return amp * np.cos(2 * np.pi * freq * t + phase)
    elif signal_type == 'prostokątny':
        return amp * signal.square(2 * np.pi * freq * t + phase)
    elif signal_type == 'piłokształtny':
        return amp * signal.sawtooth(2 * np.pi * freq * t + phase)
    elif signal_type == 'chirp':
        return amp * signal.chirp(t, f0=freq, f1=freq*10, t1=t[-1], method='linear')
    elif signal_type == 'superpozycja':
        sin_part = amp * np.sin(2 * np.pi * freq * t + phase)
        cos_part = amp * np.cos(2 * np.pi * freq * 1.5 * t + phase)
        return sin_part + cos_part

def save_signals_to_csv(filename):
    signal_types = ['sinus', 'cosinus', 'prostokątny', 'piłokształtny', 'chirp', 'superpozycja']
    data = {'Czas': t}
    
    for st in signal_types:
        data[st] = generate_signal(t, st, initial_freq, initial_amp, initial_phase)
    
    df = pd.DataFrame(data)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(current_dir, filename)
    df.to_csv(filepath, index=False)

# Początkowy wykres
y = generate_signal(t, initial_signal_type, initial_freq, initial_amp, initial_phase)
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

# Radiobuttons dla typu sygnału
ax_radio = plt.axes([0.75, 0.1, 0.2, 0.25])
radio = RadioButtons(ax_radio, ('sinus', 'cosinus', 'prostokątny', 'piłokształtny', 'chirp', 'superpozycja'))

# Funkcja update
def update(val):
    freq = slider_freq.val
    amp = slider_amp.val  
    phase = slider_phase.val
    tmax = slider_tmax.val
    signal_type = radio.value_selected
    
    # Aktualizuj oś czasu
    t_new = np.linspace(0, tmax, 1000)
    
    # Generuj nowy sygnał  
    y_new = generate_signal(t_new, signal_type, freq, amp, phase)
    
    # Aktualizuj wykres
    line.set_data(t_new, y_new)
    ax.set_xlim(0, tmax)
    ax.set_ylim(-amp*2.5, amp*2.5)
    ax.set_title(f'Interaktywny wykres sygnału: {signal_type}')
    
    fig.canvas.draw_idle()

# Podłączenie funkcji update do sliderów i radiobuttons
slider_freq.on_changed(update)
slider_amp.on_changed(update)
slider_phase.on_changed(update)
slider_tmax.on_changed(update)
radio.on_clicked(update)

plt.show()

save_signals_to_csv('sygnalyZad1.csv')