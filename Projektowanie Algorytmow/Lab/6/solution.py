import random
import time


def analyze_list(a):
	"""Oblicza: najwiekszy element, sume, liczbe dodatnich i srednia."""
	if len(a) == 0:
		return None

	max_val = a[0]
	sum_val = 0
	positive_count = 0

	for i in range(len(a)):
		sum_val = sum_val + a[i]
		if a[i] > max_val:
			max_val = a[i]
		if a[i] > 0:
			positive_count = positive_count + 1

	average = sum_val / len(a)
	return max_val, sum_val, positive_count, average


def generate_data(n):
	"""Tworzy liste n losowych liczb calkowitych z zakresu [-1000, 1000]."""
	return [random.randint(-1000, 1000) for _ in range(n)]


def measure_times(sizes, repeats=5):
	"""Mierzy sredni czas wykonania funkcji analyze_list dla kolejnych rozmiarow."""
	results = []
	for n in sizes:
		data = generate_data(n)
		total = 0.0
		for _ in range(repeats):
			start = time.perf_counter()
			analyze_list(data)
			end = time.perf_counter()
			total += end - start
		avg_time = total / repeats
		results.append((n, avg_time))
	return results


def main():
	"""Uruchamia przyklad i pomiary czasu dla kilku rozmiarow list."""
	example = [3, -2, 7, 0, -9, 10, 4]
	result = analyze_list(example)
	print("Przykladowy wynik:", result)

	random.seed(123)
	sizes = [10_000, 20_000, 50_000, 100_000, 200_000, 500_000, 1_000_000]
	times = measure_times(sizes, repeats=5)

	print("\nPomiary czasu (srednia z 5 uruchomien):")
	for n, t in times:
		print(f"n={n:>8} -> {t:.8f} s")


if __name__ == "__main__":
	main()


# ZLOZONOSC TEORETYCZNA:
# Czas: O(n), bo petla przechodzi jeden raz przez cala liste.
# Pamiec dodatkowa: O(1), bo uzywamy stalej liczby zmiennych pomocniczych.
#
# ANALIZA I WNIOSKI:
# 1) Dla listy o dlugosci n liczba operacji rosnie liniowo wraz z n.
# 2) W pomiarach eksperymentalnych czas powinien rosnac prawie proporcjonalnie
#    do n (np. 2x wieksze n daje w przyblizeniu 2x wiekszy czas).
# 3) Male odchylenia od idealnej proporcji sa normalne (obciazenie systemu,
#    cache procesora, narzut interpretera Pythona).
#
# ZALEZNOSC EKSPERYMENT-TEORIA:
# Jesli w wynikach widac trend liniowy, to potwierdza to oszacowanie O(n).
#
# WYNIKI POMIAROW CZASU (srednia z 5 uruchomien):
# n=   10000 -> 0.00129564 s
# n=   20000 -> 0.00276446 s
# n=   50000 -> 0.00611941 s
# n=  100000 -> 0.01271845 s
# n=  200000 -> 0.02347616 s
# n=  500000 -> 0.05854840 s
# n= 1000000 -> 0.11747546 s
#
# Wniosek z danych: czasy rosna prawie proporcjonalnie do n,
# wiec wyniki eksperymentalne sa zgodne z teoria O(n).


def sum_iterative(a):
	"""Zwraca sume elementow listy w wersji iteracyjnej."""
	suma = 0
	for i in range(len(a)):
		suma = suma + a[i]
	return suma


def sum_recursive(a, n):
	"""Zwraca sume pierwszych n elementow listy w wersji rekurencyjnej."""
	if n == 0:
		return 0
	return a[n - 1] + sum_recursive(a, n - 1)


