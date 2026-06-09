# lab 13 - DFS, klasyfikacja krawędzi, sortowanie topologiczne, Kruskal
# wnioski z testów są jako komentarze przy każdym grafie w main()

import sys
import os
from collections import defaultdict

sys.setrecursionlimit(10000)

# standardowe kolory DFS: biały = nieodwiedzony, szary = w trakcie, czarny = gotowy
BIALY, SZARY, CZARNY = 0, 1, 2


# union-find - potrzebne do Kruskala żeby sprawdzać czy krawędż tworzy cykl

class ZbiorRozlaczny:
    """union-find z kompresją ścieżki i łączeniem po randze"""

    def __init__(self, n):
        # na początku każdy element jest swoim własnym rodzicem
        self.rodzic = list(range(n))
        self.ranga = [0] * n

    def znajdz(self, x):
        # przy okazji spłaszczamy drzewo (kompresja ścieżki)
        if self.rodzic[x] != x:
            self.rodzic[x] = self.znajdz(self.rodzic[x])
        return self.rodzic[x]

    def polacz(self, x, y):
        # łączy dwa zbiory, zwraca False jeśli już są w jednym (czyli byłby cykl)
        rx, ry = self.znajdz(x), self.znajdz(y)
        if rx == ry:
            return False
        if self.ranga[rx] < self.ranga[ry]:
            rx, ry = ry, rx
        self.rodzic[ry] = rx
        if self.ranga[rx] == self.ranga[ry]:
            self.ranga[rx] += 1
        return True


# wczytywanie grafu z pliku

def wczytaj_graf(sciezka):
    """
    Wczytuje graf z pliku. Format:
      linia 1: directed albo undirected
      linia 2: n m
      linie 3+: u v [waga]  (wierzchołki od 1)
    """
    with open(sciezka, 'r', encoding='utf-8') as f:
        linie = [l.strip() for l in f if l.strip() and not l.startswith('#')]

    typ = linie[0].lower()          # directed albo undirected
    n, m = map(int, linie[1].split())

    lista_sasiedztwa = {i: [] for i in range(1, n + 1)}
    krawedzie = []

    for i in range(2, 2 + m):
        czesci = linie[i].split()
        u, v = int(czesci[0]), int(czesci[1])
        w = float(czesci[2]) if len(czesci) > 2 else 1.0
        lista_sasiedztwa[u].append((v, w))
        krawedzie.append((u, v, w))
        if typ == 'undirected':
            lista_sasiedztwa[v].append((u, w))

    return {
        'typ': typ,
        'n': n,
        'wierzcholki': list(range(1, n + 1)),
        'lista_sasiedztwa': lista_sasiedztwa,
        'krawedzie': krawedzie,
    }


# DFS z jednego źródła

def dfs(graf, start, verbose=True):
    """
    DFS od wierzchołka start - liczy czasy odkrycia/zakończenia i poprzedniki.
    Wypisuje kroki jeśli verbose=True. Na końcu mówi czy obejście było pełne.
    """
    sasiedzi = graf['lista_sasiedztwa']
    kolor = {v: BIALY for v in graf['wierzcholki']}
    odkrycie = {}
    zakonczenie = {}
    poprzednik = {v: None for v in graf['wierzcholki']}
    kolejnosc = []
    czas = [0]

    if verbose:
        print(f"\n{'─'*55}")
        print(f"  DFS od wierzchołka {start}")
        print(f"{'─'*55}")

    def odwiedz(u):
        # rekurencja - wchodzimy i liczymy czas, potem wychodzimy i znow liczymy
        kolor[u] = SZARY
        czas[0] += 1
        odkrycie[u] = czas[0]
        kolejnosc.append(u)
        if verbose:
            print(f"  WEJŚCIE  {u:>3}   d[{u}]={czas[0]:>2}   "
                  f"odwiedzone dotąd: {kolejnosc}")
        for v, _ in sasiedzi[u]:
            if kolor[v] == BIALY:
                poprzednik[v] = u
                odwiedz(v)
        kolor[u] = CZARNY
        czas[0] += 1
        zakonczenie[u] = czas[0]
        if verbose:
            print(f"  WYJŚCIE  {u:>3}   d[{u}]={odkrycie[u]:>2}   "
                  f"f[{u}]={czas[0]:>2}")

    odwiedz(start)

    nieodwiedzone = [v for v in graf['wierzcholki'] if kolor[v] == BIALY]

    if verbose:
        print(f"\n  Kolejność odwiedzin : {kolejnosc}")
        print(f"  Czasy odkrycia  d[] : {odkrycie}")
        print(f"  Czasy zakończenia f[]: {zakonczenie}")
        print(f"  Poprzednicy         : "
              f"{ {v: p for v, p in poprzednik.items() if p is not None} }")
        if nieodwiedzone:
            # wierzchołki nieosiągalne ze źródła - graf niespójny lub krawędzie jednokierunkowe
            print(f"\n  Nieodwiedzone: {nieodwiedzone}")
            print("  => Jeden DFS nie wystarczył - graf jest niespójny\n"
                  "     lub część wierzchołków jest nieosiągalna ze źródła.")
            print("  => Kolejność sąsiadów wpływa na wartości d/f,\n"
                  "     ale nie zmienia zbioru osiągalnych wierzchołków.")
        else:
            # wszystkie wierzchołki odwiedzone jednym drzewem DFS
            print("\n  => Jeden DFS wystarczył - graf jest (silnie) spójny\n"
                  "     lub wszystkie wierzchołki są osiągalne ze źródła.")
            print("  => Zmiana kolejności sąsiadów wpływa na kształt drzewa DFS\n"
                  "     i wartości d/f, ale zbiór odwiedzonych wierzchołków pozostaje ten sam.")

    return {
        'kolejnosc': kolejnosc,
        'odkrycie': odkrycie,
        'zakonczenie': zakonczenie,
        'poprzednik': poprzednik,
        'nieodwiedzone': nieodwiedzone,
    }


