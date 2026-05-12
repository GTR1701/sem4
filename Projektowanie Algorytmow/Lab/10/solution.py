import random

tytuly = [
    "Pan Tadeusz", "Lalka", "Quo Vadis", "Potop", "Wesele",
    "Chłopi", "Faraon", "Zbrodnia i kara", "Mistrz i Małgorzata",
    "Władca Pierścieni", "Hobbit", "Duma i uprzedzenie", "Frankenstein",
    "Moby Dick", "Wielki Gatsby", "Zbrodnia i kara", "Don Kichot",
    "Odyseja", "Iliada", "Faust"
]

autorzy = [
    "Adam Mickiewicz", "Bolesław Prus", "Henryk Sienkiewicz",
    "Stanisław Wyspiański", "Władysław Reymont", "Fiodor Dostojewski",
    "Michaił Bułhakow", "J.R.R. Tolkien", "Jane Austen",
    "Mary Shelley", "Herman Melville", "F. Scott Fitzgerald",
    "Miguel de Cervantes", "Homer", "Johann Wolfgang von Goethe"
]


def generuj_ksiazki(n):
    ksiazki = []
    for i in range(n):
        tytul = random.choice(tytuly)
        autor = random.choice(autorzy)
        rok = random.randint(1700, 2026)
        dostepna = random.randint(0, 1)
        ksiazka = (tytul, autor, rok, dostepna)
        ksiazki.append(ksiazka)
    return ksiazki


def wyswietl_ksiazki(ksiazki):
    print(f"{'Nr':<4} {'Tytuł':<35} {'Autor':<30} {'Rok':<6} {'Dostępna'}")
    print("-" * 85)
    for i, ksiazka in enumerate(ksiazki, 1):
        tytul, autor, rok, dostepna = ksiazka
        status = "TAK" if dostepna == 1 else "NIE"
        print(f"{i:<4} {tytul:<35} {autor:<30} {rok:<6} {status}")


def zapisz_do_pliku(ksiazki, nazwa_pliku):
    with open(nazwa_pliku, "w", encoding="utf-8") as plik:
        for ksiazka in ksiazki:
            tytul, autor, rok, dostepna = ksiazka
            linia = f"{tytul};{autor};{rok};{dostepna}\n"
            plik.write(linia)
    print(f"Zapisano {len(ksiazki)} książek do pliku '{nazwa_pliku}'.")


def wczytaj_z_pliku(nazwa_pliku):
    ksiazki = []
    with open(nazwa_pliku, "r", encoding="utf-8") as plik:
        for linia in plik:
            linia = linia.strip()
            czesci = linia.split(";")
            tytul = czesci[0]
            autor = czesci[1]
            rok = int(czesci[2])
            dostepna = int(czesci[3])
            ksiazka = (tytul, autor, rok, dostepna)
            ksiazki.append(ksiazka)
    return ksiazki


# --- Stos książek ---

stos = []


def wypisz_ksiazke(ksiazka):
    tytul, autor, rok, dostepna = ksiazka
    status = "TAK" if dostepna == 1 else "NIE"
    print(f"  Tytuł: {tytul}, Autor: {autor}, Rok: {rok}, Dostępna: {status}")


def push(stos):
    tytul = input("Podaj tytuł: ")
    autor = input("Podaj autora: ")
    rok = int(input("Podaj rok: "))
    dostepna = int(input("Dostępna? (1=TAK, 0=NIE): "))
    ksiazka = (tytul, autor, rok, dostepna)
    stos.append(ksiazka)
    print("Książka dodana na stos.")


def pop(stos):
    if len(stos) == 0:
        print("Stos jest pusty!")
    else:
        ksiazka = stos.pop()
        print("Zdjęto ze stosu:")
        wypisz_ksiazke(ksiazka)


def clear(stos):
    if len(stos) == 0:
        print("Stos jest już pusty.")
    else:
        print("Opróżnianie stosu:")
        while len(stos) > 0:
            ksiazka = stos.pop()
            wypisz_ksiazke(ksiazka)
        print("Stos opróżniony.")


def wyswietl_stos(stos):
    if len(stos) == 0:
        print("Stos jest pusty.")
    else:
        print(f"Stos ({len(stos)} książek, góra na końcu):")
        for i, ksiazka in enumerate(stos, 1):
            print(f"  {i}.", end=" ")
            wypisz_ksiazke(ksiazka)


# --- Zadanie 1 ---

def zadanie1():
    n = int(input("Podaj liczbę książek do wygenerowania: "))
    ksiazki = generuj_ksiazki(n)

    print("\n=== Lista wygenerowanych książek ===")
    wyswietl_ksiazki(ksiazki)

    nazwa_pliku = "ksiazki.txt"
    zapisz_do_pliku(ksiazki, nazwa_pliku)

    print("\n=== Odczyt z pliku ===")
    wczytane = wczytaj_z_pliku(nazwa_pliku)
    wyswietl_ksiazki(wczytane)


# --- Zadanie 2 ---

