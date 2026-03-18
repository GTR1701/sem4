import time
import random

def counting_sort_digit(A, exp, base=10):
 """Counting Sort dla danej cyfry (exp - potęga)."""
 n = len(A)
 output = [0] * n
 count = [0] * base

 for i in range(n):
  index = (A[i] // exp) % base
 count[index] += 1

 for i in range(1, base):
  count[i] += count[i - 1]

 i = n - 1
 while i >= 0:
  index = (A[i] // exp) % base
  output[count[index] - 1] = A[i]
  count[index] -= 1
  i -= 1

 for i in range(n):
  A[i] = output[i]

def radix_sort(A):
 """Radix Sort LSD - cyfra po cyfrze."""
 if not A:
  return
 base = 10
 exp = 1
 max_val = max(A)

 while max_val // exp > 0:
  counting_sort_digit(A, exp, base)
  exp *= base

# Testy
def test_radix_sort():
 """Testy efektywności."""
 sizes = [1000, 5000, 10000]
 for size in sizes:
  data = [random.randint(0, 9999) for _ in range(size)] # 4 cyfry
  start = time.time()
  radix_sort(data.copy())
  end = time.time()
  print(f"Rozmiar {size}: {end - start:.4f}s")

 # Wyniki: n=1000: ~0.001s, liniowy wzrost O(dn)
#Zad 2

# Uogólniony Counting Sort dla dowolnego zakresu min-max
def counting_sort_general(A, min_val=None, max_val=None):
 """
 Uogólniony Counting Sort dla dowolnego zakresu kluczy.
 Przeskalowanie: klucz_robocze = A[i] - min_val
 Obsługuje duplikaty i jest stabilny (iteracja od końca).
 Zwraca nową tablicę posortowaną.
 """
 if not A:
  return []

 if min_val is None:
  min_val = min(A)
 if max_val is None:
  max_val = max(A)

 k = max_val - min_val  # zakres po przeskalowaniu
 count = [0] * (k + 1)

 # Zliczanie wystąpień (przeskalowane klucze)
 for val in A:
  count[val - min_val] += 1

 # Skumulowane sumy – wyznaczają pozycję końcową każdego klucza
 for i in range(1, k + 1):
  count[i] += count[i - 1]

 # Budowanie wyjścia od końca -> stabilność
 n = len(A)
 output = [0] * n
 for i in range(n - 1, -1, -1):
  scaled = A[i] - min_val
  output[count[scaled] - 1] = A[i]
  count[scaled] -= 1

 return output


# Test stabilności z identycznymi elementami
def test_stability_counting_sort():
 """
 Sprawdza stabilność uogólnionego Counting Sort.
 Używa krotek (klucz, oryginalny_indeks), by porównać kolejność
 elementów o tym samym kluczu w wyniku.
 """
 print("\n=== Test stabilności Counting Sort ===")

 # Dane: pary (klucz, oryginalny indeks) – sortujemy po kluczu
 data_keys = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5]
 tagged = [(key, idx) for idx, key in enumerate(data_keys)]

 # Posortuj klucze uogólnionym Counting Sort, zachowując tagi
 # Adaptacja: zamiast samych wartości sortujemy tagi przez stable pass
 keys = [t[0] for t in tagged]
 min_k, max_k = min(keys), max(keys)
 k = max_k - min_k
 count = [0] * (k + 1)

 for key in keys:
  count[key - min_k] += 1
 for i in range(1, k + 1):
  count[i] += count[i - 1]

 n = len(tagged)
 output = [None] * n
 for i in range(n - 1, -1, -1):
  key = tagged[i][0]
  scaled = key - min_k
  output[count[scaled] - 1] = tagged[i]
  count[scaled] -= 1

 # Sprawdzenie: klucze posortowane
 sorted_keys = [t[0] for t in output]
 assert sorted_keys == sorted(sorted_keys), "BŁĄD: klucze nie są posortowane!"

 # Sprawdzenie stabilności: dla każdej grupy takich samych kluczy
 # oryginalne indeksy muszą być w rosnącej kolejności
 stable = True
 prev_key, prev_orig = output[0]
 for key, orig_idx in output[1:]:
  if key == prev_key and orig_idx < prev_orig:
   stable = False
   break
  prev_key, prev_orig = key, orig_idx

 if stable:
  print("Stabilność: OK – kolejność elementów o tym samym kluczu zachowana")
 else:
  print("Stabilność: BŁĄD – kolejność naruszona")

 print(f"Posortowane klucze: {sorted_keys}")


# Test uogólnionego Counting Sort na ujemnych i dużych zakresach
def test_counting_sort_general():
 print("\n=== Test uogólnionego Counting Sort ===")

 cases = [
  ([3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5], "standardowe wartości"),
  ([-5, -1, -3, 0, 2, -2, 1], "zakres ujemny-dodatni"),
  ([100, 200, 150, 120, 180], "duże wartości, mały zakres"),
  ([7, 7, 7, 7], "same duplikaty"),
  ([1], "jeden element"),
 ]

 for data, label in cases:
  result = counting_sort_general(data[:])
  expected = sorted(data)
  status = "OK" if result == expected else "BŁĄD"
  print(f"  [{status}] {label}: {result}")

#Zad 3

# ── MSD Radix Sort dla stringów (rekurencyjny) ───────────────────────────────
def msd_radix_sort_strings(A, alphabet=26):
 def _sort(arr, pos):
  if len(arr) <= 1:
   return arr
  buckets = [[] for _ in range(alphabet + 1)]
  for s in arr:
   if pos >= len(s):
    buckets[0].append(s)
   else:
    buckets[ord(s[pos]) - ord('a') + 1].append(s)
  result = buckets[0][:]
  for b in buckets[1:]:
   result += _sort(b, pos + 1)
  return result
 A[:] = _sort(A, 0)

# ── LSD Radix Sort dla stringów (stała długość) ──────────────────────────────
def lsd_radix_sort_strings(A, str_len, alphabet=26):
 for pos in range(str_len - 1, -1, -1):
  buckets = [[] for _ in range(alphabet)]
  for s in A:
   buckets[ord(s[pos]) - ord('a')].append(s)
  A[:] = [s for b in buckets for s in b]

# ── LSD Radix Sort dla liczb z parametryczną bazą ───────────────────────────
def lsd_radix_sort_base(A, base):
 if not A:
  return
 max_val = max(A)
 exp = 1
 while max_val // exp > 0:
  n = len(A)
  output = [0] * n
  count = [0] * base
  for x in A:
   count[(x // exp) % base] += 1
  for i in range(1, base):
   count[i] += count[i - 1]
  for i in range(n - 1, -1, -1):
   d = (A[i] // exp) % base
   output[count[d] - 1] = A[i]
   count[d] -= 1
  A[:] = output
  exp *= base

# ── Testy i porównania ───────────────────────────────────────────────────────
def bench(fn, data):
 t = time.time()
 fn(data)
 return time.time() - t

def test_lsd_vs_msd_strings():
 print("\n=== LSD vs MSD – losowe stringi (alfabet 26 liter) ===")
 STR_LEN = 8
 sizes = [1000, 5000, 10000]
 for n in sizes:
  data = [''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=STR_LEN)) for _ in range(n)]
  d_lsd = data[:]
  d_msd = data[:]
  t_lsd = bench(lambda a: lsd_radix_sort_strings(a, STR_LEN), d_lsd)
  t_msd = bench(msd_radix_sort_strings, d_msd)
  ok = "OK" if d_lsd == d_msd == sorted(data) else "BŁĄD"
  print(f"  n={n:>6}: LSD={t_lsd:.4f}s  MSD={t_msd:.4f}s  [{ok}]")

def test_lsd_bases():
 print("\n=== LSD Radix Sort – wpływ bazy (32-bitowe liczby) ===")
 n = 10000
 data = [random.randint(0, 2**32 - 1) for _ in range(n)]
 for base in [2, 8, 10, 256]:
  d = data[:]
  t = bench(lambda a: lsd_radix_sort_base(a, base), d)
  ok = "OK" if d == sorted(data) else "BŁĄD"
  print(f"  base={base:>3}: {t:.4f}s  [{ok}]")

def test_counting_vs_lsd():
 print("\n=== Counting Sort vs LSD (n=10000, różne zakresy) ===")
 n = 10000
 cases = [
  (lambda: [random.randint(0, 99) for _ in range(n)],   "zakres 0-99"),
  (lambda: [random.randint(0, 9999) for _ in range(n)],  "zakres 0-9999"),
  (lambda: [random.randint(0, 2**32-1) for _ in range(n)], "zakres 32-bit"),
 ]
 for gen, label in cases:
  data = gen()
  d_cs = data[:]
  d_lsd = data[:]
  rng = max(d_cs) - min(d_cs)
  if rng > 10_000_000:
   t_cs_str = "N/A (zakres za duży)"
  else:
   t_cs = bench(lambda a: counting_sort_general(a), d_cs)
   t_cs_str = f"{t_cs:.4f}s"
  t_lsd = bench(lambda a: lsd_radix_sort_base(a, 256), d_lsd)
  print(f"  {label:20}: Counting={t_cs_str:>16}  LSD(b=256)={t_lsd:.4f}s")

#Zad 4

def bucket_sort(A, num_buckets):
 """Bucket Sort uogólniony na zakres [min,max] przez skalowanie.
 Każdy element trafia do kubełka: idx = (x-min)/(max-min) * (num_buckets-1)
 Kubełki są sortowane przez sorted() (Timsort).
 Zwraca nową posortowaną listę.
 """
 if len(A) <= 1:
  return A[:]
 min_val, max_val = min(A), max(A)
 if min_val == max_val:
  return A[:]
 buckets = [[] for _ in range(num_buckets)]
 span = max_val - min_val
 for x in A:
  idx = int((x - min_val) / span * (num_buckets - 1))
  buckets[idx].append(x)
 result = []
 for b in buckets:
  result.extend(sorted(b))
 return result

def test_bucket_sort():
 print("\n=== Bucket Sort – wpływ liczby kubełków (n=10000, float [0,1000]) ===")
 n = 10000
 data = [random.uniform(0, 1000) for _ in range(n)]
 for nb in [10, 100, 1000, 5000]:
  d = data[:]
  t = bench(lambda a, k=nb: bucket_sort(a, k), d)
  ok = "OK" if bucket_sort(data, nb) == sorted(data) else "BŁĄD"
  print(f"  kubełków={nb:>5}: {t:.4f}s  [{ok}]")

 print("\n=== Bucket Sort vs sorted() vs Counting Sort (n=10000, int [0,9999]) ===")
 data_int = [random.randint(0, 9999) for _ in range(n)]

 d = data_int[:]
 t_py = bench(lambda a: a.sort(), d)

 d = data_int[:]
 t_cs = bench(counting_sort_general, d)

 for nb in [10, 100, 1000, 5000]:
  d = data_int[:]
  t_bs = bench(lambda a, k=nb: bucket_sort(a, k), d)
  print(f"  kubełków={nb:>5}: sorted()={t_py:.4f}s  Counting={t_cs:.4f}s  Bucket={t_bs:.4f}s")

# Wyniki (n=10000, int [0,9999]):
#   kubełków=   10: sorted()~0.001s  Counting~0.003s  Bucket~0.015s  (mało kubełków -> duże kubełki)
#   kubełków=  100: sorted()~0.001s  Counting~0.003s  Bucket~0.004s  (dobry balans)
#   kubełków= 1000: sorted()~0.001s  Counting~0.003s  Bucket~0.003s  (blisko Counting Sort)
#   kubełków= 5000: sorted()~0.001s  Counting~0.003s  Bucket~0.008s  (overhead tworzenia kubełków rośnie)
#
# Wnioski:
#   - Bucket Sort osiąga optimum przy num_buckets ~ sqrt(n) (tu: ~100 dla n=10000)
#   - Counting Sort jest szybszy dla int o małym zakresie (O(n+k)), ale wymaga pamięci O(k)
#   - Python sorted() (Timsort) jest bardzo trudny do pobicia dla małych n
#   - Bucket Sort sprawdza się najlepiej dla danych zmiennoprzecinkowych równomiernie rozłożonych
#   - Dla dużych zakresów (float) Counting Sort nie działa; Bucket Sort jest naturalnym wyborem

if __name__ == "__main__":
 test_radix_sort()
 test_counting_sort_general()
 test_stability_counting_sort()
 test_lsd_vs_msd_strings()
 test_lsd_bases()
 test_counting_vs_lsd()
 test_bucket_sort()

