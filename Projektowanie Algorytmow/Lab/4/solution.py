import random
import string
import time
import sys
import os


def brute_force(text, pattern):
  """Wyszukiwanie wzorca metodą naiwną (Brute Force)"""
  positions = []
  n, m = len(text), len(pattern)
  for i in range(n - m + 1):
    match = True
    for j in range(m):
      if text[i + j] != pattern[j]:
        match = False
        break
    if match:
      positions.append(i)
  return positions

def kmp_build_lps(pattern):
  """Budowa tablicy LPS dla algorytmu KMP"""
  lps = [0] * len(pattern)
  length = 0
  i = 1
  while i < len(pattern):
    if pattern[i] == pattern[length]:
      length += 1
      lps[i] = length
      i += 1
    else:
      if length != 0:
        length = lps[length - 1]
      else:
        lps[i] = 0
        i += 1
  return lps

def kmp_search(text, pattern):
  """Wyszukiwanie wzorca algorytmem Knutha-Morrisa-Pratta"""
  positions = []
  n, m = len(text), len(pattern)
  lps = kmp_build_lps(pattern)
  i = 0
  j = 0
  while i < n:
    if text[i] == pattern[j]:
      i += 1
      j += 1
    if j == m:
      positions.append(i - j)
      j = lps[j - 1]
    elif i < n and text[i] != pattern[j]:
      if j != 0:
        j = lps[j - 1]
      else:
        i += 1
  return positions

def rabin_karp(text, pattern, base=256, mod=101):
  """Wyszukiwanie wzorca algorytmem Rabina-Karpa"""
  positions = []
  n, m = len(text), len(pattern)
  if m > n:
    return positions
  hpattern = 0
  htext = 0
  h = 1
  for _ in range(m - 1):
    h = (h * base) % mod
  for i in range(m):
    hpattern = (base * hpattern + ord(pattern[i])) % mod
    htext = (base * htext + ord(text[i])) % mod
  for i in range(n - m + 1):
    if hpattern == htext:
      if text[i:i+m] == pattern:
        positions.append(i)
    if i < n - m:
      htext = (base * (htext - ord(text[i]) * h) + ord(text[i+m])) % mod
      htext = (htext + mod) % mod
  return positions

def bm_bad_char_table(pattern):
  """Budowa tablicy złego znaku dla algorytmu Boyera-Moore'a"""
  table = {}
  for i, c in enumerate(pattern):
    table[c] = i
  return table

def boyer_moore(text, pattern):
  """Wyszukiwanie wzorca algorytmem Boyera-Moore'a (reguła złego znaku)"""
  positions = []
  n, m = len(text), len(pattern)
  if m == 0:
    return positions
  bad_char = bm_bad_char_table(pattern)
  s = 0
  while s <= n - m:
    j = m - 1
    while j >= 0 and pattern[j] == text[s + j]:
      j -= 1
    if j < 0:
      positions.append(s)
      s += (m - bad_char.get(text[s + m], -1)) if s + m < n else 1
    else:
      bc_shift = j - bad_char.get(text[s + j], -1)
      s += max(1, bc_shift)
  return positions

def rabin_karp_parametric(text, pattern, base=256, mod=101):
  """Zmodyfikowany Rabin-Karp z konfigurowalnymi parametrami hash'owania.
  Zwraca (positions, collisions) - listę pozycji dopasowań i liczbę kolizji."""
  positions = []
  collisions = 0
  n, m = len(text), len(pattern)
  if m > n:
    return positions, collisions
  hpattern = 0
  htext = 0
  h = 1
  for _ in range(m - 1):
    h = (h * base) % mod
  for i in range(m):
    hpattern = (base * hpattern + ord(pattern[i])) % mod
    htext = (base * htext + ord(text[i])) % mod
  for i in range(n - m + 1):
    if hpattern == htext:
      if text[i:i+m] == pattern:
        positions.append(i)
      else:
        collisions += 1
    if i < n - m:
      htext = (base * (htext - ord(text[i]) * h) + ord(text[i+m])) % mod
      htext = (htext + mod) % mod
  return positions, collisions

def test_rabin_karp_params():
  """Zad 5 - wpływ parametrów base i mod na kolizje i czas działania"""
  text = generate_text(50000)
  pattern = "abcde"
  configs = [
    (256,   101,  "mały mod  (101),  base=256"),
    (256,  1009,  "średni mod (1009), base=256"),
    (256, 99991,  "duży mod  (99991), base=256"),
    ( 31,   101,  "mały mod  (101),  base=31"),
    ( 31,  1009,  "średni mod (1009), base=31"),
    ( 31, 99991,  "duży mod  (99991), base=31"),
  ]
  print("\n=== Zad 5: Rabin-Karp - wpływ parametrów haszowania ===")
  print(f"{'Konfiguracja':<38} {'Dopas.':>7} {'Kolizje':>9} {'Czas':>10}")
  print("-" * 68)
  for base, mod, label in configs:
    start = time.time()
    positions, collisions = rabin_karp_parametric(text, pattern, base, mod)
    elapsed = time.time() - start
    print(f"{label:<38} {len(positions):>7} {collisions:>9} {elapsed:>9.6f}s")