def zadanie2():
    stos = []

    while True:
        print("\n=== STOS KSIĄŻEK ===")
        print("1. Push (dodaj książkę)")
        print("2. Pop (zdejmij książkę)")
        print("3. Clear (opróżnij stos)")
        print("4. Wyświetl stos")
        print("5. Powrót do menu głównego")

        wybor = input("Wybierz opcję: ")

        if wybor == "1":
            push(stos)
        elif wybor == "2":
            pop(stos)
        elif wybor == "3":
            clear(stos)
        elif wybor == "4":
            wyswietl_stos(stos)
        elif wybor == "5":
            break
        else:
            print("Nieznana opcja.")


# --- Zadanie 3 ---

def enqueue(kolejka):
    tytul = input("Podaj tytuł: ")
    autor = input("Podaj autora: ")
    rok = int(input("Podaj rok: "))
    dostepna = int(input("Dostępna? (1=TAK, 0=NIE): "))
    ksiazka = (tytul, autor, rok, dostepna)
    kolejka.append(ksiazka)
    print("Książka dodana do kolejki.")


def dequeue(kolejka):
    if len(kolejka) == 0:
        print("Kolejka jest pusta!")
    else:
        ksiazka = kolejka.pop(0)
        print("Obsłużono (usunięto z początku kolejki):")
        wypisz_ksiazke(ksiazka)


def clear_kolejka(kolejka):
    if len(kolejka) == 0:
        print("Kolejka jest już pusta.")
    else:
        print("Opróżnianie kolejki:")
        while len(kolejka) > 0:
            ksiazka = kolejka.pop(0)
            wypisz_ksiazke(ksiazka)
        print("Kolejka opróżniona.")


def wyswietl_kolejke(kolejka):
    if len(kolejka) == 0:
        print("Kolejka jest pusta.")
    else:
        print(f"Kolejka ({len(kolejka)} książek, pierwszy na początku):")
        for i, ksiazka in enumerate(kolejka, 1):
            print(f"  {i}.", end=" ")
            wypisz_ksiazke(ksiazka)


def zadanie3():
    kolejka = []

    while True:
        print("\n=== KOLEJKA WYPOŻYCZALNI ===")
        print("1. Enqueue (dodaj książkę do kolejki)")
        print("2. Dequeue (obsłuż pierwszą książkę)")
        print("3. Clear (opróżnij kolejkę)")
        print("4. Wyświetl kolejkę")
        print("5. Powrót do menu głównego")

        wybor = input("Wybierz opcję: ")

        if wybor == "1":
            enqueue(kolejka)
        elif wybor == "2":
            dequeue(kolejka)
        elif wybor == "3":
            clear_kolejka(kolejka)
        elif wybor == "4":
            wyswietl_kolejke(kolejka)
        elif wybor == "5":
            break
        else:
            print("Nieznana opcja.")


# --- Zadanie 4 ---

class Node:
    def __init__(self, ksiazka):
        self.ksiazka = ksiazka
        self.nastepny = None


class LinkedList:
    def __init__(self):
        self.head = None

    def klucz(self, ksiazka):
        tytul, autor, rok, dostepna = ksiazka
        return f"{tytul}_{rok}"

    def dodaj(self, ksiazka):
        nowy = Node(ksiazka)
        nowy.nastepny = self.head
        self.head = nowy
        print(f"Dodano książkę (klucz: {self.klucz(ksiazka)}).")

    def usun(self, szukany_klucz):
        aktualny = self.head
        poprzedni = None
        while aktualny is not None:
            if self.klucz(aktualny.ksiazka) == szukany_klucz:
                if poprzedni is None:
                    self.head = aktualny.nastepny
                else:
                    poprzedni.nastepny = aktualny.nastepny
                print("Usunięto książkę:")
                wypisz_ksiazke(aktualny.ksiazka)
                return
            poprzedni = aktualny
            aktualny = aktualny.nastepny
        print(f"Nie znaleziono książki o kluczu '{szukany_klucz}'.")

    def szukaj(self, szukany_klucz):
        aktualny = self.head
        while aktualny is not None:
            if self.klucz(aktualny.ksiazka) == szukany_klucz:
                print("Znaleziono książkę:")
                wypisz_ksiazke(aktualny.ksiazka)
                return
            aktualny = aktualny.nastepny
        print(f"Nie znaleziono książki o kluczu '{szukany_klucz}'.")

    def wyswietl(self):
        if self.head is None:
            print("Lista jest pusta.")
            return
        aktualny = self.head
        i = 1
        while aktualny is not None:
            print(f"  {i}. [klucz: {self.klucz(aktualny.ksiazka)}]", end=" ")
            wypisz_ksiazke(aktualny.ksiazka)
            aktualny = aktualny.nastepny
            i += 1


