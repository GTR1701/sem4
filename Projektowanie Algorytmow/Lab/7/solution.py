def czynniki_pierwsze(n):
    if n < 2:
        return []
    for i in range(2, n):
        if n % i == 0:
            return czynniki_pierwsze(i) + czynniki_pierwsze(n // i)
    return [n]


print(czynniki_pierwsze(60))
print(czynniki_pierwsze(121))
print(czynniki_pierwsze(997))


import time


def sito_eratostenesa(p):
    jest_pierwsza = [True] * (p + 1)
    jest_pierwsza[0] = False
    jest_pierwsza[1] = False

    i = 2
    while i * i <= p:
        if jest_pierwsza[i]:
            j = i * i
            while j <= p:
                jest_pierwsza[j] = False
                j += i
        i += 1

    wynik = []
    for n in range(2, p + 1):
        if jest_pierwsza[n]:
            wynik.append(n)
    return wynik


def sprawdz_podzielnosc(p):
    wynik = []
    for n in range(2, p + 1):
        pierwsza = True
        for i in range(2, n):
            if n % i == 0:
                pierwsza = False
                break
        if pierwsza:
            wynik.append(n)
    return wynik


for p in [50, 100, 500]:
    start = time.time()
    sito_eratostenesa(p)
    czas_sito = time.time() - start

    start = time.time()
    sprawdz_podzielnosc(p)
    czas_prosta = time.time() - start

    print(f"p={p}: sito={czas_sito:.6f}s, prosta={czas_prosta:.6f}s")

print(sito_eratostenesa(1000))


import matplotlib.pyplot as plt
from collections import Counter


def nwd_faktoryzacja(a, b):
    czynniki_a = czynniki_pierwsze(a)
    czynniki_b = czynniki_pierwsze(b)

    licznik_a = Counter(czynniki_a)
    licznik_b = Counter(czynniki_b)

    wynik = 1
    for p in licznik_a:
        if p in licznik_b:
            wynik *= p ** min(licznik_a[p], licznik_b[p])
    return wynik


def nwd_euklides(a, b):
    while b != 0:
        a, b = b, a % b
    return a


a = 12345
m = 1000

czasy_faktoryzacja = []
czasy_euklides = []

for b in range(1, m + 1):
    start = time.time()
    nwd_faktoryzacja(a, b)
    czasy_faktoryzacja.append(time.time() - start)

    start = time.time()
    nwd_euklides(a, b)
    czasy_euklides.append(time.time() - start)

plt.plot(range(1, m + 1), czasy_faktoryzacja, label="faktoryzacja")
plt.plot(range(1, m + 1), czasy_euklides, label="euklides")
plt.xlabel("b")
plt.ylabel("czas [s]")
plt.legend()
plt.title(f"NWD({a}, b) dla b w <1, {m}>")
plt.show()


import random


def szybkie_potegowanie(podstawa, wykladnik, modulo):
    wynik = 1
    podstawa = podstawa % modulo
    while wykladnik > 0:
        if wykladnik % 2 == 1:
            wynik = (wynik * podstawa) % modulo
        wykladnik = wykladnik // 2
        podstawa = (podstawa * podstawa) % modulo
    return wynik


def test_fermata(n, k=10):
    if n < 2:
        return False
    for _ in range(k):
        a = random.randint(2, n - 2)
        if szybkie_potegowanie(a, n - 1, n) != 1:
            return False
    return True


def test_millera_rabina(n, k=10):
    if n < 2:
        return False
    if n == 2 or n == 3:
        return True
    if n % 2 == 0:
        return False

    r = 0
    d = n - 1
    while d % 2 == 0:
        r += 1
        d //= 2

    for _ in range(k):
        a = random.randint(2, n - 2)
        x = szybkie_potegowanie(a, d, n)

        if x == 1 or x == n - 1:
            continue

        jest_zlozona = True
        for _ in range(r - 1):
            x = (x * x) % n
            if x == n - 1:
                jest_zlozona = False
                break

        if jest_zlozona:
            return False

    return True


liczby_pierwsze = [7, 13, 97, 997, 7919]
liczby_zlozone = [9, 15, 100, 561, 8000]

print("Liczba | Fermat | Miller-Rabin")
print("-" * 35)
for n in liczby_pierwsze + liczby_zlozone:
    fermat = test_fermata(n)
    miller = test_millera_rabina(n)
    print(f"{n:6} | {str(fermat):6} | {str(miller)}")