def generate_text(length=100000):
  """Generowanie losowego tekstu"""
  return ''.join(random.choice(string.ascii_lowercase) for _ in range(length))

def test_algorithms():
  """Porównanie czasu działania algorytmów wyszukiwania"""
  texts = [generate_text(10000), generate_text(50000)]
  pattern = "abcab"
  algorithms = [
  ("BruteForce", brute_force),
  ("KMP", kmp_search),
  ("RabinKarp", rabin_karp),
  ("BoyerMoore", boyer_moore),
  ]
  for text in texts:
    print(f"\nDługość tekstu: {len(text)}, wzorzec: '{pattern}'")
    for name, func in algorithms:
      start = time.time()
      result = func(text, pattern)
      end = time.time()
      print(f"{name}: {len(result)} dopasowań, czas: {end - start:.6f}s")

def test_worst_case():
  """Zad 4 - tekst z dużą liczbą powtórzeń, wzorzec z wieloma powtórzeniami"""
  text = "a" * 100000
  pattern = "aaaaab"
  algorithms = [
  ("BruteForce", brute_force),
  ("KMP", kmp_search),
  ("RabinKarp", rabin_karp),
  ("BoyerMoore", boyer_moore),
  ]
  print("\n=== Zad 4: tekst 100000x'a', wzorzec 'aaaaab' ===")
  for name, func in algorithms:
    start = time.time()
    result = func(text, pattern)
    end = time.time()
    print(f"{name}: {len(result)} dopasowań, czas: {end - start:.6f}s")

def search_from_file(filepath, pattern, algorithm="kmp", preview=None):
  """Wczytuje tekst z pliku .txt i wyszukuje wzorzec wybranym algorytmem.
  Wypisuje liczbę dopasowań i pierwsze `preview` indeksów wystąpień (None = wszystkie)."""
  if not os.path.isfile(filepath):
    print(f"Błąd: plik '{filepath}' nie istnieje.")
    return
  with open(filepath, encoding="utf-8") as f:
    text = f.read()
  algorithms = {
    "brute":    brute_force,
    "kmp":      kmp_search,
    "rk":       rabin_karp,
    "bm":       boyer_moore,
  }
  algo_name = algorithm.lower()
  if algo_name not in algorithms:
    print(f"Nieznany algorytm '{algorithm}'. Dostępne: brute, kmp, rk, bm.")
    return
  func = algorithms[algo_name]
  start = time.time()
  positions = func(text, pattern)
  elapsed = time.time() - start
  count = len(positions)
  first_few = positions if preview is None else positions[:preview]
  print(f"Plik:        {filepath}")
  print(f"Wzorzec:     '{pattern}'")
  print(f"Algorytm:    {algo_name}")
  print(f"Dopasowania: {count}")
  if first_few:
    label = "Wszystkie indeksy" if preview is None else f"Pierwsze {min(preview, count)}"
    print(f"{label}: {first_few}")
  else:
    print("Brak dopasowań.")
  print(f"Czas:        {elapsed:.6f}s")

def verify_algorithms(text, pattern):
  """Sprawdza, czy wszystkie algorytmy zwracają identyczne listy indeksów dopasowań.
  Wypisuje wynik weryfikacji oraz komunikat diagnostyczny w przypadku różnic."""
  algorithms = [
    ("BruteForce", brute_force),
    ("KMP",        kmp_search),
    ("RabinKarp",  rabin_karp),
    ("BoyerMoore", boyer_moore),
  ]
  results = {}
  for name, func in algorithms:
    results[name] = sorted(func(text, pattern))

  reference_name, reference = next(iter(results.items()))
  all_equal = True
  print(f"\n=== Weryfikacja zgodności algorytmów (wzorzec: '{pattern}') ===")
  for name, positions in results.items():
    if positions == reference:
      print(f"  {name}: OK ({len(positions)} dopasowań)")
    else:
      all_equal = False
      missing  = sorted(set(reference) - set(positions))
      extra    = sorted(set(positions) - set(reference))
      print(f"  {name}: NIEZGODNOŚĆ względem {reference_name}!")
      if missing:
        print(f"    Brakujące indeksy: {missing}")
      if extra:
        print(f"    Nadmiarowe indeksy: {extra}")

  if all_equal:
    print("  Wynik: wszystkie algorytmy zgodne.")
  else:
    print("  Wynik: wykryto rozbieżności - sprawdź komunikaty powyżej.")

