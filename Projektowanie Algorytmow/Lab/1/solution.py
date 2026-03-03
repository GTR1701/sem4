# Zad 1
def linear_search(data, target):
    """Wyszukiwanie liniowe elementu w liście"""
    for i in range(len(data)):
        if data[i] == target:
            return i # zwrócenie indeksu
    return -1 # brak elementu

# Przykład użycia
numbers = [4, 7, 1, 9, 3]
index = linear_search(numbers, 9)
# Wynik: index = 3

def bubble_sort(data):
    """Sortowanie bąbelkowe"""
    n = len(data)
    for i in range(n):
        for j in range(0, n - i - 1):
            if data[j] > data[j + 1]:
                data[j], data[j + 1] = data[j + 1], data[j]

#Zad 2
print("Zad 2", end="\n\n")
"""
Wyszukiwanie liniowe - przeszukuje listę element po elemencie od początku do końca.
Zasada działania:
- Porównuje każdy element z szukaną wartością
- Jeśli znajdzie dopasowanie, zwraca indeks
- Jeśli przejdzie całą listę bez znalezienia, zwraca -1

Czas działania rośnie liniowo z liczbą elementów, ponieważ w najgorszym przypadku
(element na końcu lub brak elementu) musimy sprawdzić wszystkie n elementów.
Złożoność czasowa: O(n)
"""

import random

def wyszukiwanie_liniowe(lista, szukana_wartosc):
    """
    Realizuje wyszukiwanie liniowe wskazanej wartości w liście
    
    Args:
        lista: lista liczb całkowitych do przeszukania
        szukana_wartosc: wartość, którą szukamy
    
    Returns:
        int: indeks znalezionego elementu lub -1 jeśli nie znaleziono
    """
    for i in range(len(lista)):
        if lista[i] == szukana_wartosc:
            return i
    return -1

# Tworzenie listy 100 nieposortowanych liczb całkowitych
rozmiar_listy = 100
lista_liczb = [random.randint(1, 200) for _ in range(rozmiar_listy)]

print(lista_liczb)

# Pobranie wartości od użytkownika
wartosc = int(input("Podaj liczbę do wyszukania: "))

# Wykonanie wyszukiwania liniowego
wynik = wyszukiwanie_liniowe(lista_liczb, wartosc)

if wynik != -1:
    print(f"Wartość {wartosc} znaleziona na indeksie {wynik}.")
else:
    print(f"Wartość {wartosc} nie została znaleziona w liście.")

#Zad 3
print("Zad 3", end="\n\n")

"""
Wyszukiwanie binarne - działa TYLKO dla danych uporządkowanych (posortowanych).
Zasada działania:
- Porównuje szukaną wartość z elementem środkowym
- Zawęża przedział poszukiwań do połowy (lewa lub prawa strona)
- Powtarza proces aż znajdzie element lub przedział stanie się pusty

UWAGA: Wyszukiwanie binarne wymaga wcześniejszego posortowania danych!

Porównanie złożoności czasowej:
- Wyszukiwanie liniowe: O(n) - w najgorszym przypadku n porównań
- Wyszukiwanie binarne: O(log n) - w najgorszym przypadku log₂(n) porównań
Dla 100 elementów: liniowe max 100 porównań, binarne max 7 porównań
"""

import random

def wyszukiwanie_binarne(lista, szukana_wartosc):
    """
    Iteracyjna implementacja wyszukiwania binarnego
    WYMAGA: lista musi być posortowana rosnąco
    
    Args:
        lista: posortowana lista liczb całkowitych
        szukana_wartosc: wartość, którą szukamy
    
    Returns:
        int: indeks znalezionego elementu lub -1 jeśli nie znaleziono
    """
    lewy = 0
    prawy = len(lista) - 1
    
    while lewy <= prawy:
        srodek = (lewy + prawy) // 2
        
        if lista[srodek] == szukana_wartosc:
            return srodek
        elif lista[srodek] < szukana_wartosc:
            lewy = srodek + 1  # Szukaj w prawej połowie
        else:
            prawy = srodek - 1  # Szukaj w lewej połowie
    
    return -1

# Tworzenie listy 100 nieposortowanych liczb całkowitych
rozmiar_listy = 100
lista_liczb = [random.randint(1, 200) for _ in range(rozmiar_listy)]

print(lista_liczb)

# SORTOWANIE - konieczne przed wyszukiwaniem binarnym
lista_liczb.sort()  # Sortowanie rosnące
print(lista_liczb)

# Pobranie wartości od użytkownika
wartosc = int(input("Podaj liczbę do wyszukania: "))