# pełne DFS - odwiedza wszystkie wierzchołki, nawet jeśli graf niespojny

def pelne_dfs(graf, verbose=True):
    """
    DFS dla całego grafu - startuje od każdego nieodwiedzonego wierzchołka.
    Przy okazji klasyfikuje krawędzie.
    """
    sasiedzi = graf['lista_sasiedztwa']
    typ_grafu = graf['typ']
    kolor = {v: BIALY for v in graf['wierzcholki']}
    odkrycie = {}
    zakonczenie = {}
    poprzednik = {v: None for v in graf['wierzcholki']}
    kolejnosc = []
    krawedzie_klas = []   # (u, v, typ_krawedzi)
    czas = [0]
    liczba_wizyt = [0]   # licznik uruchomień DFS-WIZYTA

    if verbose:
        print(f"\n{'─'*55}")
        print("  Pełne DFS (wszystkie wierzchołki)")
        print(f"{'─'*55}")

    def odwiedz(u):
        # rekurencja - liczymy czasy wejścia/wyjścia i przy okazji klasyfikujemy krawędzie
        liczba_wizyt[0] += 1
        kolor[u] = SZARY
        czas[0] += 1
        odkrycie[u] = czas[0]
        kolejnosc.append(u)
        if verbose:
            print(f"  WEJŚCIE  {u:>3}   d[{u}]={czas[0]:>2}")

        for v, _ in sasiedzi[u]:
            # w grafie nieskierowanym nie chcemy iść z powrotem do rodzica
            if typ_grafu == 'undirected' and poprzednik[u] == v:
                continue
            if kolor[v] == BIALY:
                poprzednik[v] = u
                krawedzie_klas.append((u, v, 'drzewowa'))
                odwiedz(v)
            elif kolor[v] == SZARY:
                # v jest szary - jesteśmy w trakcie jego odwiedzania, więc mamy cykl
                krawedzie_klas.append((u, v, 'wsteczna'))
            elif odkrycie[u] < odkrycie[v]:
                # v odkryty później niż u, ale już czarny - krawędź w przód (tylko skierowane)
                krawedzie_klas.append((u, v, 'wprzod'))
            else:
                # v leży w innym poddrzewie lasu DFS - krawędź poprzeczna
                krawedzie_klas.append((u, v, 'poprzeczna'))

        kolor[u] = CZARNY
        czas[0] += 1
        zakonczenie[u] = czas[0]
        if verbose:
            print(f"  WYJŚCIE  {u:>3}   d[{u}]={odkrycie[u]:>2}   "
                  f"f[{u}]={czas[0]:>2}")

    for v in graf['wierzcholki']:
        if kolor[v] == BIALY:
            if verbose:
                print(f"\n  [Nowe drzewo DFS zaczyna się od wierzchołka {v}]")
            odwiedz(v)

    # szukamy korzeni - idziemy w górę po poprzednikach
    drzewa = {}
    for v in graf['wierzcholki']:
        korzen = v
        while poprzednik[korzen] is not None:
            korzen = poprzednik[korzen]
        drzewa.setdefault(korzen, []).append(v)

    if verbose:
        print(f"\n  Globalna kolejność odwiedzin: {kolejnosc}")
        print(f"  Czasy d[]: {odkrycie}")
        print(f"  Czasy f[]: {zakonczenie}")
        print(f"\n  Las DFS - drzewa (korzeń → wierzchołki):")
        for korzen, wierz in sorted(drzewa.items()):
            print(f"    Korzeń {korzen}: {sorted(wierz)}")
        # liczba wizyt = ile razy wywołano odwiedz()
        print(f"  Liczba uruchomień DFS-WIZYTA: {liczba_wizyt[0]}")

    return {
        'kolejnosc': kolejnosc,
        'odkrycie': odkrycie,
        'zakonczenie': zakonczenie,
        'poprzednik': poprzednik,
        'krawedzie_klas': krawedzie_klas,
        'drzewa': drzewa,
        'liczba_wizyt': liczba_wizyt[0],
    }


