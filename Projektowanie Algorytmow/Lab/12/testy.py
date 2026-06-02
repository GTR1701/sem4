# testy.py – Porównanie eksperymentalne BST, AVL i drzewa czerwono-czarnego
#
# Eksperyment mierzy dla n ∈ {100, 500, 1000, 5000}:
#   • czas wstawiania wszystkich n elementów
#   • wysokość uzyskanego drzewa
#   • czas pojedynczego wyszukiwania (mediana z 500 powtórzeń)
#
# Wyniki i wnioski umieszczone w komentarzu na końcu pliku.

import random
import sys
import time

from avltree import AVLNode, avl_insert, get_height as avl_get_height
from rbtree import RBTree

sys.setrecursionlimit(50_000)  # zabezpieczenie dla BST przy losowych danych


# ---------------------------------------------------------------------------
# Proste drzewo BST
# ---------------------------------------------------------------------------

class BSTNode:
    """Węzeł zwykłego drzewa BST (bez równoważenia)."""

    def __init__(self, key):
        self.key = key
        self.left = None
        self.right = None


def bst_insert(root, key):
    """Wstawia klucz do BST i zwraca (nowy) korzeń."""
    if root is None:
        return BSTNode(key)
    if key < root.key:
        root.left = bst_insert(root.left, key)
    elif key > root.key:
        root.right = bst_insert(root.right, key)
    return root


def bst_search(root, key):
    """Szuka klucza w BST (działa też dla węzłów AVLNode)."""
    if root is None or root.key == key:
        return root
    if key < root.key:
        return bst_search(root.left, key)
    return bst_search(root.right, key)


def bst_height(root):
    """Zwraca wysokość BST (liść = 1, puste = 0)."""
    if root is None:
        return 0
    return 1 + max(bst_height(root.left), bst_height(root.right))


# ---------------------------------------------------------------------------
# Pomocnicza funkcja wysokości dla RB-drzewa
# ---------------------------------------------------------------------------

def rb_height(tree):
    """Zwraca wysokość drzewa czerwono-czarnego (węzły NIL nie liczą się)."""
    def _h(node):
        if node is tree.NIL:
            return 0
        return 1 + max(_h(node.left), _h(node.right))
    return _h(tree.root)


# ---------------------------------------------------------------------------
# Eksperyment
# ---------------------------------------------------------------------------

REPEATS_SEARCH = 500   # liczba powtórzeń pomiaru czasu wyszukiwania
SIZES = [100, 500, 1000, 5000]