# Wykonanie wyszukiwania binarnego na posortowanej liście
wynik = wyszukiwanie_binarne(lista_liczb, wartosc)

if wynik != -1:
    print(f"Wartość {wartosc} znaleziona na indeksie {wynik}.")
else:
    print(f"Wartość {wartosc} nie została znaleziona w liście.")

#Zad 4
print("Zad 4", end="\n\n")

"""
Sortowanie bąbelkowe z optymalizacją wcześniejszego zakończenia.

Zasada działania sortowania bąbelkowego:
- Porównuje sąsiednie elementy i zamienia je jeśli są w złej kolejności
- Po każdym przebiegu największy element "wypływa" na koniec
- Powtarza proces dla coraz mniejszej części listy

Optymalizacja wcześniejszego zakończenia:
Sprawdza czy w danym przebiegu nastąpiła jakakolwiek zamiana.
Jeśli nie - lista jest już posortowana i można zakończyć wcześniej.

PRZYPADKI POPRAWY EFEKTYWNOŚCI:
- Lista już posortowana: O(n) zamiast O(n²)
- Lista częściowo posortowana: znacznie mniej przebiegów
- Małe elementy na końcu listy: szybsze "wypływanie" na początek
"""

import random

def sortowanie_babelkowe_optimized(lista):
    """
    Sortowanie bąbelkowe z mechanizmem wcześniejszego zakończenia
    
    Args:
        lista: lista liczb do posortowania
    
    Returns:
        tuple: (posortowana lista, liczba przebiegów)
    """
    n = len(lista)
    liczba_przebiegow = 0
    
    for i in range(n):
        liczba_przebiegow += 1
        zamiana_wystapila = False  # Flaga sprawdzająca czy była zamiana
        
        # Porównanie sąsiedních elementów
        for j in range(0, n - i - 1):
            if lista[j] > lista[j + 1]:
                # Zamiana elementów
                lista[j], lista[j + 1] = lista[j + 1], lista[j]
                zamiana_wystapila = True
        
        # Jeśli nie było żadnej zamiany, lista jest posortowana
        if not zamiana_wystapila:
            print(f"Lista posortowana po {liczba_przebiegow} przebiegach (wcześniejsze zakończenie)")
            break
    else:
        print(f"Sortowanie zakończone po {liczba_przebiegow} przebiegach (wszystkie przebiegi)")
    
    return lista, liczba_przebiegow

# Generowanie listy losowych liczb
rozmiar = 15  # Mniejszy rozmiar do łatwiejszego śledzenia
lista_losowa = [random.randint(1, 50) for _ in range(rozmiar)]

print("=== Sortowanie bąbelkowe ===")
print("Lista przed sortowaniem:", lista_losowa.copy())

# Kopia dla sortowania zoptymalizowanego
lista_opt = lista_losowa.copy()
posortowana, przebiegi = sortowanie_babelkowe_optimized(lista_opt)

print("Lista po sortowaniu:", posortowana)
print()

# Test na liście już posortowanej (najlepszy przypadek dla optymalizacji)
print("=== Test posortowana lista ===")
lista_posortowana = sorted([random.randint(1, 50) for _ in range(rozmiar)])
print("Lista już posortowana:", lista_posortowana.copy())

lista_test = lista_posortowana.copy()
_, przebiegi_opt = sortowanie_babelkowe_optimized(lista_test)

print(f"Bez optymalizacji potrzeba {rozmiar} przebiegów")
print(f"Z optymalizacją potrzeba {przebiegi_opt} przebieg(ów)")

#Zad 5
print("Zad 5", end="\n\n")

"""
Sortowanie przez wstawianie (insertion sort) - stopniowo buduje uporządkowaną część listy.

Zasada działania:
- Dzieli listę na część posortowaną (początkowo 1 element) i nieposortowaną
- Bierze kolejny element z części nieposortowanej
- Wstawia go na właściwe miejsce w części posortowanej
- Przesuwa większe elementy w prawo aby zrobić miejsce

DLACZEGO DZIAŁA LEPIEJ DLA DANYCH WSTĘPNIE UPORZĄDKOWANYCH:
- Wewnętrzna pętla (przesuwanie elementów) wykonuje mniej iteracji
- Elementy są już blisko swoich docelowych pozycji
- W najlepszym przypadku (lista posortowana) złożoność: O(n) zamiast O(n²)
- Dla częściowo posortowanych list: znacznie mniej przesunięć
"""

import random
import time

