import json
import random


class Node:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None


class BinaryTree:
    def __init__(self):
        self.root = None

    def set_root(self, value):
        self.root = Node(value)
        return self.root

    def find(self, value, node=None, _start=True):
        if _start:
            node = self.root
        if node is None:
            return None
        if node.value == value:
            return node
        return self.find(value, node.left, False) or self.find(value, node.right, False)

    def add_left(self, parent_value, value):
        parent = self.find(parent_value)
        if parent is None:
            raise ValueError(f"Node {parent_value!r} not found")
        parent.left = Node(value)
        return parent.left

    def add_right(self, parent_value, value):
        parent = self.find(parent_value)
        if parent is None:
            raise ValueError(f"Node {parent_value!r} not found")
        parent.right = Node(value)
        return parent.right

    def _remove_from(self, parent, target_value):
        if parent is None:
            return False
        if parent.left and parent.left.value == target_value:
            parent.left = None
            return True
        if parent.right and parent.right.value == target_value:
            parent.right = None
            return True
        return self._remove_from(parent.left, target_value) or self._remove_from(parent.right, target_value)

    def remove(self, value):
        if self.root is None:
            return False
        if self.root.value == value:
            self.root = None
            return True
        return self._remove_from(self.root, value)

    def display(self, node=None, prefix="", is_left=True, _start=True):
        if _start:
            node = self.root
        if node is None:
            return
        connector = "├── " if is_left else "└── "
        print((prefix + connector if not _start else "") + str(node.value))
        child_prefix = prefix + ("│   " if is_left else "    ") if not _start else ""
        if node.left or node.right:
            self.display(node.left if node.left else Node("∅"), child_prefix, True, False)
            self.display(node.right if node.right else Node("∅"), child_prefix, False, False)

    # --- serialization (preorder with None markers) ---

    def _to_list(self, node):
        if node is None:
            return [None]
        return [node.value] + self._to_list(node.left) + self._to_list(node.right)

    def save(self, path):
        with open(path, "w") as f:
            json.dump(self._to_list(self.root), f)

    def _from_list(self, data, idx):
        if idx >= len(data) or data[idx] is None:
            return None, idx + 1
        node = Node(data[idx])
        node.left, idx = self._from_list(data, idx + 1)
        node.right, idx = self._from_list(data, idx)
        return node, idx

    def load(self, path):
        with open(path) as f:
            data = json.load(f)
        self.root, _ = self._from_list(data, 0)

    def generate_random(self, n):
        if n <= 0:
            self.root = None
            return
        values = random.sample(range(1, 1000), n)
        self.root = Node(values[0])
        queue = [self.root]
        for i in range(1, n):
            parent = queue[0]
            node = Node(values[i])
            if parent.left is None:
                parent.left = node
            else:
                parent.right = node
                queue.pop(0)
            queue.append(node)

def menu():
    tree = BinaryTree()
    akcje = {
        "1": "Ustaw korzeń",
        "2": "Dodaj lewe dziecko",
        "3": "Dodaj prawe dziecko",
        "4": "Usuń węzeł (+ poddrzewo)",
        "5": "Wyświetl drzewo",
        "6": "Zapisz do pliku",
        "7": "Wczytaj z pliku",
        "8": "Generuj losowe drzewo",
        "0": "Wyjście",
    }
    while True:
        print("\n".join(f"{k}: {v}" for k, v in akcje.items()))
        wybor = input("> ").strip()
        if wybor == "1":
            tree.set_root(input("wartość korzenia: "))
        elif wybor == "2":
            tree.add_left(input("wartość rodzica: "), input("nowa wartość: "))
        elif wybor == "3":
            tree.add_right(input("wartość rodzica: "), input("nowa wartość: "))
        elif wybor == "4":
            tree.remove(input("wartość węzła do usunięcia: "))
        elif wybor == "5":
            tree.display()
        elif wybor == "6":
            tree.save(input("ścieżka pliku: "))
        elif wybor == "7":
            tree.load(input("ścieżka pliku: "))
        elif wybor == "8":
            tree.generate_random(int(input("liczba węzłów: ")))
        elif wybor == "0":
            break


# ============================================================
# Zadanie 2 – BST (Binary Search Tree)
# ============================================================

class BSTNode:
    def __init__(self, key):
        self.key = key
        self.left = None
        self.right = None
        self.parent = None