def measure_sum_times(sizes, repeats=5):
	"""Mierzy czasy wersji iteracyjnej i rekurencyjnej dla roznych n."""
	results = []
	for n in sizes:
		data = generate_data(n)

		total_iter = 0.0
		total_rec = 0.0

		for _ in range(repeats):
			start_iter = time.perf_counter()
			sum_iterative(data)
			end_iter = time.perf_counter()
			total_iter += end_iter - start_iter

			start_rec = time.perf_counter()
			sum_recursive(data, n)
			end_rec = time.perf_counter()
			total_rec += end_rec - start_rec

		avg_iter = total_iter / repeats
		avg_rec = total_rec / repeats
		results.append((n, avg_iter, avg_rec))

	return results


def run_task_2():
	"""Uruchamia porownanie algorytmu sumowania iteracyjnie i rekurencyjnie."""
	random.seed(321)
	sizes = [100, 300, 500, 700, 900]
	results = measure_sum_times(sizes, repeats=5)

	print("\nZadanie 2 - porownanie SUMA iteracyjna i rekurencyjna:")
	for n, t_iter, t_rec in results:
		print(f"n={n:>4} -> iteracyjna: {t_iter:.8f} s, rekurencyjna: {t_rec:.8f} s")


if __name__ == "__main__":
	run_task_2()


# ZADANIE 2 - ZLOZONOSC I WNIOSKI:
# 1) Wersja iteracyjna ma zlozonosc czasowa O(n) i pamieciowa O(1).
# 2) Wersja rekurencyjna ma zlozonosc czasowa O(n), ale pamieciowa O(n),
#    bo kazde wywolanie rekurencyjne trafia na stos.
# 3) W praktyce wersja rekurencyjna jest zwykle wolniejsza przez narzut
#    wielu wywolan funkcji.
# 4) Dlatego dla duzych n lepiej sprawdza sie wersja iteracyjna.
#
# WYNIKI POMIAROW ZADANIE 2 (srednia z 5 uruchomien):
# n= 100 -> iteracyjna: 0.00000689 s, rekurencyjna: 0.00001346 s
# n= 300 -> iteracyjna: 0.00001350 s, rekurencyjna: 0.00008909 s
# n= 500 -> iteracyjna: 0.00002261 s, rekurencyjna: 0.00015177 s
# n= 700 -> iteracyjna: 0.00003241 s, rekurencyjna: 0.00021558 s
# n= 900 -> iteracyjna: 0.00004149 s, rekurencyjna: 0.00026603 s
#
# Wniosek: obie metody maja O(n), ale iteracyjna jest wyraznie szybsza.
# Wynik eksperymentalny zgadza sie z analiza praktyczna (narzut rekurencji).


def matrix_multiply(a, b, n):
    """Mnozy dwie macierze kwadratowe a i b rozmiaru n x n.
    Zwraca wynikowa macierz c oraz liczbe wykonanych mnozenia."""
    c = [[0] * n for _ in range(n)]
    multiplications = 0

    for i in range(n):
        for j in range(n):
            s = 0
            for k in range(n):
                s = s + a[i][k] * b[k][j]
                multiplications = multiplications + 1
            c[i][j] = s

    return c, multiplications


def generate_matrix(n):
    """Tworzy losowa macierz kwadratowa rozmiaru n x n z wartosciami 0-9."""
    return [[random.randint(0, 9) for _ in range(n)] for _ in range(n)]


def run_task_3():
    """Uruchamia mnozenie macierzy dla kilku rozmiarow i wypisuje czas + liczbe mnozenia."""
    random.seed(42)
    sizes = [10, 20, 50, 100, 150, 200]

    print("\nZadanie 3 - mnozenie macierzy MATRIX-MULTIPLY:")
    for n in sizes:
        a = generate_matrix(n)
        b = generate_matrix(n)

        start = time.perf_counter()
        c, mults = matrix_multiply(a, b, n)
        end = time.perf_counter()

        print(f"n={n:>3} -> czas: {end - start:.8f} s, mnozenia: {mults}")


if __name__ == "__main__":
    run_task_3()