# klasyfikacja krawędzi - używa pelne_dfs pod spodem

def klasyfikuj_krawedzie(graf, verbose=True):
    """
    Klasyfikuje krawędzie po uruchomieniu pelne_dfs.
    Typy: drzewowa, wsteczna, wprzod (tylko skierowane), poprzeczna (tylko skierowane).
    """
    wynik = pelne_dfs(graf, verbose=False)
    klas = {'drzewowa': [], 'wsteczna': [], 'wprzód': [], 'poprzeczna': []}
    for u, v, typ in wynik['krawedzie_klas']:
        klas[typ].append((u, v))

    if verbose:
        print(f"\n{'─'*55}")
        print("  Klasyfikacja krawędzi")
        print(f"{'─'*55}")
        for typ, lista in klas.items():
            if lista:
                print(f"  {typ.capitalize():<13}: {lista}")
        # krawędź wsteczna w grafie skierowanym oznacza istnienie cyklu
        if klas['wsteczna'] and graf['typ'] == 'directed':
            print("  => Wykryto krawędzie wsteczne - graf zawiera cykl.")
        elif not klas['wsteczna']:
            print("  => Brak krawędzi wstecznych - graf jest acykliczny.")
        # w grafach nieskierowanych nie występują krawędzie w przód ani poprzeczne
        if graf['typ'] == 'undirected':
            print("  (W grafach nieskierowanych występują tylko krawędzie drzewowe i wsteczne.)")

    return klas


# sortowanie topologiczne

def sortowanie_topologiczne(graf, verbose=True):
    """
    Sortuje wierzchołki DAGa metodą DFS - wrzucamy na stos po zakończeniu.
    Jeśli trafi się krawędź wsteczna to graf ma cykl i zwracamy None.
    """
    if graf['typ'] != 'directed':
        if verbose:
            print("  Sortowanie topologiczne: tylko dla grafów skierowanych.")
        return None

    sasiedzi = graf['lista_sasiedztwa']
    kolor = {v: BIALY for v in graf['wierzcholki']}
    wynik = []
    cykl = [False]

    if verbose:
        print(f"\n{'─'*55}")
        print("  Sortowanie topologiczne")
        print(f"{'─'*55}")

    def odwiedz(u):
        # po zakończeniu u dajemy go na stos - stąd bierzemy wynik w odwrotnej kolejności
        if cykl[0]:
            return
        kolor[u] = SZARY
        for v, _ in sasiedzi[u]:
            if cykl[0]:                          # zatrzymaj gdy cykl już wykryty
                break
            if kolor[v] == BIALY:
                odwiedz(v)
            elif kolor[v] == SZARY:
                # v jest szary - jesteśmy w środku jego odwiedzania, a więc mamy cykl
                cykl[0] = True
                if verbose:
                    print(f"  Wykryto krawędź wsteczną: {u} → {v}")
                break
        if not cykl[0]:                          # wrzucamy na stos po zakończeniu przetwarzania u
            kolor[u] = CZARNY
            wynik.append(u)
            if verbose:
                print(f"  Zakończono {u:>3},  stos (od góry): {list(reversed(wynik))}")

    for v in graf['wierzcholki']:
        if kolor[v] == BIALY and not cykl[0]:
            odwiedz(v)

    if cykl[0]:
        if verbose:
            print("  => Graf zawiera cykl - sortowanie topologiczne niemożliwe.")
        return None

    topo = list(reversed(wynik))
    if verbose:
        print(f"\n  Kolejność topologiczna: {topo}")
        # weryfikacja - każda krawędź u->v powinna mieć u wcześniej niż v w porządku
        poz = {v: i for i, v in enumerate(topo)}
        ok = all(poz[u] < poz[v] for u, v, _ in graf['krawedzie'])
        print(f"  Weryfikacja (każda krawędź u→v ma poz[u]<poz[v]): {'TAK' if ok else 'NIE'}")
    return topo


