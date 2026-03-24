import cv2
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.widgets import RadioButtons, Button, Slider, TextBox
import tkinter as tk
from tkinter import filedialog

filename = "gory.jpg"
current_dir = os.path.dirname(os.path.abspath(__file__))
filepath = os.path.join(current_dir, filename)
image1 = cv2.imread(filepath)

filepath2 = os.path.join(current_dir, 'obraz_kopiowany.png')
cv2.imwrite(filepath2, image1)

# Zmienna przechowująca stan aplikacji
state = {
    'image': image1,
    'color_space': 'RGB',
    'noise': False,         # czy szum sól i pieprz jest włączony
    'noise_salt': 0.02,     # odsetek pikseli soli (2 %)
    'noise_pepper': 0.02,   # odsetek pikseli pieprzu (2 %)
    'rotation': 0,          # kąt obrotu w stopniach
}

COLOR_SPACES = ['RGB', 'aRGB', 'YCbCr', 'HSL']

X_LABELS = {
    'RGB':   'Wartość piksela (0–255)',
    'aRGB':  'Wartość piksela (0–255)',
    'YCbCr': 'Wartość składowej (0–255)',
    'HSL':   'Wartość składowej (0–255)',
}

def add_salt_pepper(image_bgr, salt_amount=0.02, pepper_amount=0.02):
    """Nakłada szum sól i pieprz – nie modyfikuje oryginału."""
    out = image_bgr.copy()
    total = image_bgr.size // image_bgr.shape[2]   # liczba pikseli
    rng = np.random.default_rng(seed=0)            # deterministyczny szum
    # Sól (białe piksele)
    n_salt = int(salt_amount * total)
    rows = rng.integers(0, image_bgr.shape[0], n_salt)
    cols = rng.integers(0, image_bgr.shape[1], n_salt)
    out[rows, cols] = 255
    # Pieprz (czarne piksele)
    n_pepper = int(pepper_amount * total)
    rows = rng.integers(0, image_bgr.shape[0], n_pepper)
    cols = rng.integers(0, image_bgr.shape[1], n_pepper)
    out[rows, cols] = 0
    return out

def rotate_image(image_bgr, angle):
    """Obraca obraz o podany kąt (stopnie, CCW), rozszerza canvas."""
    if angle == 0:
        return image_bgr
    h, w = image_bgr.shape[:2]
    cx, cy = w / 2.0, h / 2.0
    M = cv2.getRotationMatrix2D((cx, cy), angle, 1.0)
    cos_a = abs(M[0, 0])
    sin_a = abs(M[0, 1])
    new_w = int(h * sin_a + w * cos_a)
    new_h = int(h * cos_a + w * sin_a)
    M[0, 2] += new_w / 2.0 - cx
    M[1, 2] += new_h / 2.0 - cy
    return cv2.warpAffine(image_bgr, M, (new_w, new_h), borderValue=(0, 0, 0))


def current_display_image():
    """Zwraca obraz do wyświetlenia (obrót → szum)."""
    img = rotate_image(state['image'], state['rotation'])
    if state['noise']:
        img = add_salt_pepper(img, state['noise_salt'], state['noise_pepper'])
    return img


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
        (name, vals / max_val, line_c, fill_c)
        for name, vals, line_c, fill_c in channels
    ]

    for name, vals, line_c, fill_c in normalized:
        ax.bar(x, vals, width=1.0, alpha=0.55, color=fill_c, linewidth=0)
        ax.step(x, vals, where='mid', color=line_c, linewidth=0.8, alpha=0.95)

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

fig = plt.figure(figsize=(16, 9), facecolor='#1a1a1a')

# Wszystkie osie pozycjonowane ręcznie [left, bottom, width, height]
# Lewa kolumna (szeroka): obraz | suwak | histogram
# Prawa kolumna (wąska):  radio | przyciski
ax_img    = fig.add_axes([0.05, 0.44, 0.78, 0.52])               # duży podgląd
ax_slider = fig.add_axes([0.05, 0.36, 0.78, 0.04],               # suwak obrotu
                         facecolor='#2a2a2a')
ax_hist   = fig.add_axes([0.05, 0.07, 0.78, 0.26])               # histogram
ax_rb     = fig.add_axes([0.867, 0.35, 0.115, 0.58],             # radio
                         facecolor='#2a2a2a')
ax_btn          = fig.add_axes([0.855, 0.22, 0.135, 0.07])       # wybierz obraz
ax_btn_snp      = fig.add_axes([0.855, 0.12, 0.135, 0.07])       # szum S&P
ax_slider_salt  = fig.add_axes([0.855, 0.075, 0.135, 0.033],     # suwak soli
                               facecolor='#2a2a2a')
ax_slider_pepper = fig.add_axes([0.855, 0.028, 0.135, 0.033],    # suwak pieprzu
                                facecolor='#2a2a2a')
ax_tb_save  = fig.add_axes([0.05, 0.010, 0.52, 0.052])           # pole nazwy pliku
ax_btn_save = fig.add_axes([0.60, 0.008, 0.23, 0.056])           # przycisk zapisu

def redraw_image(title_path=None):
    ax_img.cla()
    ax_img.imshow(cv2.cvtColor(current_display_image(), cv2.COLOR_BGR2RGB))
    name = title_path or filepath
    tags = []
    if state['noise']:
        tags.append('szum S&P')
    if state['rotation'] != 0:
        tags.append(f'{state["rotation"]:+.0f}°')
    tag_str = '  [' + ', '.join(tags) + ']' if tags else ''
    ax_img.set_title(
        f'Załadowany obraz: {os.path.basename(name)}{tag_str}',
        color='white', fontsize=10, pad=6,
    )
    ax_img.axis('off')