# ZADANIE 3 - ZLOZONOSC I WNIOSKI:
# 1) Trzy zagniezdzzone petle po n krokow kazda daja O(n^3) operacji.
# 2) Liczba mnozenia wynosi dokladnie n^3, co widac w wynikach:
#    n=10 -> 1 000, n=50 -> 125 000, n=100 -> 1 000 000, n=200 -> 8 000 000.
# 3) Czas rowniez rosnie szesciennie: podwojenie n daje ok. 8x wiekszy czas.
# 4) Pamiec dodatkowa: O(n^2) na przechowanie macierzy wynikowej.
#
# WYNIKI POMIAROW ZADANIE 3:
# n= 10 -> czas: 0.00009968 s, mnozenia: 1000
# n= 20 -> czas: 0.00078535 s, mnozenia: 8000
# n= 50 -> czas: 0.01156546 s, mnozenia: 125000
# n=100 -> czas: 0.09209975 s, mnozenia: 1000000
# n=150 -> czas: 0.31198188 s, mnozenia: 3375000
# n=200 -> czas: 0.75897004 s, mnozenia: 8000000
#
# Wniosek: wyniki eksperymentalne potwierdzaja zlozonosc O(n^3).
# Zarowno czas jak i liczba mnozenia rosna szesciennie wraz z n.