# algorytm Kruskala - minimalne drzewo rozpinające

def kruskal(graf, verbose=True):
    """
    Kruskal - MST dla grafu nieskierowanego.
    Sortujemy krawędzie rosnąco po wadze i dodajemy je jeśli nie tworzą cyklu.
    Do sprawdzania cykli używamy union-find.
    """
    if graf['typ'] != 'undirected':
        if verbose:
            print("  Kruskal: tylko dla grafów nieskierowanych.")
        return None

    wierzcholki = graf['wierzcholki']
    idx = {v: i for i, v in enumerate(wierzcholki)}

    # w liście sąsiedztwa każda krawędź pojawia się dwa razy - deduplikacja
    widziane = set()
    unikalne = []
    for u, v, w in graf['krawedzie']:
        klucz = (min(u, v), max(u, v))
        if klucz not in widziane:
            widziane.add(klucz)
            unikalne.append((w, u, v))

    krawedzie_sort = sorted(unikalne)
    zb = ZbiorRozlaczny(len(wierzcholki))
    mst = []
    waga = 0.0

    if verbose:
        print(f"\n{'─'*55}")
        print("  Algorytm Kruskala")
        print(f"{'─'*55}")
        print(f"  Krawędzie wg rosnącej wagi: "
              f"{[(u, v, w) for w, u, v in krawedzie_sort]}")

    for w, u, v in krawedzie_sort:
        if zb.polacz(idx[u], idx[v]):
            mst.append((u, v, w))
            waga += w
            if verbose:
                print(f"  DODANO    ({u},{v},{w:.1f})  |  MST waga = {waga:.1f}  "
                      f"|  krawędzie MST: {mst}")
        else:
            if verbose:
                print(f"  POMINIĘTO ({u},{v},{w:.1f})  -  tworzyłaby cykl")

    if verbose:
        print(f"\n  MST końcowe : {mst}")
        print(f"  Łączna waga : {waga:.1f}")
        n = len(wierzcholki)
        # MST powinno mieć dokładnie n-1 krawędzi; mniej oznacza niespójny graf
        print(f"  Liczba krawędzi MST: {len(mst)}  (wymagane |V|-1 = {n-1}): "
              f"{'OK' if len(mst) == n - 1 else 'BŁĄD - graf może być niespójny'}")
    return {'mst': mst, 'waga': waga}


# =============================================================================
# TWORZENIE PLIKÓW TESTOWYCH
# =============================================================================

def utworz_pliki_testowe(katalog):
    """tworzy pliki z grafami testowymi jeśli nie istnieją"""
    os.makedirs(katalog, exist_ok=True)

    pliki = {
        # spójny skierowany - cykl 2->4->5->2, krawędź 3->4 wyjdzie jako poprzeczna
        'spojny_skierowany.txt': (
            "directed\n5 6\n1 2\n1 3\n2 4\n3 4\n4 5\n5 2\n"
        ),
        # trzy osobne składowe - dobre do testowania niespojności
        'niespojny.txt': (
            "directed\n7 4\n1 2\n2 3\n4 5\n6 7\n"
        ),
        # DAG bez żadnego cyklu - sort topo powinien działać
        'dag.txt': (
            "directed\n6 7\n1 2\n1 3\n2 4\n3 4\n4 5\n3 6\n5 6\n"
        ),
        # ten sam kształt co dag ale z krawędzią 4->2 zamykającą cykl
        'z_cyklem.txt': (
            "directed\n4 5\n1 2\n2 3\n3 4\n4 2\n1 4\n"
        ),
        # ważony nieskierowany do Kruskala, oczekiwana waga MST = 11
        'wazony_nieskierowany.txt': (
            "undirected\n6 9\n"
            "1 2 4\n1 3 3\n2 3 1\n2 4 2\n3 5 5\n"
            "4 5 7\n4 6 3\n5 6 2\n1 6 8\n"
        ),
    }

    for nazwa, zawartosc in pliki.items():
        sciezka = os.path.join(katalog, nazwa)
        with open(sciezka, 'w', encoding='utf-8') as f:
            f.write(zawartosc)

    print(f"Pliki testowe zapisane w: {katalog}")


# tutaj wszystko się uruchamia

