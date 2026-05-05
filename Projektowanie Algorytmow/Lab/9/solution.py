import math
import time


def dft(samples):
    N = len(samples)
    result = []

    for k in range(N):
        real = 0
        imag = 0
        for n in range(N):
            angle = -2 * math.pi * k * n / N
            real += samples[n] * math.cos(angle)
            imag += samples[n] * math.sin(angle)
        result.append(complex(real, imag))

    return result


def generate_signal(N):
    signal = []
    for n in range(N):
        signal.append(math.sin(2 * math.pi * n / N))
    return signal


sizes = [128, 512, 2048]

for N in sizes:
    signal = generate_signal(N)

    start = time.time()
    spectrum = dft(signal)
    end = time.time()

    elapsed = end - start
    print(f"N = {N:5d}  czas: {elapsed:.4f} s")

# Zad 2
def fft(samples):
    N = len(samples)

    # przypadek bazowy
    if N == 1:
        return [complex(samples[0])]

    # rozkład na parzyste i nieparzyste indeksy
    even = fft(samples[0::2])
    odd  = fft(samples[1::2])

    result = [complex(0)] * N

    for k in range(N // 2):
        # pierwiastek jednostkowy: W = e^(-2*pi*i*k/N)
        angle = -2 * math.pi * k / N
        W = complex(math.cos(angle), math.sin(angle))

        twiddle = W * odd[k]

        result[k]           = even[k] + twiddle
        result[k + N // 2]  = even[k] - twiddle

    return result


# Pomiar czasu FFT
print()
for N in sizes:
    signal = generate_signal(N)

    start = time.time()
    spectrum_fft = fft(signal)
    end = time.time()

    elapsed = end - start
    print(f"N = {N:5d}  czas FFT: {elapsed:.4f} s")


# Sprawdzenie zgodności DFT vs FFT (dla N=128)
print()
N = 128
signal = generate_signal(N)
spectrum_dft = dft(signal)
spectrum_fft = fft(signal)

max_error = 0
for k in range(N):
    diff = abs(spectrum_dft[k] - spectrum_fft[k])
    if diff > max_error:
        max_error = diff

print(f"Maksymalna różnica DFT vs FFT (N={N}): {max_error:.2e}")


#Zad 3
def ifft(samples):
    N = len(samples)

    # IFFT = sprzężenie -> FFT -> sprzężenie -> podziel przez N
    conjugated = [complex(x.real, -x.imag) for x in samples]
    transformed = fft(conjugated)
    result = [complex(x.real / N, -x.imag / N) for x in transformed]

    return result


def next_power_of_two(n):
    p = 1
    while p < n:
        p *= 2
    return p


def poly_multiply_fft(a, b):
    result_len = len(a) + len(b) - 1
    N = next_power_of_two(result_len)

    # wyzerowanie (padding) do długości N
    a_padded = list(a) + [0] * (N - len(a))
    b_padded = list(b) + [0] * (N - len(b))

    # FFT obu wielomianów
    fa = fft(a_padded)
    fb = fft(b_padded)

    # mnożenie punkt po punkcie
    fc = [fa[i] * fb[i] for i in range(N)]

    # odwrotna FFT
    result_full = ifft(fc)

    # zaokrąglenie i obcięcie do właściwej długości
    result = [round(result_full[i].real) for i in range(result_len)]

    return result


def poly_multiply_naive(a, b):
    result = [0] * (len(a) + len(b) - 1)
    for i in range(len(a)):
        for j in range(len(b)):
            result[i + j] += a[i] * b[j]
    return result


def generate_poly(degree):
    poly = []
    for i in range(degree + 1):
        poly.append(i + 1)
    return poly


# Sprawdzenie poprawności dla małego przykładu
# (2 + 3x) * (1 + x) = 2 + 5x + 3x^2
a = [2, 3]
b = [1, 1]
print()
print(f"Test: {a} * {b}")
print(f"  naive: {poly_multiply_naive(a, b)}")
print(f"  FFT:   {poly_multiply_fft(a, b)}")

# Porównanie czasów
print()
degrees = [20, 100, 300, 1000, 5000]

for deg in degrees:
    a = generate_poly(deg)
    b = generate_poly(deg)

    start = time.time()
    poly_multiply_naive(a, b)
    t_naive = time.time() - start

    start = time.time()
    poly_multiply_fft(a, b)
    t_fft = time.time() - start

    print(f"stopień {deg:4d}  naive: {t_naive:.5f} s   FFT: {t_fft:.5f} s")

# Zad 4
import matplotlib.pyplot as plt

# --- pomiar DFT i FFT (transformacja sygnału) ---
signal_sizes = [64, 128, 256, 512, 1024, 2048]
times_dft = []
times_fft = []

for N in signal_sizes:
    signal = generate_signal(N)

    start = time.time()
    dft(signal)
    times_dft.append(time.time() - start)

    start = time.time()
    fft(signal)
    times_fft.append(time.time() - start)

# --- pomiar naiwnego mnożenia i FFT-mnożenia wielomianów ---
poly_sizes = [32, 64, 128, 256, 512, 1024]
times_poly_naive = []
times_poly_fft = []

for deg in poly_sizes:
    a = generate_poly(deg)
    b = generate_poly(deg)

    start = time.time()
    poly_multiply_naive(a, b)
    times_poly_naive.append(time.time() - start)

    start = time.time()
    poly_multiply_fft(a, b)
    times_poly_fft.append(time.time() - start)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

ax1.plot(signal_sizes, times_dft,       marker='o', label='DFT - O(n²)')
ax1.plot(signal_sizes, times_fft,       marker='s', label='FFT - O(n log n)')
ax1.set_title('Transformacja sygnału: DFT vs FFT')
ax1.set_xlabel('Rozmiar sygnału N')
ax1.set_ylabel('Czas [s]')
ax1.legend()
ax1.grid(True)

ax2.plot(poly_sizes, times_poly_naive,  marker='o', label='Mnożenie naiwne - O(n²)')
ax2.plot(poly_sizes, times_poly_fft,    marker='s', label='Mnożenie FFT - O(n log n)')
ax2.set_title('Mnożenie wielomianów: naiwne vs FFT')
ax2.set_xlabel('Stopień wielomianu')
ax2.set_ylabel('Czas [s]')
ax2.legend()
ax2.grid(True)

plt.tight_layout()
plt.show()

# Algorytmy O(n²) (DFT, naiwne mnożenie) rosną kwadratowo - podwojenie N
# czterokrotnie wydłuża czas. Algorytmy O(n log n) (FFT, mnożenie przez FFT)
# rosną znacznie wolniej: podwojenie N tylko nieco ponad dwukrotnie zwiększa
# czas. Dla małych N różnica jest niewidoczna lub FFT jest nawet wolniejsze
# (narzut rekurencji), ale dla dużych N przewaga FFT jest bardzo wyraźna.


# Zad 5

# 1. Parametry sygnału
fs = 128        # częstotliwość próbkowania [Hz]
N5 = 128        # liczba próbek (potęga 2)
dt = 1.0 / fs   # krok czasowy [s]

# składowe sinusoidalne: A_i * sin(2*pi*a_i*t)
A = [3.0, 1.5]
a = [5,   12 ]

# składowe cosinusoidalne: B_j * cos(2*pi*b_j*t)
B = [2.0]
b = [3  ]

# generowanie próbek sygnału
t_values = [n * dt for n in range(N5)]
signal5 = []
for t in t_values:
    val = 0.0
    for i in range(len(A)):
        val += A[i] * math.sin(2 * math.pi * a[i] * t)
    for j in range(len(B)):
        val += B[j] * math.cos(2 * math.pi * b[j] * t)
    signal5.append(val)

# 2. FFT sygnału
spectrum5 = fft(signal5)

# Widmo amplitudowe (jednostronne, znormalizowane)
# amplituda = |X_k| / N, ale dla k>0 i k<N/2 mnożymy razy 2 (bo sygnał rzeczywisty)
half = N5 // 2 + 1
amplitudes_orig = []
for k in range(half):
    amp = abs(spectrum5[k]) / N5
    if 0 < k < N5 // 2:
        amp *= 2
    amplitudes_orig.append(amp)

freqs = [k * fs / N5 for k in range(half)]

# Wydruk widma
print("\nWidmo amplitudowe (składowe > 0.1):")
for k in range(half):
    if amplitudes_orig[k] > 0.1:
        print(f"  bin k={k:3d}   f = {freqs[k]:6.1f} Hz   amplituda = {amplitudes_orig[k]:.3f}")

# 3. Wybór częstotliwości do wyzerowania
print("\nPodaj numery binów (k) do wyzerowania, oddzielone spacją (Enter = pomiń):")
user_input = input("> ").strip()

bins_to_zero = []
if user_input:
    for token in user_input.split():
        try:
            bins_to_zero.append(int(token))
        except ValueError:
            pass

# 4. Filtracja - zerowanie wybranych binów (+ sprzężone lustrzane)
filtered_spectrum = list(spectrum5)
for k in bins_to_zero:
    if 0 <= k < N5:
        filtered_spectrum[k] = complex(0)
        mirror = N5 - k
        if 0 < mirror < N5:
            filtered_spectrum[mirror] = complex(0)

# Widmo po filtracji
amplitudes_filt = []
for k in range(half):
    amp = abs(filtered_spectrum[k]) / N5
    if 0 < k < N5 // 2:
        amp *= 2
    amplitudes_filt.append(amp)

# 5. Odwrotna FFT i rekonstrukcja sygnału
reconstructed_complex = ifft(filtered_spectrum)
signal_reconstructed = [x.real for x in reconstructed_complex]

# 6. Wykresy (2x2)
fig5, axes = plt.subplots(2, 2, figsize=(13, 8))
fig5.suptitle('Zadanie 5 - Filtracja sygnału z użyciem FFT')

axes[0, 0].plot(t_values, signal5, color='steelblue')
axes[0, 0].set_title('Sygnał oryginalny')
axes[0, 0].set_xlabel('Czas [s]')
axes[0, 0].set_ylabel('Amplituda')
axes[0, 0].grid(True)

axes[0, 1].stem(freqs, amplitudes_orig)
axes[0, 1].set_title('Widmo amplitudowe - oryginał')
axes[0, 1].set_xlabel('Częstotliwość [Hz]')
axes[0, 1].set_ylabel('Amplituda')
axes[0, 1].grid(True)

axes[1, 0].stem(freqs, amplitudes_filt)
axes[1, 0].set_title('Widmo amplitudowe - po filtracji')
axes[1, 0].set_xlabel('Częstotliwość [Hz]')
axes[1, 0].set_ylabel('Amplituda')
axes[1, 0].grid(True)

axes[1, 1].plot(t_values, signal_reconstructed, color='darkorange')
axes[1, 1].set_title('Sygnał zrekonstruowany (po filtracji)')
axes[1, 1].set_xlabel('Czas [s]')
axes[1, 1].set_ylabel('Amplituda')
axes[1, 1].grid(True)

plt.tight_layout()
plt.show()