def power_fast(a, n, calls):
    """Szybkie potegowanie przez kolejne podnosienie do kwadratu (rekurencja).
    calls to lista jednoelementowa uzywana jako licznik wywolan."""
    calls[0] = calls[0] + 1
    if n == 0:
        return 1
    if n % 2 == 0:
        x = power_fast(a, n // 2, calls)
        return x * x
    else:
        return a * power_fast(a, n - 1, calls)


def power_simple(a, n):
    """Proste potegowanie przez petle - mnozy a przez siebie n razy."""
    result = 1
    for _ in range(n):
        result = result * a
    return result


def run_task_4():
    """Porownuje szybkie i proste potegowanie pod wzgledem czasu i liczby wywolan."""
    a = 2
    exponents = [10, 100, 1000, 10000, 100000, 1000000]

    print("\nZadanie 4 - szybkie potegowanie vs prosty algorytm:")
    for n in exponents:
        calls = [0]
        start = time.perf_counter()
        power_fast(a, n, calls)
        end = time.perf_counter()
        t_fast = end - start

        start = time.perf_counter()
        power_simple(a, n)
        end = time.perf_counter()
        t_simple = end - start

        print(f"n={n:>7} -> szybkie: {t_fast:.8f} s (wywolan: {calls[0]:>4}), "
              f"proste: {t_simple:.8f} s")


if __name__ == "__main__":
    run_task_4()


# ZADANIE 4 - ZLOZONOSC I WNIOSKI:
# Szybkie potegowanie:
#   - Zlozonosc czasowa i pamieciowa: O(log n) — co parzyste n to dzielimy
#     wykladnik na pol, co nieparzyste odejmujemy 1 (i od razu polowimy).
#   - Liczba wywolan funkcji wynosi mniej wiecej 2*log2(n).
#
# Proste potegowanie:
#   - Zlozonosc: O(n) — zawsze dokladnie n mnozen w petli.
#
# WYNIKI POMIAROW ZADANIE 4:
# n=     10 -> szybkie: 0.00001112 s (wywolan:  6), proste: 0.00000345 s
# n=    100 -> szybkie: 0.00000467 s (wywolan: 10), proste: 0.00008365 s
# n=   1000 -> szybkie: 0.00000986 s (wywolan: 16), proste: 0.00011850 s
# n=  10000 -> szybkie: 0.00004068 s (wywolan: 19), proste: 0.00267543 s
# n= 100000 -> szybkie: 0.00029054 s (wywolan: 23), proste: 0.18230059 s
# n=1000000 -> szybkie: 0.00381343 s (wywolan: 27), proste: 13.98259784 s
#
# Wniosek: dla malych n roznica jest niewidoczna, ale juz dla n=1 000 000
# szybkie potegowanie wykonuje tylko ok. 40 wywolan, a proste milion mnozen.
# Roznica czasow rosnie wraz z n i jest wyraznie widoczna eksperymentalnie.


def zero_subset(a):
    """Sprawdza czy istnieje niepusty podzbiór listy a o sumie rownej 0.
    Iteruje po wszystkich maskach bitowych od 1 do 2^n - 1.
    Zwraca (found, subsets_checked), gdzie subsets_checked to liczba
    sprawdzonych podzbiorow (rowna 2^n - 1)."""
    n = len(a)
    found = False
    subsets_checked = 0

    for mask in range(1, 2 ** n):
        subsets_checked = subsets_checked + 1
        s = 0
        subset = []
        for i in range(n):
            if mask & (1 << i):
                s = s + a[i]
                subset.append(a[i])
        if s == 0:
            found = True

    return found, subsets_checked


def run_task_5():
    """Mierzy czas zero_subset dla rosnacych n i potwierdza zlozonosc O(2^n)."""
    random.seed(7)
    sizes = [10, 12, 14, 16, 18, 20, 22, 24]

    print("\nZadanie 5 - ZERO-SUBSET, zlozonosc 2^n:")
    for n in sizes:
        # Dane bez oczywistego podzbioru zerowego (same liczby dodatnie + jedna ujemna)
        a = [random.randint(1, 100) for _ in range(n - 1)] + [-999]

        start = time.perf_counter()
        found, subsets_checked = zero_subset(a)
        end = time.perf_counter()

        print(f"n={n:>2} -> czas: {end - start:.6f} s, "
              f"podzbiorow: {subsets_checked:>8} (2^n={2**n:>8}), znaleziono: {found}")


if __name__ == "__main__":
    run_task_5()


# ZADANIE 5 - ZLOZONOSC I WNIOSKI:
# 1) Dla listy n-elementowej liczba niepustych podzbiorow wynosi 2^n - 1.
#    Algorytm sprawdza kazdy z nich, wiec zlozonosc to O(2^n).
# 2) Kazde zwiekszenie n o 1 podwaja liczbe sprawdzonych podzbiorow i czas.
# 3) Dla n=24 sprawdzamy juz ponad 16 milionow podzbiorow — czas wyrazni rosnie.
# 4) Pamiec dodatkowa: O(n) na subset i zmienne pomocnicze.
#
# WYNIKI POMIAROW ZADANIE 5:
# n=10 -> czas:  0.000590 s, podzbiorow:      1023 (2^n=     1024)
# n=12 -> czas:  0.002737 s, podzbiorow:      4095 (2^n=     4096)
# n=14 -> czas:  0.013889 s, podzbiorow:     16383 (2^n=    16384)
# n=16 -> czas:  0.063468 s, podzbiorow:     65535 (2^n=    65536)
# n=18 -> czas:  0.263478 s, podzbiorow:    262143 (2^n=   262144)
# n=20 -> czas:  1.144328 s, podzbiorow:   1048575 (2^n=  1048576)
# n=22 -> czas:  5.181254 s, podzbiorow:   4194303 (2^n=  4194304)
# n=24 -> czas: 22.824178 s, podzbiorow:  16777215 (2^n= 16777216)
#
# Wniosek: exponencjalny wzrost czasu jest dobrze widoczny eksperymentalnie.
# Kazde +1 do n niemal dokladnie podwaja czas, co potwierdza O(2^n).


# =============================================================================
# ZADANIE 6 - POROWNANIE CZASOW TRZECH ALGORYTMOW O ROZNYCH ZLOZONO SCIACH
# =============================================================================
# Algorytmy uzyte do porownania (z poprzednich zadan):
#   - sum_iterative  -> O(n)
#   - matrix_multiply -> O(n^3)
#   - zero_subset    -> O(2^n)  (tylko male n, bo rosnie wykladniczo)

def run_task_6():
    """Zbiera czasy dla trzech algorytmow i wyswietla zestawienie porownawcze."""
    random.seed(99)
    REPEATS = 3

    # --- O(n): sum_iterative ---
    sizes_linear = [10, 50, 100, 200, 500, 1000, 5000, 10000]
    print("\nZadanie 6a - O(n): sum_iterative")
    print(f"{'n':>6}  {'czas (srednia)':>16}")
    for n in sizes_linear:
        data = generate_data(n)
        total = 0.0
        for _ in range(REPEATS):
            start = time.perf_counter()
            sum_iterative(data)
            total += time.perf_counter() - start
        print(f"{n:>6}  {total / REPEATS:.8f} s")

    # --- O(n^3): matrix_multiply ---
    sizes_cubic = [10, 50, 100, 200]
    print("\nZadanie 6b - O(n^3): matrix_multiply")
    print(f"{'n':>6}  {'czas (srednia)':>16}  {'operacji (n^3)':>14}")
    for n in sizes_cubic:
        a = generate_matrix(n)
        b = generate_matrix(n)
        total = 0.0
        for _ in range(REPEATS):
            start = time.perf_counter()
            matrix_multiply(a, b, n)
            total += time.perf_counter() - start
        print(f"{n:>6}  {total / REPEATS:.8f} s  {n**3:>14}")

    # --- O(2^n): zero_subset ---
    sizes_exp = [10, 12, 14, 16, 18, 20]
    print("\nZadanie 6c - O(2^n): zero_subset")
    print(f"{'n':>4}  {'czas':>12}  {'podzbiorow (2^n-1)':>20}")
    for n in sizes_exp:
        a = [random.randint(1, 100) for _ in range(n)]
        start = time.perf_counter()
        _, checked = zero_subset(a)
        elapsed = time.perf_counter() - start
        print(f"{n:>4}  {elapsed:.6f} s  {checked:>20}")


if __name__ == "__main__":
    run_task_6()


# ZADANIE 6 - WYNIKI I ANALIZA:
#
# O(n) - sum_iterative (srednia z 3 powtorzen):
#     n=   10 -> 0.00000135 s
#     n=   50 -> 0.00000156 s
#     n=  100 -> 0.00000256 s
#     n=  200 -> 0.00000465 s
#     n=  500 -> 0.00001383 s
#     n= 1000 -> 0.00002803 s
#     n= 5000 -> 0.00013287 s
#     n=10000 -> 0.00029398 s
#
# O(n^3) - matrix_multiply (srednia z 3 powtorzen):
#     n= 10 -> 0.00005502 s  (operacji:       1000)
#     n= 50 -> 0.00693780 s  (operacji:     125000)
#     n=100 -> 0.05243488 s  (operacji:    1000000)
#     n=200 -> 0.42656300 s  (operacji:    8000000)
#
# O(2^n) - zero_subset (1 pomiar):
#     n=10 -> 0.000564 s  (podzbiorow:    1023)
#     n=12 -> 0.002766 s  (podzbiorow:    4095)
#     n=14 -> 0.012899 s  (podzbiorow:   16383)
#     n=16 -> 0.064918 s  (podzbiorow:   65535)
#     n=18 -> 0.264931 s  (podzbiorow:  262143)
#     n=20 -> 1.141212 s  (podzbiorow: 1048575)
#
# Porownanie z teoria:
# - O(n):   n=1000 vs n=10000 -> czas x10 przy n x10. Zgodne z O(n).
# - O(n^3): n=50 vs n=100     -> czas ~7.5x przy n x2. Zgodne z O(n^3) ~ 8x.
#            n=100 vs n=200   -> czas ~8.1x przy n x2. Dokladnie O(n^3).
# - O(2^n): n=10 vs n=12     -> czas ~5x przy n+2.   Zgodne z O(2^n) ~ 4x.
#            n=18 vs n=20    -> czas ~4.3x przy n+2.  Dokladnie O(2^n).
# Wyniki eksperymentalne potwierdzaja te proporcje.