def main():
    """odpala testy na wszystkich pięciu grafach"""
    katalog = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'grafy')
    utworz_pliki_testowe(katalog)

    SEP = '═' * 65

    # -------------------------------------------------------------------
    # graf 1: spójny skierowany, cykl 2->4->5->2
    # DFS od 1 odwiedza wszystkie wierzchołki jednym drzewem
    # zmiana kolejności sąsiadów zmieni czasy d/f, ale nie zbiór odwiedzonych
    # -------------------------------------------------------------------
    print(f"\n{SEP}")
    print("  GRAF 1 - Spójny skierowany z cyklem 2→4→5→2")
    print(SEP)
    g1 = wczytaj_graf(os.path.join(katalog, 'spojny_skierowany.txt'))
    print(f"  Typ: {g1['typ']} | wierzchołki: {g1['wierzcholki']}")
    print(f"  Krawędzie: {[(u, v) for u, v, _ in g1['krawedzie']]}")
    dfs(g1, start=1)
    klasyfikuj_krawedzie(g1)
    sortowanie_topologiczne(g1)   # niemożliwe - graf zawiera cykl 2->4->5->2

    # -------------------------------------------------------------------
    # graf 2: niespójny - trzy składowe {1,2,3}, {4,5}, {6,7}
    # dfs(start=1) widzi tylko {1,2,3}, pozostałe wierzchołki zostają białe
    # pelne_dfs() uruchamia się osobno dla każdej składowej -> las DFS z 3 drzewami
    # łączna liczba wywołań odwiedz() = 7 = |V|
    # -------------------------------------------------------------------
    print(f"\n{SEP}")
    print("  GRAF 2 - Niespójny (składowe: {1,2,3}, {4,5}, {6,7})")
    print(SEP)
    g2 = wczytaj_graf(os.path.join(katalog, 'niespojny.txt'))
    print(f"  Typ: {g2['typ']} | wierzchołki: {g2['wierzcholki']}")
    dfs(g2, start=1)              # obejmie tylko {1,2,3}, reszta nieosiągalna
    pelne_dfs(g2)                 # trzy drzewa DFS, łącznie 7 wywołań odwiedz()

    # -------------------------------------------------------------------
    # graf 3: DAG, brak cyklu
    # krawędź 3->4 będzie poprzeczna, bo 4 jest już odwiedzone przez 2->4
    # oczekiwana kolejność topologiczna: 1, 3, 2, 4, 5, 6
    # -------------------------------------------------------------------
    print(f"\n{SEP}")
    print("  GRAF 3 - DAG (skierowany acykliczny, 6 wierzchołków)")
    print(SEP)
    g3 = wczytaj_graf(os.path.join(katalog, 'dag.txt'))
    print(f"  Typ: {g3['typ']} | wierzchołki: {g3['wierzcholki']}")
    dfs(g3, start=1)
    klasyfikuj_krawedzie(g3)
    sortowanie_topologiczne(g3)   # powinno się powieść - brak cyklu

    # -------------------------------------------------------------------
    # graf 4: skierowany z cyklem 2->3->4->2
    # graf 3 z dodaną krawędzią 4->2, która zamknęła cykl
    # DFS wykryje krawędź wsteczną 4->2 (v=2 jest szary gdy przetwarzamy 4)
    # sortowanie topologiczne zwraca None
    # -------------------------------------------------------------------
    print(f"\n{SEP}")
    print("  GRAF 4 - Skierowany z cyklem 2→3→4→2")
    print(SEP)
    g4 = wczytaj_graf(os.path.join(katalog, 'z_cyklem.txt'))
    print(f"  Typ: {g4['typ']} | wierzchołki: {g4['wierzcholki']}")
    dfs(g4, start=1)
    klasyfikuj_krawedzie(g4)
    sortowanie_topologiczne(g4)   # wykryje cykl, zwróci None

    # -------------------------------------------------------------------
    # graf 5: ważony nieskierowany - algorytm Kruskala
    # oczekiwane MST: (2,3,1),(2,4,2),(5,6,2),(1,3,3),(4,6,3) - łączna waga 11
    # krawędź (1,2,4) zostanie odrzucona, bo zamknęłaby cykl {1,2,3}
    # -------------------------------------------------------------------
    print(f"\n{SEP}")
    print("  GRAF 5 - Ważony nieskierowany (MST Kruskal, oczekiwana waga=11)")
    print(SEP)
    g5 = wczytaj_graf(os.path.join(katalog, 'wazony_nieskierowany.txt'))
    print(f"  Typ: {g5['typ']} | wierzchołki: {g5['wierzcholki']}")
    pelne_dfs(g5)
    kruskal(g5)

    print(f"\n{SEP}")
    print("  Zakończono wszystkie testy.")
    print(SEP)


if __name__ == '__main__':
    main()
