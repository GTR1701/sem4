import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from scipy.stats import rice, poisson, rayleigh as rayleigh_dist

N = 10000
BINS = 60

# Parametry początkowe
NU0, SIGMA_R0 = 3.0, 1.0
LAM0 = 10.0
SIGMA_RAY0 = 1.5


def gen_rician(nu, sigma, n=N):
    X = np.random.normal(nu, sigma, n)
    Y = np.random.normal(0.0, sigma, n)
    return np.sqrt(X**2 + Y**2)


def gen_poisson(lam, n=N):
    return np.random.poisson(lam, n)


def gen_rayleigh(sigma, n=N):
    return np.random.rayleigh(sigma, n)


fig = plt.figure(figsize=(16, 8))
fig.subplots_adjust(top=0.90, bottom=0.38, left=0.06, right=0.97, wspace=0.35)

ax1 = fig.add_subplot(1, 3, 1)
ax2 = fig.add_subplot(1, 3, 2)
ax3 = fig.add_subplot(1, 3, 3)


def plot_all(nu, sigma_r, lam, sigma_ray):
    ax1.cla()
    ax2.cla()
    ax3.cla()

    # --- Szum Riciana ---
    r_data = gen_rician(nu, sigma_r)
    ax1.hist(r_data, bins=BINS, density=True, color='steelblue', alpha=0.75,
             edgecolor='white', linewidth=0.5, label='Histogram')
    x_r = np.linspace(0, r_data.max() * 1.1, 400)
    b = nu / sigma_r if sigma_r > 0 else 0.0
    ax1.plot(x_r, rice.pdf(x_r, b=b, scale=sigma_r), 'r-', lw=2, label='PDF')
    ax1.set_title('Szum Riciana', fontsize=11, fontweight='bold')
    ax1.set_xlabel('Amplituda')
    ax1.set_ylabel('Gęstość prawdopodobieństwa')
    ax1.legend(fontsize=8, loc='upper right')
    ax1.text(0.97, 0.95, f'ν = {nu:.2f}\nσ = {sigma_r:.2f}',
             transform=ax1.transAxes, ha='right', va='top', fontsize=8,
             bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow', alpha=0.8))

    # --- Szum Poissona ---
    p_data = gen_poisson(lam)
    std_p = max(1, int(np.sqrt(lam)))
    p_min = max(0, int(lam) - 4 * std_p)
    p_max = int(lam) + 5 * std_p + 1
    bins_p = np.arange(p_min, p_max + 1) - 0.5
    ax2.hist(p_data, bins=bins_p, density=True, color='darkorange', alpha=0.75,
             edgecolor='white', linewidth=0.5, label='Histogram')
    k = np.arange(p_min, p_max)
    pmf_vals = poisson.pmf(k, lam)
    ax2.vlines(k, 0, pmf_vals, colors='red', lw=1.5, alpha=0.8)
    ax2.plot(k, pmf_vals, 'r.', markersize=5, label='PMF', zorder=5)
    ax2.set_title('Szum Poissona', fontsize=11, fontweight='bold')
    ax2.set_xlabel('Liczba zdarzeń')
    ax2.set_ylabel('Prawdopodobieństwo')
    ax2.legend(fontsize=8, loc='upper right')
    ax2.text(0.97, 0.95, f'λ = {lam:.1f}',
             transform=ax2.transAxes, ha='right', va='top', fontsize=8,
             bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow', alpha=0.8))

    # --- Szum Rayleigha ---
    ray_data = gen_rayleigh(sigma_ray)
    ax3.hist(ray_data, bins=BINS, density=True, color='forestgreen', alpha=0.75,
             edgecolor='white', linewidth=0.5, label='Histogram')
    x_ray = np.linspace(0, ray_data.max() * 1.1, 400)
    ax3.plot(x_ray, rayleigh_dist.pdf(x_ray, scale=sigma_ray), 'r-', lw=2, label='PDF')
    ax3.set_title('Szum Rayleigha', fontsize=11, fontweight='bold')
    ax3.set_xlabel('Amplituda')
    ax3.set_ylabel('Gęstość prawdopodobieństwa')
    ax3.legend(fontsize=8, loc='upper right')
    ax3.text(0.97, 0.95, f'σ = {sigma_ray:.2f}',
             transform=ax3.transAxes, ha='right', va='top', fontsize=8,
             bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow', alpha=0.8))

    fig.canvas.draw_idle()


# Pierwsze rysowanie
plot_all(NU0, SIGMA_R0, LAM0, SIGMA_RAY0)

# ---- Suwaki ----
# Rician – 2 suwaki: ν i σ
ax_nu     = fig.add_axes([0.06,  0.24, 0.26, 0.025])
ax_sig_r  = fig.add_axes([0.06,  0.18, 0.26, 0.025])
# Poisson – 1 suwak: λ
ax_lam    = fig.add_axes([0.395, 0.21, 0.245, 0.025])
# Rayleigh – 1 suwak: σ
ax_sig_ray = fig.add_axes([0.715, 0.21, 0.245, 0.025])

sl_nu      = Slider(ax_nu,      'ν  (nu)',      0.0,  10.0, valinit=NU0,        valstep=0.1,  color='steelblue')
sl_sig_r   = Slider(ax_sig_r,   'σ  (sigma)',   0.1,   5.0, valinit=SIGMA_R0,   valstep=0.05, color='steelblue')
sl_lam     = Slider(ax_lam,     'λ  (lambda)',  0.5,  50.0, valinit=LAM0,       valstep=0.5,  color='darkorange')
sl_sig_ray = Slider(ax_sig_ray, 'σ  (sigma)',   0.1,   5.0, valinit=SIGMA_RAY0, valstep=0.05, color='forestgreen')

# Etykiety grup suwaków
fig.text(0.19,  0.29,  'Parametry – Rician',   ha='center', fontsize=9, fontweight='bold', color='steelblue')
fig.text(0.518, 0.255, 'Parametry – Poisson',  ha='center', fontsize=9, fontweight='bold', color='darkorange')
fig.text(0.838, 0.255, 'Parametry – Rayleigh', ha='center', fontsize=9, fontweight='bold', color='forestgreen')


def update(val):
    plot_all(sl_nu.val, sl_sig_r.val, sl_lam.val, sl_sig_ray.val)


sl_nu.on_changed(update)
sl_sig_r.on_changed(update)
sl_lam.on_changed(update)
sl_sig_ray.on_changed(update)

fig.suptitle('Generatory szumów: Rician · Poisson · Rayleigh', fontsize=13, fontweight='bold')
fig.canvas.manager.set_window_title('Szumy: Rician · Poisson · Rayleigh')
plt.show()
