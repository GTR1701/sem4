import cv2
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.widgets import RadioButtons, Button
import tkinter as tk
from tkinter import filedialog

filename = "gory.jpg"
current_dir = os.path.dirname(os.path.abspath(__file__))
filepath = os.path.join(current_dir, filename)
image1 = cv2.imread(filepath)

filepath2 = os.path.join(current_dir, 'obraz_kopiowany.png')
cv2.imwrite(filepath2, image1)

# Zmienna przechowująca aktualnie wyświetlany obraz i przestrzeń kolorów
state = {
    'image': image1,
    'color_space': 'RGB',
}

COLOR_SPACES = ['RGB', 'aRGB', 'YCbCr', 'HSL']

X_LABELS = {
    'RGB':   'Wartość piksela (0–255)',
    'aRGB':  'Wartość piksela (0–255)',
    'YCbCr': 'Wartość składowej (0–255)',
    'HSL':   'Wartość składowej (0–255)',
}


def smooth_hist(arr, sigma=2.5):
    """Wygładza histogram filtrem Gaussa (bez zewnętrznych zależności)."""
    k = max(3, int(sigma * 4) | 1)   # nieparzysta liczba próbek
    half = k // 2
    kernel = np.exp(-0.5 * (np.arange(k) - half) ** 2 / sigma ** 2)
    kernel /= kernel.sum()
    return np.convolve(arr, kernel, mode='same')


def get_channels(image_bgr, color_space):
    """Zwraca listę (nazwa, histogram[256], kolor_linii, kolor_fill)."""
    b_ch, g_ch, r_ch = cv2.split(image_bgr)

    def hist256(ch):
        return cv2.calcHist([ch], [0], None, [256], [0, 256]).flatten()

    if color_space == 'RGB':
        return [
            ('Red',   hist256(r_ch), 'tomato',     'red'),
            ('Green', hist256(g_ch), 'limegreen',  'lime'),
            ('Blue',  hist256(b_ch), 'dodgerblue', 'blue'),
        ]

    elif color_space == 'aRGB':
        luma = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
        return [
            ('Red',        hist256(r_ch),   'tomato',     'red'),
            ('Green',      hist256(g_ch),   'limegreen',  'lime'),
            ('Blue',       hist256(b_ch),   'dodgerblue', 'blue'),
            ('Naświetlenie', hist256(luma), 'white',    '#cccccc'),
        ]

    elif color_space == 'YCbCr':
        # Luma (Y) + chroma niebieska (Cb) + chroma czerwona (Cr)
        ycrcb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2YCrCb)
        y_ch  = ycrcb[:, :, 0]
        cr_ch = ycrcb[:, :, 1]
        cb_ch = ycrcb[:, :, 2]
        return [
            ('Y  (jasność)',   hist256(y_ch),  'white',      '#cccccc'),
            ('Cr (czerwień)',  hist256(cr_ch), 'tomato',     'red'),
            ('Cb (błękit)',    hist256(cb_ch), 'dodgerblue', 'blue'),
        ]

    elif color_space == 'HSL':
        hls  = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HLS)
        h_ch = hls[:, :, 0]   # zakres 0–179 (OpenCV)
        l_ch = hls[:, :, 1]   # 0–255
        s_ch = hls[:, :, 2]   # 0–255

        # Hue ma tylko 180 unikalnych wartości – interpolujemy do 256 kubełków,
        # żeby uniknąć poszarpanego wykresu
        h_raw = cv2.calcHist([h_ch], [0], None, [180], [0, 180]).flatten()
        h_hist = np.interp(np.linspace(0, 179, 256), np.arange(180), h_raw)

        return [
            ('Hue',        h_hist,        'gold',        'orange'),
            ('Saturation', hist256(s_ch), 'deepskyblue', 'steelblue'),
            ('Lightness',  hist256(l_ch), 'white',       '#cccccc'),
        ]

    else:
        raise ValueError(f"Nieznana przestrzeń kolorów: {color_space}")