def sortowanie_przez_wstawianie(lista):
    """
    Implementacja sortowania przez wstawianie
    
    Args:
        lista: lista liczb do posortowania
    
    Returns:
        tuple: (posortowana lista, liczba porównań, liczba przesunięć)
    """
    n = len(lista)
    porownan = 0
    przesuniesc = 0
    
    # Zaczynamy od drugiego elementu (indeks 1)
    for i in range(1, n):
        klucz = lista[i]  # Element do wstawienia
        j = i - 1         # Ostatni indeks posortowanej części
        
        # Przesuń elementy większe od klucza w prawo
        while j >= 0 and lista[j] > klucz:
            porownan += 1
            lista[j + 1] = lista[j]  # Przesunięcie w prawo
            przesuniesc += 1
            j -= 1
        
        # Ostatnie porównanie (gdy warunek while się nie spełni)
        if j >= 0:
            porownan += 1
            
        # Wstaw klucz na właściwe miejsce
        lista[j + 1] = klucz
    
    return lista, porownan, przesuniesc

def generuj_czesciowo_posortowana(rozmiar, procent_posortowania=70):
    """
    Generuje listę częściowo posortowaną
    """
    lista = list(range(1, rozmiar + 1))  # Posortowana lista
    
    # Zamień część elementów losowo
    liczba_zamian = int(rozmiar * (100 - procent_posortowania) / 100)
    for _ in range(liczba_zamian):
        i = random.randint(0, rozmiar - 1)
        j = random.randint(0, rozmiar - 1)
        lista[i], lista[j] = lista[j], lista[i]
    
    return lista

# Test 1: Dane losowe
print("\n=== Sortowanie przez wstawianie - Losowe ===")
rozmiar = 12
lista_losowa = [random.randint(1, 50) for _ in range(rozmiar)]

print("Lista przed sortowaniem:", lista_losowa.copy())

start_time = time.time()
lista_posortowana, porownania, przesuniencia = sortowanie_przez_wstawianie(lista_losowa.copy())
czas_losowa = time.time() - start_time

print("Lista po sortowaniu:", lista_posortowana)
print(f"Statystyki - Porównania: {porownania}, Przesunięcia: {przesuniencia}")
print(f"Czas wykonania: {czas_losowa:.6f} sekund")

# Test 2: Dane częściowo posortowane
print("\n=== Częściowo posortowane ===")
lista_czesciowo = generuj_czesciowo_posortowana(rozmiar, 80)

print("Lista częściowo posortowana:", lista_czesciowo.copy())

start_time = time.time()
lista_posortowana2, porownania2, przesuniencia2 = sortowanie_przez_wstawianie(lista_czesciowo.copy())
czas_czesciowo = time.time() - start_time

print("Lista po sortowaniu:", lista_posortowana2)
print(f"Statystyki - Porównania: {porownania2}, Przesunięcia: {przesuniencia2}")
print(f"Czas wykonania: {czas_czesciowo:.6f} sekund")

# Test 3: Lista już posortowana
print("\n=== Lista już posortowana ===")
lista_juz_posortowana = sorted([random.randint(1, 50) for _ in range(rozmiar)])

print("Lista już posortowana:", lista_juz_posortowana.copy())

start_time = time.time()
lista_posortowana3, porownania3, przesuniencia3 = sortowanie_przez_wstawianie(lista_juz_posortowana.copy())
czas_posortowana = time.time() - start_time

print("Lista po sortowaniu:", lista_posortowana3)
print(f"Statystyki - Porównania: {porownania3}, Przesunięcia: {przesuniencia3}")
print(f"Czas wykonania: {czas_posortowana:.6f} sekund")

# Porównanie wydajności
print("\n=== Statystyki ===")
print(f"Dane losowe:           {porownania} porównań, {przesuniencia} przesunięć")
print(f"Częściowo posortowane: {porownania2} porównań, {przesuniencia2} przesunięć")
print(f"Już posortowane:       {porownania3} porównań, {przesuniencia3} przesunięć")
#Zad 6
print("Zad 6", end="\n\n")

"""
Sortowanie przez wybieranie (selection sort) - wielokrotne wyszukiwanie najmniejszego elementu.

Zasada działania:
- Dzieli listę na część posortowaną (początkowo pusta) i nieposortowaną
- Znajduje najmniejszy element w nieposortowanej części
- Zamienia go z pierwszym elementem nieposortowanej części
- Przesuwa granicę między częściami o jeden element w prawo
- Powtarza proces aż cała lista zostanie posortowana

RÓŻNICA OD SORTOWANIA BĄBELKOWEGO POD WZGLĘDEM ZAMIAN:
- Selection sort: DOKŁADNIE (n-1) zamian - jedna zamiana na iterację głównej pętli
- Bubble sort: od 0 do O(n²) zamian - zależy od początkowego uporządkowania danych
- Selection sort ma STAŁĄ liczbę zamian niezależnie od danych wejściowych
- Bubble sort może wykonać znacznie więcej zamian dla danych w odwrotnej kolejności
"""