# --- Obraz ---
redraw_image()

# --- Histogram (domyślnie RGB) ---
redraw_histogram(ax_hist, current_display_image(), state['color_space'])

# --- Suwak obrotu ---
rotation_slider = Slider(
    ax_slider, 'Obrót', -180, 180,
    valinit=0, valstep=1,
    color='dodgerblue',
)
rotation_slider.label.set_color('white')
rotation_slider.valtext.set_color('white')
for spine in ax_slider.spines.values():
    spine.set_edgecolor('#555555')

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

# --- Toggle szumu sól i pieprz ---
btn_snp = Button(ax_btn_snp, 'Szum S&P: WYŁ', color='#3a3a3a', hovercolor='#555555')
btn_snp.label.set_color('#aaaaaa')
btn_snp.label.set_fontsize(9)

# --- Suwak soli ---
salt_slider = Slider(
    ax_slider_salt, 'Sól', 0.0, 0.2,
    valinit=0.02, valstep=0.001,
    color='white',
)
salt_slider.label.set_color('white')
salt_slider.label.set_fontsize(8)
salt_slider.valtext.set_color('white')
salt_slider.valtext.set_fontsize(8)
for spine in ax_slider_salt.spines.values():
    spine.set_edgecolor('#555555')

# --- Suwak pieprzu ---
pepper_slider = Slider(
    ax_slider_pepper, 'Pieprz', 0.0, 0.2,
    valinit=0.02, valstep=0.001,
    color='#444444',
)
pepper_slider.label.set_color('white')
pepper_slider.label.set_fontsize(8)
pepper_slider.valtext.set_color('white')
pepper_slider.valtext.set_fontsize(8)
for spine in ax_slider_pepper.spines.values():
    spine.set_edgecolor('#555555')


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
    state['_last_path'] = path
    # Zapisz kopię PNG
    cv2.imwrite(os.path.join(current_dir, 'obraz_kopiowany.png'), img)

    # Odśwież podgląd i histogram
    redraw_image(path)
    redraw_histogram(ax_hist, current_display_image(), state['color_space'])
    fig.canvas.draw_idle()


def on_radio(label):
    state['color_space'] = label
    redraw_histogram(ax_hist, current_display_image(), label)
    fig.canvas.draw_idle()


def on_toggle_snp(_event):
    state['noise'] = not state['noise']
    if state['noise']:
        btn_snp.label.set_text('Szum S&P: WŁ')
        btn_snp.label.set_color('gold')
        btn_snp.ax.set_facecolor('#4a3a00')
    else:
        btn_snp.label.set_text('Szum S&P: WYŁ')
        btn_snp.label.set_color('#aaaaaa')
        btn_snp.ax.set_facecolor('#3a3a3a')
    redraw_image(state.get('_last_path'))
    redraw_histogram(ax_hist, current_display_image(), state['color_space'])
    fig.canvas.draw_idle()


def on_rotation(val):
    state['rotation'] = int(val)
    redraw_image(state.get('_last_path'))
    redraw_histogram(ax_hist, current_display_image(), state['color_space'])
    fig.canvas.draw_idle()


def on_salt(val):
    state['noise_salt'] = val
    if state['noise']:
        redraw_image(state.get('_last_path'))
        redraw_histogram(ax_hist, current_display_image(), state['color_space'])
        fig.canvas.draw_idle()


def on_pepper(val):
    state['noise_pepper'] = val
    if state['noise']:
        redraw_image(state.get('_last_path'))
        redraw_histogram(ax_hist, current_display_image(), state['color_space'])
        fig.canvas.draw_idle()


# --- Pole nazwy pliku ---
tb_save = TextBox(ax_tb_save, 'Plik: ', initial='output.png',
                  color='#2a2a2a', hovercolor='#3a3a3a')
tb_save.label.set_color('white')
tb_save.label.set_fontsize(12)
tb_save.text_disp.set_color('white')
tb_save.text_disp.set_fontsize(13)
for spine in ax_tb_save.spines.values():
    spine.set_edgecolor('#555555')

# --- Przycisk zapisu ---
btn_save = Button(ax_btn_save, 'Zapisz obraz', color='#1a3a1a', hovercolor='#2a5a2a')
btn_save.label.set_color('lightgreen')
btn_save.label.set_fontsize(9)


def on_save(_event):
    name = tb_save.text.strip() or 'output.png'
    # Zapewnij rozszerzenie
    if not os.path.splitext(name)[1]:
        name += '.png'
    save_dir = os.path.dirname(state.get('_last_path', filepath))
    save_path = os.path.join(save_dir, name)
    img_to_save = current_display_image()
    cv2.imwrite(save_path, img_to_save)
    fig.canvas.draw_idle()


btn_save.on_clicked(on_save)

btn.on_clicked(on_open)
radio.on_clicked(on_radio)
btn_snp.on_clicked(on_toggle_snp)
rotation_slider.on_changed(on_rotation)
salt_slider.on_changed(on_salt)
pepper_slider.on_changed(on_pepper)

fig.canvas.manager.set_window_title('Analiza histogramu obrazu')
plt.show()