def zadanie4():
    lista = LinkedList()

    while True:
        print("\n=== LISTA Z DOWIĄZANIAMI ===")
        print("1. Dodaj książkę")
        print("2. Usuń książkę (po kluczu tytuł_rok)")
        print("3. Wyszukaj książkę (po kluczu tytuł_rok)")
        print("4. Wyświetl listę")
        print("5. Powrót do menu głównego")

        wybor = input("Wybierz opcję: ")

        if wybor == "1":
            tytul = input("Podaj tytuł: ")
            autor = input("Podaj autora: ")
            rok = int(input("Podaj rok: "))
            dostepna = int(input("Dostępna? (1=TAK, 0=NIE): "))
            lista.dodaj((tytul, autor, rok, dostepna))
        elif wybor == "2":
            klucz = input("Podaj klucz (tytuł_rok): ")
            lista.usun(klucz)
        elif wybor == "3":
            klucz = input("Podaj klucz (tytuł_rok): ")
            lista.szukaj(klucz)
        elif wybor == "4":
            lista.wyswietl()
        elif wybor == "5":
            break
        else:
            print("Nieznana opcja.")


# --- Zadanie 5 ---

class UnionFind:
    def __init__(self, dzialy):
        # każdy dział jest swoim własnym rodzicem na początku
        self.rodzic = {}
        self.ranga = {}
        for dzial in dzialy:
            self.rodzic[dzial] = dzial
            self.ranga[dzial] = 0

    def znajdz(self, x):
        # znajdowanie korzenia z kompresją ścieżki
        if self.rodzic[x] != x:
            self.rodzic[x] = self.znajdz(self.rodzic[x])
        return self.rodzic[x]

    def polacz(self, x, y):
        kx = self.znajdz(x)
        ky = self.znajdz(y)
        if kx == ky:
            return  # już w tej samej grupie
        # łączenie po randze
        if self.ranga[kx] < self.ranga[ky]:
            kx, ky = ky, kx
        self.rodzic[ky] = kx
        if self.ranga[kx] == self.ranga[ky]:
            self.ranga[kx] += 1

    def czy_razem(self, x, y):
        return self.znajdz(x) == self.znajdz(y)

    def skladowe(self):
        grupy = {}
        for dzial in self.rodzic:
            korzen = self.znajdz(dzial)
            if korzen not in grupy:
                grupy[korzen] = []
            grupy[korzen].append(dzial)
        return list(grupy.values())


def zadanie5():
    print("\nPodaj działy biblioteki (oddzielone przecinkami):")
    print("Przykład: Historia, Matematyka, Fantastyka, Biologia, Fizyka")
    wejscie = input("> ")
    dzialy = [d.strip() for d in wejscie.split(",")]

    uf = UnionFind(dzialy)

    print("\nPodaj krawędzie grafu (wspólne zasoby) w formacie: DziałA DziałB")
    print("Wpisz 'koniec' aby zakończyć podawanie krawędzi.")
    while True:
        krawedz = input("Krawędź: ")
        if krawedz.strip().lower() == "koniec":
            break
        czesci = krawedz.strip().split()
        if len(czesci) != 2:
            print("Podaj dokładnie dwie nazwy działów oddzielone spacją.")
            continue
        a, b = czesci[0], czesci[1]
        if a not in uf.rodzic or b not in uf.rodzic:
            print("Nieznany dział. Dostępne:", ", ".join(dzialy))
            continue
        uf.polacz(a, b)
        print(f"Połączono '{a}' i '{b}'.")

    print("\n=== SPÓJNE SKŁADOWE ===")
    for i, grupa in enumerate(uf.skladowe(), 1):
        print(f"Składowa {i}: {', '.join(grupa)}")

    print("\n=== ZAPYTANIA O PRZYNALEŻNOŚĆ ===")
    print("Wpisz dwa działy oddzielone spacją, aby sprawdzić czy są w tej samej grupie.")
    print("Wpisz 'koniec' aby wrócić do menu.")
    while True:
        zapytanie = input("Zapytanie: ")
        if zapytanie.strip().lower() == "koniec":
            break
        czesci = zapytanie.strip().split()
        if len(czesci) != 2:
            print("Podaj dokładnie dwie nazwy działów.")
            continue
        a, b = czesci[0], czesci[1]
        if a not in uf.rodzic or b not in uf.rodzic:
            print("Nieznany dział. Dostępne:", ", ".join(dzialy))
            continue
        if uf.czy_razem(a, b):
            print(f"TAK – '{a}' i '{b}' należą do tej samej spójnej grupy.")
        else:
            print(f"NIE – '{a}' i '{b}' są w różnych grupach.")


# --- Menu główne ---

while True:
    print("\n=== BIBLIOTEKA - WYBIERZ ZADANIE ===")
    print("1. Zadanie 1 - Generowanie i zapis katalogu książek")
    print("2. Zadanie 2 - Stos książek")
    print("3. Zadanie 3 - Kolejka wypożyczalni")
    print("4. Zadanie 4 - Lista z dowiązaniami")
    print("5. Zadanie 5 - Zbiory rozłączne (Union-Find)")
    print("6. Wyjście")

    wybor = input("Wybierz zadanie: ")

    if wybor == "1":
        zadanie1()
    elif wybor == "2":
        zadanie2()
    elif wybor == "3":
        zadanie3()
    elif wybor == "4":
        zadanie4()
    elif wybor == "5":
        zadanie5()
    elif wybor == "6":
        break
    else:
        print("Nieznana opcja.")