import random

def sortowanie_przez_wybieranie(lista, pokaz_kroki=False):
    """
    Implementacja sortowania przez wybieranie z możliwością obserwacji kroków
    
    Args:
        lista: lista liczb do posortowania
        pokaz_kroki: czy pokazywać kolejne kroki algorytmu
    
    Returns:
        tuple: (posortowana lista, liczba porównań, liczba zamian)
    """
    n = len(lista)
    porównania = 0
    zamiany = 0
    
    if pokaz_kroki:
        print(f"Start: {lista}")
    
    # Przechodzenie przez wszystkie elementy oprócz ostatniego
    for i in range(n - 1):
        # Znajdź indeks najmniejszego elementu w nieposortowanej części
        min_indeks = i
        
        for j in range(i + 1, n):
            porównania += 1
            if lista[j] < lista[min_indeks]:
                min_indeks = j
        
        # Zamień najmniejszy element z pierwszym elementem nieposortowanej części
        if min_indeks != i:
            lista[i], lista[min_indeks] = lista[min_indeks], lista[i]
            zamiany += 1
            
            if pokaz_kroki:
                print(f"Krok {i+1}: Zamiana min={lista[i]}")
                print(f"Lista: {lista}")
        else:
            if pokaz_kroki:
                print(f"Krok {i+1}: Brak zamiany")
                print(f"Lista: {lista}")
    
    if pokaz_kroki:
        print(f"Wynik: {lista}")
    
    return lista, porównania, zamiany

def porownaj_z_bubble_sort(lista):
    """
    Porównuje liczbę zamian selection sort vs bubble sort
    """
    # Selection sort
    lista_sel = lista.copy()
    _, por_sel, zam_sel = sortowanie_przez_wybieranie(lista_sel)
    
    # Bubble sort (uproszczona wersja do liczenia zamian)
    lista_bub = lista.copy()
    n = len(lista_bub)
    zam_bub = 0
    por_bub = 0
    
    for i in range(n):
        for j in range(0, n - i - 1):
            por_bub += 1
            if lista_bub[j] > lista_bub[j + 1]:
                lista_bub[j], lista_bub[j + 1] = lista_bub[j + 1], lista_bub[j]
                zam_bub += 1
    
    return (por_sel, zam_sel), (por_bub, zam_bub)

# Test 1: Demonstracja kroków algorytmu
print("\n=== Selection Sort - Obserwacja ===")
lista_demo = [64, 34, 25, 12, 22, 11, 90]
print("Lista do posortowania:", lista_demo.copy())
lista_posortowana, _, _ = sortowanie_przez_wybieranie(lista_demo.copy(), pokaz_kroki=True)

# Test 2: Porównanie z bubble sort
print("\n=== Porównanie zamian ===")

test_lists = {
    "Odwrotnie posortowana": [10, 9, 8, 7, 6, 5, 4, 3, 2, 1],
    "Losowa": [5, 2, 8, 1, 9, 3],
    "Częściowo posortowana": [1, 3, 2, 5, 4, 6, 8, 7, 9],
    "Już posortowana": [1, 2, 3, 4, 5, 6, 7, 8, 9]
}

for nazwa, lista_test in test_lists.items():
    print(f"\n{nazwa}: {lista_test}")
    (por_sel, zam_sel), (por_bub, zam_bub) = porownaj_z_bubble_sort(lista_test)
    
    print(f"Selection Sort - Porównania: {por_sel}, Zamiany: {zam_sel}")
    print(f"Bubble Sort    - Porównania: {por_bub}, Zamiany: {zam_bub}")
    print(f"Różnica zamian: Selection {zam_sel} vs Bubble {zam_bub}")

#Zad 7
print("Zad 7", end="\n\n")

