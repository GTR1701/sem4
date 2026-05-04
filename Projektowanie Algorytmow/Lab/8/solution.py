def prime_factors(n):
    """Zwraca słownik {czynnik_pierwszy: wykładnik} dla n."""
    factors = {}
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors[d] = factors.get(d, 0) + 1
            n //= d
        d += 1
    if n > 1:
        factors[n] = factors.get(n, 0) + 1
    return factors


def phi(n):
    """Funkcja Eulera phi(n) - liczba liczb względnie pierwszych z n w przedziale [1, n)."""
    if n == 1:
        return 1
    factors = prime_factors(n)
    result = n
    for p in factors:
        result = result // p * (p - 1)
    return result


import math
import time


def czy_pierwsza(n):
    """Sprawdza, czy n jest liczbą pierwszą przez próbne dzielenie do sqrt(n)."""
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for d in range(3, math.isqrt(n) + 1, 2):
        if n % d == 0:
            return False
    return True


def pierwsza_wieksza_od(limit):
    """Zwraca pierwszą liczbę pierwszą większą od limit."""
    n = limit + 1
    while not czy_pierwsza(n):
        n += 1
    return n


def xor_cipher(text: str, key: int) -> str:
    """Szyfruje/deszyfruje tekst operacją XOR z kluczem (bajt po bajcie)."""
    key_byte = key & 0xFF
    return "".join(chr(ord(c) ^ key_byte) for c in text)


def diffie_hellman():
    """Symulacja protokołu wymiany klucza Diffie-Hellmana z szyfrowaniem XOR."""
    print("\n=== Protokół Diffie-Hellman ===")

    p = 23
    g = 5
    print(f"Parametry publiczne:  p = {p},  g = {g}")

    a = 6
    b = 15

    A = pow(g, a, p)
    B = pow(g, b, p)
    print(f"tajny a = {a},  publiczne A = g^a mod p = {A}")
    print(f"tajny b = {b},  publiczne B = g^b mod p = {B}")

    klucz_A = pow(B, a, p)
    klucz_B = pow(A, b, p)
    print(f"\nklucz 1: {klucz_A}")
    print(f"klucz 2: {klucz_B}")
    print(f"Wspólny sekret: {klucz_A}")

    wiadomosc = "Hello Bob!"
    zaszyfrowana = xor_cipher(wiadomosc, klucz_A)
    odszyfrowana = xor_cipher(zaszyfrowana, klucz_B)
    print(f"\nWiadomość oryginalna:  {wiadomosc!r}")
    print(f"Po zaszyfrowaniu XOR:  {zaszyfrowana!r}")
    print(f"Po odszyfrowaniu XOR:  {odszyfrowana!r}")


if __name__ == "__main__":
    test_values = [10, 21, 35, 100]
    print("=== Testy dla wybranych wartości ===")
    for n in test_values:
        factors = prime_factors(n)
        print(f"phi({n:4d}) = {phi(n):4d}  |  czynniki pierwsze: {factors}")

    print("\n=== Wartości phi(n) dla n = 1..30 ===")
    for n in range(1, 31):
        print(f"phi({n:2d}) = {phi(n):2d}")

    print("\n=== Pierwsza liczba pierwsza większa od podanego limitu ===")
    for limit in [100, 500, 1000]:
        start = time.perf_counter()
        p = pierwsza_wieksza_od(limit)
        elapsed = time.perf_counter() - start
        print(f"Pierwsza pierwsza > {limit:4d}: {p:5d}  (czas: {elapsed*1e6:.2f} µs)")

    print("\n=== Ocena czasu dla dużych n (sprawdzanie pojedynczej liczby) ===")
    big_values = [10**6 + 3, 10**9 + 7, 10**12 + 39]
    for n in big_values:
        start = time.perf_counter()
        wynik = czy_pierwsza(n)
        elapsed = time.perf_counter() - start
        print(f"czy_pierwsza({n}) = {wynik}  (czas: {elapsed*1000:.3f} ms)")

    diffie_hellman()

# =============================================================================
# ANALIZA I PORÓWNANIE: RSA vs. DIFFIE-HELLMAN
# =============================================================================
# 1. Mechanizm wymiany kluczy:
#    - RSA jest kryptosystemem asymetrycznym: klucz publiczny (e, n) służy do
#      szyfrowania, a prywatny (d, n) do deszyfrowania. Nadawca nie musi znać
#      żadnej wspólnej tajemnicy – wystarczy klucz publiczny odbiorcy.
#    - Diffie-Hellman nie szyfruje bezpośrednio; umożliwia dwóm stronom
#      uzgodnienie wspólnego sekretu przez kanał publiczny, który następnie
#      służy jako klucz do symetrycznego szyfru (np. AES, XOR).
#
# 2. Rola liczb pierwszych i potęgowania modularnego:
#    - RSA opiera bezpieczeństwo na trudności faktoryzacji dużej liczby n = p·q
#      (dwie duże pierwsze); phi(n) = (p-1)(q-1) pozwala wyznaczyć klucze e i d.
#    - DH opiera bezpieczeństwo na trudności problemu logarytmu dyskretnego:
#      znając g, p i g^a mod p wyznaczenie a jest obliczeniowo niemożliwe.
#    - Oba algorytmy intensywnie korzystają z szybkiego potęgowania modularnego
#      (pow(b, e, m) w Pythonie – O(log e)), co czyni szyfrowanie wydajnym
#      nawet dla dużych liczb.
#
# 3. Ograniczenia własnych implementacji:
#    - Klucze są zbyt krótkie (p = 23 dla DH, n < 2^16 dla RSA) – w praktyce
#      wymagane jest minimum 2048 bitów; nasze wartości można szybko złamać.
#    - Generowanie kluczy nie używa kryptograficznie bezpiecznego źródła
#      losowości (brak secrets/os.urandom), co wyklucza zastosowanie produkcyjne.
#    - Czas faktoryzacji rośnie eksponencjalnie z rozmiarem n, przez co
#      implementacja prime_factors() jest niepraktyczna dla kluczy RSA ≥ 512 bit.
# =============================================================================