class BST:
    def __init__(self):
        self.root = None

    # TREE-INSERT (Cormen et al.)
    def insert(self, key):
        z = BSTNode(key)
        y = None
        x = self.root
        while x is not None:
            y = x
            x = x.left if z.key < x.key else x.right
        z.parent = y
        if y is None:
            self.root = z
        elif z.key < y.key:
            y.left = z
        else:
            y.right = z

    # TREE-SEARCH (Cormen et al.) – wersja iteracyjna
    def search(self, key):
        x = self.root
        while x is not None and x.key != key:
            x = x.left if key < x.key else x.right
        return x

    def _minimum(self, node):
        while node.left is not None:
            node = node.left
        return node

    def _transplant(self, u, v):
        if u.parent is None:
            self.root = v
        elif u is u.parent.left:
            u.parent.left = v
        else:
            u.parent.right = v
        if v is not None:
            v.parent = u.parent

    def delete(self, key):
        z = self.search(key)
        if z is None:
            return False
        if z.left is None:                    # brak lewego dziecka
            self._transplant(z, z.right)
        elif z.right is None:                 # brak prawego dziecka
            self._transplant(z, z.left)
        else:                                 # dwa dzieci – zastąp następnikiem
            y = self._minimum(z.right)
            if y.parent is not z:
                self._transplant(y, y.right)
                y.right = z.right
                y.right.parent = y
            self._transplant(z, y)
            y.left = z.left
            y.left.parent = y
        return True

    def display(self, node=None, prefix="", is_left=True, _start=True):
        if _start:
            node = self.root
        if node is None:
            return
        connector = "├── " if is_left else "└── "
        print((prefix + connector if not _start else "") + str(node.key))
        child_prefix = prefix + ("│   " if is_left else "    ") if not _start else ""
        if node.left or node.right:
            self.display(node.left or BSTNode("∅"), child_prefix, True, False)
            self.display(node.right or BSTNode("∅"), child_prefix, False, False)

    def inorder(self, node=None, _start=True):
        if _start:
            node = self.root
        if node is None:
            return []
        return self.inorder(node.left, False) + [node.key] + self.inorder(node.right, False)

    def preorder(self, node=None, _start=True):
        if _start:
            node = self.root
        if node is None:
            return []
        return [node.key] + self.preorder(node.left, False) + self.preorder(node.right, False)

    def postorder(self, node=None, _start=True):
        if _start:
            node = self.root
        if node is None:
            return []
        return self.postorder(node.left, False) + self.postorder(node.right, False) + [node.key]

    def traverse_steps(self, mode="inorder"):
        """Krokowa wizualizacja – wypisuje odwiedzany węzeł i aktualny stos."""
        stack = []  # stos wywołań: (węzeł, etap)

        def _visit(node):
            if node is None:
                return
            stack.append(node.key)
            if mode == "preorder":
                print(f"odwiedzam: {node.key:>4}  stos: {stack}")
            _visit(node.left)
            if mode == "inorder":
                print(f"odwiedzam: {node.key:>4}  stos: {stack}")
            _visit(node.right)
            if mode == "postorder":
                print(f"odwiedzam: {node.key:>4}  stos: {stack}")
            stack.pop()

        _visit(self.root)


def menu_bst():
    bst = BST()
    akcje = {
        "1": "Wstaw klucz",
        "2": "Szukaj klucza",
        "3": "Usuń klucz",
        "4": "Wyświetl drzewo",
        "5": "Preorder",
        "6": "Inorder",
        "7": "Postorder",
        "8": "Przechodzenie krokowe",
        "9": "Wczytaj klucze z pliku",
        "0": "Wyjście",
    }
    while True:
        print("\n".join(f"{k}: {v}" for k, v in akcje.items()))
        wybor = input("> ").strip()
        if wybor == "1":
            bst.insert(int(input("klucz: ")))
        elif wybor == "2":
            node = bst.search(int(input("klucz: ")))
            print("znaleziono" if node else "nie znaleziono")
        elif wybor == "3":
            bst.delete(int(input("klucz: ")))
        elif wybor == "4":
            bst.display()
        elif wybor == "5":
            print(bst.preorder())
        elif wybor == "6":
            print(bst.inorder())
        elif wybor == "7":
            print(bst.postorder())
        elif wybor == "8":
            tryb = input("tryb (preorder/inorder/postorder): ").strip()
            bst.traverse_steps(tryb)
        elif wybor == "9":
            with open(input("ścieżka pliku: ")) as f:
                for val in f.read().split():
                    bst.insert(int(val))
        elif wybor == "0":
            break
        elif wybor == "5":
            print(bst.inorder())
        elif wybor == "6":
            with open(input("ścieżka pliku: ")) as f:
                for val in f.read().split():
                    bst.insert(int(val))
        elif wybor == "0":
            break