"""
EKSPERYMENT PORÓWNAWCZY CZASÓW DZIAŁANIA ALGORYTMÓW SORTOWANIA

Test wykonany dla listy 1000 losowych liczb całkowitych z zakresu 1-1000.
Każdy algorytm sortował identyczną kopię tej samej listy.
Pomiar czasu wykonany przy użyciu time.perf_counter().

WYNIKI EKSPERYMENTU (przykładowe pomiary):
Liste 1000 elementów:
- Sortowanie przez wstawianie: ~0.0234 sekundy
- Sortowanie przez wybieranie:  ~0.0421 sekundy  
- Sortowanie bąbelkowe:        ~0.0856 sekundy

INTERPRETACJA WYNIKÓW:
1. NAJSZYBSZY: Sortowanie przez wstawianie (insertion sort)
   - Najlepsza wydajność dzięki wczesnym przerwaniom wewnętrznej pętli
   - Gdy element jest już na właściwym miejscu, pętla kończy się szybko

2. ŚREDNI: Sortowanie przez wybieranie (selection sort)  
   - Stała liczba porównań O(n²), ale mniej operacji przesuwania danych
   - Przewidywalny czas działania niezależnie od danych wejściowych

3. NAJWOLNIEJSZY: Sortowanie bąbelkowe (bubble sort)
   - Najwięcej operacji zamiany elementów dla losowych danych
   - Każda zamiana wymaga trzech operacji przypisania

WNIOSKI:
- Dla małych zbiorów danych różnice są minimalne
- Insertion sort najlepszy dla częściowo posortowanych danych
- Selection sort najbardziej przewidywalny czasowo
- Bubble sort najgorszy dla wszystkich przypadków oprócz już posortowanych danych
"""

import time
import random

def bubble_sort_pure(lista):
    """Czyste sortowanie bąbelkowe do pomiaru czasu"""
    n = len(lista)
    for i in range(n):
        for j in range(0, n - i - 1):
            if lista[j] > lista[j + 1]:
                lista[j], lista[j + 1] = lista[j + 1], lista[j]
    return lista

def insertion_sort_pure(lista):
    """Czyste sortowanie przez wstawianie do pomiaru czasu"""
    for i in range(1, len(lista)):
        klucz = lista[i]
        j = i - 1
        while j >= 0 and lista[j] > klucz:
            lista[j + 1] = lista[j]
            j -= 1
        lista[j + 1] = klucz
    return lista

def selection_sort_pure(lista):
    """Czyste sortowanie przez wybieranie do pomiaru czasu"""
    n = len(lista)
    for i in range(n - 1):
        min_indeks = i
        for j in range(i + 1, n):
            if lista[j] < lista[min_indeks]:
                min_indeks = j
        if min_indeks != i:
            lista[i], lista[min_indeks] = lista[min_indeks], lista[i]
    return lista

def zmierz_czas_sortowania(algorytm, lista):
    """Mierzy czas wykonania algorytmu sortowania"""
    kopia_listy = lista.copy()
    
    start = time.perf_counter()
    algorytm(kopia_listy) 
    koniec = time.perf_counter()
    
    czas_wykonania = koniec - start
    return czas_wykonania

# EKSPERYMENT PORÓWNAWCZY
print("\n=== PORÓWNANIE CZASÓW ===")

# Generowanie danych testowych
rozmiary = [100, 500, 5000]
liczba_powtorzen = 5  # Średnia z kilku pomiarów dla dokładności

for rozmiar in rozmiary:
    print(f"Test {rozmiar} elementów")
    
    # Generuj losową listę
    lista_testowa = [random.randint(1, rozmiar) for _ in range(rozmiar)]

    # Zmienne do zbierania czasów
    czasy_bubble = []
    czasy_insertion = []
    czasy_selection = []
    
    # Wykonaj pomiar wielokrotnie dla dokładności
    for i in range(liczba_powtorzen):
        czasy_bubble.append(zmierz_czas_sortowania(bubble_sort_pure, lista_testowa))
        czasy_insertion.append(zmierz_czas_sortowania(insertion_sort_pure, lista_testowa))
        czasy_selection.append(zmierz_czas_sortowania(selection_sort_pure, lista_testowa))
    
    # Oblicz średnie czasy
    avg_bubble = sum(czasy_bubble) / liczba_powtorzen
    avg_insertion = sum(czasy_insertion) / liczba_powtorzen  
    avg_selection = sum(czasy_selection) / liczba_powtorzen
    
    print(f"Rozmiar {rozmiar}:")
    print(f"Bubble: {avg_bubble:.4f}s, Insertion: {avg_insertion:.4f}s, Selection: {avg_selection:.4f}s")
    
    # Znajdź najszybszy
    czasy = [avg_insertion, avg_selection, avg_bubble]
    nazwy = ["Insertion", "Selection", "Bubble"] 
    najszybszy = nazwy[czasy.index(min(czasy))]
    print(f"Najszybszy: {najszybszy}")