def redraw_histogram(ax, image_bgr, color_space):
    ax.cla()
    ax.set_facecolor('#1a1a1a')

    channels = get_channels(image_bgr, color_space)
    x = np.arange(256)

    max_val = max(ch[1].max() for ch in channels) or 1.0
    normalized = [
        (name, smooth_hist(vals / max_val), line_c, fill_c)
        for name, vals, line_c, fill_c in channels
    ]

    for name, vals, line_c, fill_c in normalized:
        ax.fill_between(x, vals, alpha=0.40, color=fill_c, linewidth=0)
        ax.plot(x, vals, color=line_c, linewidth=1.0, alpha=0.95)

    ax.set_xlim(0, 255)
    ax.set_ylim(0, 1.08)
    ax.tick_params(colors='gray', labelsize=8)
    for spine in ax.spines.values():
        spine.set_edgecolor('#444444')
    ax.grid(True, color='#2a2a2a', linewidth=0.6, linestyle='--')

    patches = [mpatches.Patch(color=line_c, label=name)
               for name, _, line_c, _ in normalized]
    ax.legend(handles=patches, loc='upper left', facecolor='#2a2a2a',
              edgecolor='#555555', labelcolor='white', fontsize=9)

    ax.set_title(f'Histogram kolorów – {color_space}', color='white', fontsize=11, pad=6)
    ax.set_xlabel(X_LABELS[color_space], color='gray', fontsize=8)
    ax.set_ylabel('Częstotliwość (norm.)', color='gray', fontsize=8)

fig = plt.figure(figsize=(15, 8), facecolor='#1a1a1a')

# Siatka: 2 wiersze × 2 kolumny; prawa kolumna zawiera radio + przycisk
gs = fig.add_gridspec(
    2, 2,
    width_ratios=[5.2, 1],
    height_ratios=[1.1, 1],
    hspace=0.50,
    wspace=0.18,
    left=0.07, right=0.97,
    top=0.9, bottom=0.10,
)

ax_img  = fig.add_subplot(gs[0, 0])
ax_hist = fig.add_subplot(gs[1, 0])

# Prawa kolumna: radio (górne 80%) + przycisk (dolne 20%)
ax_rb  = fig.add_axes([0.875, 0.25, 0.105, 0.60], facecolor='#2a2a2a')
ax_btn = fig.add_axes([0.860, 0.10, 0.125, 0.08])

# --- Obraz ---
image_rgb = cv2.cvtColor(state['image'], cv2.COLOR_BGR2RGB)
ax_img.imshow(image_rgb)
ax_img.set_title(
    f'Załadowany obraz: {os.path.basename(filepath)}',
    color='white', fontsize=10, pad=6,
)
ax_img.axis('off')

# --- Histogram (domyślnie RGB) ---
redraw_histogram(ax_hist, state['image'], state['color_space'])

# --- Radio buttons ---
for spine in ax_rb.spines.values():
    spine.set_edgecolor('#555555')

radio = RadioButtons(ax_rb, COLOR_SPACES, activecolor='dodgerblue')
for lbl in radio.labels:
    lbl.set_color('white')
    lbl.set_fontsize(11)
ax_rb.set_title('Przestrzeń\nkolorów', color='white', fontsize=10, pad=10)

# --- Przycisk wyboru pliku ---
btn = Button(ax_btn, 'Wybierz obraz', color='#3a3a3a', hovercolor='#555555')
btn.label.set_color('white')
btn.label.set_fontsize(9)


def on_open(_event):
    # Ukryj okno matplotlib, otwórz dialog, przywróć focus
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    path = filedialog.askopenfilename(
        title='Wybierz obraz',
        filetypes=[
            ('Obrazy', '*.jpg *.jpeg *.png *.bmp *.tiff *.tif *.webp'),
            ('Wszystkie pliki', '*.*'),
        ],
    )
    root.destroy()

    if not path:
        return

    img = cv2.imread(path)
    if img is None:
        return

    state['image'] = img
    # Zapisz kopię PNG
    cv2.imwrite(os.path.join(current_dir, 'obraz_kopiowany.png'), img)

    # Odśwież podgląd
    ax_img.cla()
    ax_img.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    ax_img.set_title(
        f'Załadowany obraz: {os.path.basename(path)}',
        color='white', fontsize=10, pad=6,
    )
    ax_img.axis('off')

    # Odśwież histogram
    redraw_histogram(ax_hist, img, state['color_space'])
    fig.canvas.draw_idle()


def on_radio(label):
    state['color_space'] = label
    redraw_histogram(ax_hist, state['image'], label)
    fig.canvas.draw_idle()


btn.on_clicked(on_open)
radio.on_clicked(on_radio)
plt.show()