if __name__ == "__main__":
  if len(sys.argv) >= 3:
    # Użycie: python solution.py <plik.txt> <wzorzec> [algorytm] [liczba_wyników]
    _filepath  = sys.argv[1]
    _pattern   = sys.argv[2]
    _algorithm = sys.argv[3] if len(sys.argv) >= 4 else "kmp"
    _preview   = int(sys.argv[4]) if len(sys.argv) >= 5 else None
    search_from_file(_filepath, _pattern, _algorithm, _preview)
  else:
    test_algorithms()
    test_worst_case()
    test_rabin_karp_params()
    text = generate_text(10000)
    verify_algorithms(text, "a")
    verify_algorithms("a" * 1000, "a")

# Zad 2
# BruteForce: 5 dopasowań, czas: 0.010469s
# KMP: 5 dopasowań, czas: 0.009609s
# RabinKarp: 5 dopasowań, czas: 0.021080s

# Zad 3 - Algorytm Boyera-Moore'a (reguła złego znaku)
# Wyniki porównawcze (tekst 50 000 znaków, wzorzec "abc"):
# BruteForce: 5 dopasowań, czas: 0.008089s
# KMP:        5 dopasowań, czas: 0.009310s
# RabinKarp:  5 dopasowań, czas: 0.013605s
# BoyerMoore: 5 dopasowań, czas: 0.005226s
#
# Wnioski:
# Boyer-Moore okazał się najszybszy (~2x szybszy niż BruteForce i KMP).
# Reguła złego znaku pozwala przeskoczyć wiele pozycji już przy pierwszym
# niezgodnym znaku - im rzadsza alfabet/dłuższy wzorzec, tym większy zysk.
# Rabin-Karp był najwolniejszy ze względu na koszt obliczania hash'y.
# KMP i BruteForce mają zbliżone czasy dla krótkich wzorców w losowym tekście.

# Zad 4 - Tekst z dużą liczbą powtórzeń
# Wyniki (tekst 100 000x'a', wzorzec "aaaaab"):
# BruteForce: 0 dopasowań, czas: 0.045110s
# KMP:        0 dopasowań, czas: 0.024224s
# RabinKarp:  0 dopasowań, czas: 0.027234s
# BoyerMoore: 0 dopasowań, czas: 0.027556s
#
# Wnioski:
# BruteForce jest zdecydowanie najwolniejszy - dla każdej pozycji porównuje
# aż 5 znaków 'a' zanim natrafi na niezgodność (brak 'b'), co daje O(n*m)
# w najgorszym przypadku.
# KMP radzi sobie najlepiej dzięki tablicy LPS - po niezgodności nie cofa się
# do początku wzorca, lecz wykorzystuje już dopasowany prefiks, co daje O(n+m).
# RabinKarp: hash wzorca "aaaaab" pasuje często do okien złożonych z samych 'a'
# (kolizje), więc musi wykonywać wiele dodatkowych weryfikacji znakami.
# BoyerMoore traci swoją przewagę w tym przypadku - reguła złego znaku prawie
# nie pomaga, gdy wszystkie znaki tekstu i wzorca są takie same ('a'). Przesuwa
# wzorzec tylko o 1 przy każdej niezgodności na ostatniej pozycji, degenerując
# się do O(n*m).

# Zad 5 - Rabin-Karp z konfigurowalnymi parametrami haszowania
# Tekst: 50 000 losowych znaków, wzorzec: "abcde"
#
# Konfiguracja                            Dopas.   Kolizje       Czas
# --------------------------------------------------------------------
# mały mod  (101),  base=256                   0       503  0.013619s
# średni mod (1009), base=256                  0        70  0.015754s
# duży mod  (99991), base=256                  0         1  0.018194s
# mały mod  (101),  base=31                    0       497  0.014382s
# średni mod (1009), base=31                   0        51  0.015543s
# duży mod  (99991), base=31                   0         2  0.015394s
#
# Wnioski:
# Im większy moduł (mod), tym mniej kolizji - przy mod=101 było ich ~500,
# przy mod=99991 spadły do 1-2. Wynika to bezpośrednio z tego, że przy małym
# modzie wiele różnych okien tekstu daje ten sam hash (przestrzeń hashów jest mała).
# Wybór podstawy (base=256 vs base=31) ma mniejszy wpływ na liczbę kolizji niż
# wartość modułu, lecz może nieznacznie zmieniać rozkład hashy.
# Czas rośnie wraz z modułem - przy dużym mod obliczenia arytmetyczne angażują
# większe liczby, co nieznacznie spowalnia działanie (~0.002s różnicy).
# Kompromis: duży mod (liczba pierwsza > rozmiar tekstu) minimalizuje
# kolizje i eliminuje prawie wszystkie zbędne porównania znaków.