def measure(n, keys):
    """Mierzy czasy i wysokości dla wszystkich trzech struktur dla zestawu kluczy."""
    search_key = keys[n // 2]   # szukany element (zawsze istnieje w drzewie)
    stats = {}

    # --- BST ---
    t0 = time.perf_counter()
    bst_root = None
    for k in keys:
        bst_root = bst_insert(bst_root, k)
    t_ins = time.perf_counter() - t0

    h = bst_height(bst_root)

    t0 = time.perf_counter()
    for _ in range(REPEATS_SEARCH):
        bst_search(bst_root, search_key)
    t_srch = (time.perf_counter() - t0) / REPEATS_SEARCH

    stats["BST"] = (t_ins * 1000, h, t_srch * 1e6)   # ms, -, µs

    # --- AVL ---
    t0 = time.perf_counter()
    avl_root = None
    for k in keys:
        avl_root = avl_insert(avl_root, k)
    t_ins = time.perf_counter() - t0

    h = avl_get_height(avl_root)   # O(1) – wysokość przechowywana w węźle

    t0 = time.perf_counter()
    for _ in range(REPEATS_SEARCH):
        bst_search(avl_root, search_key)   # AVL to BST – szukanie identyczne
    t_srch = (time.perf_counter() - t0) / REPEATS_SEARCH

    stats["AVL"] = (t_ins * 1000, h, t_srch * 1e6)

    # --- RB-tree ---
    t0 = time.perf_counter()
    rb = RBTree()
    for k in keys:
        rb.insert(k)
    t_ins = time.perf_counter() - t0

    h = rb_height(rb)

    t0 = time.perf_counter()
    for _ in range(REPEATS_SEARCH):
        rb.search(search_key)
    t_srch = (time.perf_counter() - t0) / REPEATS_SEARCH

    stats["RB"] = (t_ins * 1000, h, t_srch * 1e6)

    return stats


def print_table(all_results):
    """Wypisuje wyniki w sformatowanej tabeli."""
    hdr = f"{'n':>6}  {'Struktura':<10}  {'Wstawianie [ms]':>17}  {'Wysokość':>9}  {'Wyszukiwanie [µs]':>18}"
    sep = "-" * len(hdr)
    print(sep)
    print(hdr)
    print(sep)
    for n, stats in sorted(all_results.items()):
        for name in ("BST", "AVL", "RB"):
            t_ins, h, t_srch = stats[name]
            print(f"{n:>6}  {name:<10}  {t_ins:>17.4f}  {h:>9}  {t_srch:>18.4f}")
        print(sep)


if __name__ == "__main__":
    random.seed(42)
    all_results = {}
    for n in SIZES:
        keys = random.sample(range(1, n * 20), n)
        all_results[n] = measure(n, keys)

    print_table(all_results)


# ---------------------------------------------------------------------------
# Wyniki eksperymentu (seed=42):
#
# --------------------------------------------------------------------
#      n  Struktura     Wstawianie [ms]   Wysokość   Wyszukiwanie [µs]
# --------------------------------------------------------------------
#    100  BST                    0.0467         14              0.3363
#    100  AVL                    0.1961          8              0.1189
#    100  RB                     0.1004          8              0.2926
# --------------------------------------------------------------------
#    500  BST                    0.2882         20              0.4750
#    500  AVL                    1.2683         11              0.3305
#    500  RB                     0.4915         11              0.3497
# --------------------------------------------------------------------
#   1000  BST                    0.6766         25              0.4168
#   1000  AVL                    2.8583         12              0.4307
#   1000  RB                     1.0414         12              0.3923
# --------------------------------------------------------------------
#   5000  BST                    4.9462         29              0.4975
#   5000  AVL                   18.2121         15              0.5483
#   5000  RB                     5.9737         15              0.6201
# --------------------------------------------------------------------
#
# Wnioski:
#
# 1. Wysokość:
#    BST na losowych danych ma wysokość ~2·log₂(n) (29 dla n=5000),
#    czyli ok. 2× więcej niż AVL/RB (oba po 15). Przy posortowanych
#    danych BST degenerowałoby do n, podczas gdy AVL/RB gwarantują
#    O(log n) nawet w najgorszym przypadku.
#
# 2. Czas wstawiania:
#    BST jest najszybsze – brak narzutu na rotacje ani rekolorowanie.
#    RB-tree jest drugi pod względem szybkości: iteracyjna pętla fixup
#    jest efektywna w Pythonie. AVL jest najwolniejsze, bo rekurencyjne
#    wywołania avl_insert generują duży narzut wywołań funkcji w Pythonie
#    (dla n=5000: AVL ≈ 3× wolniejsze od RB i ≈ 4× wolniejsze od BST).
#
# 3. Czas wyszukiwania:
#    Różnice są niewielkie dla losowych danych (wszystkie struktury mają
#    porównywalną wysokość). Dla n=100 AVL jest najszybsze dzięki
#    najmniejszej wysokości (8). Dla większych n zysk z mniejszej
#    wysokości jest marginalizowany przez inne czynniki (lokalność
#    pamięci, narzut wskaźników parent w RB).
#
# 4. Skalowanie:
#    Czas wstawiania rośnie zgodnie z O(n·log n), czas wyszukiwania
#    z O(log n), co potwierdzają dane – np. wstawianie BST: 0.047 ms
#    (n=100) → 4.95 ms (n=5000), wzrost ≈ 106× przy wzroście n o 50×.
#
# 5. Praktyczne rekomendacje:
#    • Dane losowe, brak gwarancji worst-case wymaganych → BST.
#    • Intensywne wyszukiwanie, minimalna wysokość kluczowa → AVL.
#    • Mieszane operacje (wstawianie + usuwanie + wyszukiwanie) → RB.
# ---------------------------------------------------------------------------