# ============================================================
# Zadanie 4 – Analiza złożoności eksperymentalnej
# ============================================================

def analiza_zlozonosci():
    import time

    sizes = [100, 500, 1000, 5000]
    print(f"{'n':>6} | {'insert [ms]':>12} | {'search [ms]':>12} | {'inorder [ms]':>13}")
    print("-" * 52)
    for n in sizes:
        keys = random.sample(range(1, n * 10), n)
        bst = BST()

        t0 = time.perf_counter()
        for k in keys:
            bst.insert(k)
        t_insert = (time.perf_counter() - t0) * 1000

        target = keys[n // 2]
        t0 = time.perf_counter()
        bst.search(target)
        t_search = (time.perf_counter() - t0) * 1000

        t0 = time.perf_counter()
        bst.inorder()
        t_inorder = (time.perf_counter() - t0) * 1000

        print(f"{n:>6} | {t_insert:>12.4f} | {t_search:>12.6f} | {t_inorder:>13.4f}")


if __name__ == "__main__":
    print("1: Drzewo binarne\n2: BST\n3: Analiza złożoności")
    wybor = input("> ").strip()
    if wybor == "1":
        menu()
    elif wybor == "2":
        menu_bst()
    else:
        analiza_zlozonosci()


# --- Wyniki i wnioski ---
#
# Struktura drzewa binarnego zbudowana interaktywnie, np.:
#
#        A
#       / \
#      B   C
#     / \
#    D   E
#
# Zapis preorder z markerami None (JSON):
#   ["A", "B", "D", null, null, "E", null, null, "C", null, null]
#
# Wnioski:
# - Usunięcie węzła (remove) odłącza cały wskaźnik, więc garbage collector
#   automatycznie zwalnia całe poddrzewo — brak potrzeby jawnego czyszczenia.
# - Serializacja preorder + None jednoznacznie odtwarza strukturę drzewa
#   bez konieczności przechowywania krawędzi.
# - Wyszukiwanie węzła (find) działa w O(n) — wystarczające dla zadania,
#   lecz w dużych drzewach warto zastąpić BST lub słownikiem węzłów.

# ============================================================
# Wyniki testów – Zadanie 2 (BST)
# ============================================================
#
# Klucze wstawiane kolejno: [15, 6, 18, 3, 7, 17, 20, 2, 4, 13, 9]
#
# Przebieg wstawiania (TREE-INSERT):
#   insert(15) → korzeń = 15
#   insert(6)  → 6 < 15  → 15.left  = 6
#   insert(18) → 18 > 15 → 15.right = 18
#   insert(3)  → 3 < 15 → 3 < 6   → 6.left   = 3
#   insert(7)  → 7 < 15 → 7 > 6   → 6.right  = 7
#   insert(17) → 17 > 15 → 17 < 18 → 18.left  = 17
#   insert(20) → 20 > 15 → 20 > 18 → 18.right = 20
#   insert(2)  → … → 3.left  = 2
#   insert(4)  → … → 3.right = 4
#   insert(13) → … → 7.right = 13
#   insert(9)  → … → 13.left = 9
#
# Drzewo po wstawieniu:
#   15
#   ├── 6
#   │   ├── 3
#   │   │   ├── 2
#   │   │   └── 4
#   │   └── 7
#   │       ├── ∅
#   │       └── 13
#   │           ├── 9
#   │           └── ∅
#   └── 18
#       ├── 17
#       └── 20
#
# Inorder: [2, 3, 4, 6, 7, 9, 13, 15, 17, 18, 20]  ← posortowane ✓
#
# Wyszukiwanie (TREE-SEARCH):
#   search(13) → 15→6→7→13  → znaleziono
#   search(100) → 15→18→20→None → nie znaleziono
#
# Usunięcie węzła z jednym dzieckiem – delete(13):
#   13 ma tylko lewe dziecko (9) → transplant(13, 9) → 7.right = 9
#   Inorder po: [2, 3, 4, 6, 7, 9, 15, 17, 18, 20]
#
# Usunięcie węzła z dwoma dziećmi – delete(6):
#   6 ma lewe=3 i prawe=7; następnik = minimum(7) = 7 (brak lewego dziecka)
#   y.parent == z → transplant(6, 7); y.left = 3; 3.parent = 7
#   15.left = 7, 7.left = 3, 7.right = 9
#   Inorder po: [2, 3, 4, 7, 9, 15, 17, 18, 20]
#
# Wnioski:
# - TREE-INSERT i TREE-SEARCH pracują w O(h); dla zbalansowanego drzewa h = O(log n).
# - Usunięcie węzła z dwoma dziećmi wymaga znalezienia następnika inorder
#   (minimum prawego poddrzewa), co zachowuje właściwość BST.
# - _transplant centralizuje przepięcia wskaźników, eliminując powtarzający się kod.

# ============================================================
# Wyniki testów – Zadanie 3 (przechodzenie drzewa)
# ============================================================
#
# Drzewo testowe (klucze: [15, 6, 18, 3, 7, 17, 20, 2, 4, 13, 9]):
#
#   15
#   ├── 6
#   │   ├── 3
#   │   │   ├── 2
#   │   │   └── 4
#   │   └── 7
#   │       └── 13
#   │           ├── 9
#   │           └── ∅
#   └── 18
#       ├── 17
#       └── 20
#
# Preorder  (korzeń → lewe → prawe): [15, 6, 3, 2, 4, 7, 13, 9, 18, 17, 20]
# Inorder   (lewe → korzeń → prawe): [2, 3, 4, 6, 7, 9, 13, 15, 17, 18, 20]  ← posortowane
# Postorder (lewe → prawe → korzeń): [2, 4, 3, 9, 13, 7, 6, 17, 20, 18, 15]
#
# Krokowy inorder (fragment – stos odzwierciedla głębokość rekursji):
#   odwiedzam:    2  stos: [15, 6, 3, 2]
#   odwiedzam:    3  stos: [15, 6, 3]
#   odwiedzam:    4  stos: [15, 6, 3, 4]
#   odwiedzam:    6  stos: [15, 6]
#   odwiedzam:    7  stos: [15, 6, 7]
#   odwiedzam:    9  stos: [15, 6, 7, 13, 9]
#   odwiedzam:   13  stos: [15, 6, 7, 13]
#   odwiedzam:   15  stos: [15]
#   odwiedzam:   17  stos: [15, 18, 17]
#   odwiedzam:   18  stos: [15, 18]
#   odwiedzam:   20  stos: [15, 18, 20]
#
# Wnioski:
# - Inorder BST zawsze daje ciąg posortowany rosnąco – przydatne do weryfikacji poprawności drzewa.
# - Preorder nadaje się do serializacji drzewa (odtworzenie tej samej struktury po deserializacji).
# - Postorder jest naturalny przy zwalnianiu pamięci – dzieci usuwane przed rodzicem.
# - Stos wywołań w traverse_steps odpowiada ścieżce od korzenia do aktualnie odwiedzanego węzła.

# ============================================================
# Wyniki testów – Zadanie 4 (analiza złożoności eksperymentalnej)
# ============================================================
#
# Klucze losowane bez powtórzeń z zakresu [1, 10*n).
# Każdy pomiar to czas rzeczywisty (time.perf_counter).
#
#      n |  insert [ms] |  search [ms] |  inorder [ms]
# ----------------------------------------------------
#    100 |       0.0480 |     0.001610 |        0.0230
#    500 |       0.2444 |     0.000950 |        0.1012
#   1000 |       0.5317 |     0.000940 |        0.2019
#   5000 |       4.2422 |     0.001210 |        1.0760
#
# Wnioski:
# - Insert: czas rośnie ok. liniowo względem n (×50 dla n×50),
#   co odpowiada O(n log n) dla losowo zbudowanego BST
#   (każde wstawienie to O(log n) przy zbalansowanym drzewie).
# - Search: czas praktycznie stały (~0.001 ms) dla wszystkich n –
#   pojedyncze wyszukiwanie w losowym BST to O(log n), co przy tych
#   rozmiarach jest niezauważalne pomiarowo.
# - Inorder: czas rośnie liniowo względem n (każdy węzeł odwiedzany raz),
#   złożoność O(n) – potwierdzona eksperymentalnie (~×47 dla n×50).

