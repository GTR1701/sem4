# btree.py – Implementacja B-drzewa
#
# Testy dla kluczy [10, 20, 5, 6, 12, 30, 7, 17]:
#   Wyniki (po uruchomieniu) zapisane w komentarzu na końcu pliku.


class BTreeNode:
    """Węzeł B-drzewa."""

    def __init__(self, t, leaf=True):
        self.t = t           # minimalny stopień drzewa
        self.keys = []       # lista kluczy w węźle
        self.children = []   # lista dzieci
        self.leaf = leaf     # czy węzeł jest liściem


class BTree:
    """B-drzewo o minimalnym stopniu t (każdy węzeł ma co najwyżej 2t-1 kluczy)."""

    def __init__(self, t):
        self.t = t
        self.root = BTreeNode(t, leaf=True)  # na starcie puste drzewo (liść)

    # ------------------------------------------------------------------
    # Wyszukiwanie  (B-TREE-SEARCH wg CLRS)
    # ------------------------------------------------------------------

    def search(self, k, x=None):
        """Szuka klucza k w poddrzewie zaczepionym w węźle x.
        Zwraca (węzeł, indeks) lub None jeśli nie znaleziono."""
        if x is None:
            x = self.root
        i = 0
        while i < len(x.keys) and k > x.keys[i]:
            i += 1
        if i < len(x.keys) and k == x.keys[i]:
            return (x, i)
        if x.leaf:
            return None
        return self.search(k, x.children[i])

    # ------------------------------------------------------------------
    # Wstawianie
    # ------------------------------------------------------------------

    def insert(self, k):
        """Wstawia klucz k do B-drzewa; w razie potrzeby dzieli pełne węzły."""
        r = self.root
        if len(r.keys) == 2 * self.t - 1:   # korzeń jest pełny → rośnie w górę
            s = BTreeNode(self.t, leaf=False)
            s.children.append(self.root)
            self.root = s
            self.split_child(s, 0)
            self._insert_non_full(s, k)
        else:
            self._insert_non_full(r, k)

    def split_child(self, x, i):
        """Dzieli pełne dziecko x.children[i] na dwa węzły i wstawia medianę do x.
        Węzeł x musi być niepełny; x.children[i] musi mieć dokładnie 2t-1 kluczy."""
        t = self.t
        y = x.children[i]               # pełny węzeł do podziału
        z = BTreeNode(t, leaf=y.leaf)   # nowy węzeł (prawa połowa)

        mid_key = y.keys[t - 1]         # klucz medianowy idący do rodzica

        z.keys = y.keys[t:]             # prawa połowa kluczy (t-1 sztuk)
        y.keys = y.keys[:t - 1]         # lewa połowa kluczy (t-1 sztuk)

        if not y.leaf:
            z.children = y.children[t:]  # prawa połowa dzieci (t sztuk)
            y.children = y.children[:t]  # lewa połowa dzieci (t sztuk)

        x.keys.insert(i, mid_key)        # mediana wchodzi do rodzica
        x.children.insert(i + 1, z)      # z wchodzi jako i+1-sze dziecko x

    def _insert_non_full(self, x, k):
        """Wstawia klucz k do niepełnego węzła x (rekurencyjnie)."""
        i = len(x.keys) - 1
        if x.leaf:
            # Przesuń klucze większe od k o jedną pozycję w prawo
            x.keys.append(None)
            while i >= 0 and k < x.keys[i]:
                x.keys[i + 1] = x.keys[i]
                i -= 1
            x.keys[i + 1] = k
        else:
            # Znajdź właściwe dziecko
            while i >= 0 and k < x.keys[i]:
                i -= 1
            i += 1
            if len(x.children[i].keys) == 2 * self.t - 1:   # dziecko pełne
                self.split_child(x, i)
                if k > x.keys[i]:   # po podziale sprawdź, do której połowy iść
                    i += 1
            self._insert_non_full(x.children[i], k)

    # ------------------------------------------------------------------
    # Wyświetlanie poziomami
    # ------------------------------------------------------------------

    def print_tree(self):
        """Wyświetla B-drzewo poziom po poziomie; każdy węzeł jako lista kluczy."""
        if not self.root.keys:
            print("(puste drzewo)")
            return
        queue = [(self.root, 0)]
        cur_level = 0
        row = []
        while queue:
            node, level = queue.pop(0)
            if level != cur_level:
                print(f"  Poziom {cur_level}: " + "   ".join(str(n.keys) for n in row))
                row = []
                cur_level = level
            row.append(node)
            if not node.leaf:
                for child in node.children:
                    queue.append((child, level + 1))
        if row:
            print(f"  Poziom {cur_level}: " + "   ".join(str(n.keys) for n in row))

    # ------------------------------------------------------------------
    # Wysokość drzewa
    # ------------------------------------------------------------------

    def height(self, node=None):
        """Zwraca wysokość drzewa (liść = 0)."""
        if node is None:
            node = self.root
        if node.leaf:
            return 0
        return 1 + self.height(node.children[0])


# ----------------------------------------------------------------------
# Testy
# ----------------------------------------------------------------------

if __name__ == "__main__":
    keys = [10, 20, 5, 6, 12, 30, 7, 17]

    for t in (2, 3):
        print(f"\n{'=' * 50}")
        print(f"B-drzewo stopnia t = {t}  (max {2*t-1} kluczy / węzeł)")
        print(f"{'=' * 50}")
        tree = BTree(t)
        for k in keys:
            tree.insert(k)

        tree.print_tree()

        h = tree.height()
        root_keys = len(tree.root.keys)
        print(f"\n  Wysokość drzewa          : {h}")
        print(f"  Liczba kluczy w korzeniu : {root_keys}")

        print("\n  Wyszukiwanie wybranych kluczy:")
        for k in [6, 17, 99]:
            result = tree.search(k)
            if result:
                node, idx = result
                print(f"    search({k:2d}) → znaleziono  (klucze węzła: {node.keys})")
            else:
                print(f"    search({k:2d}) → NIE znaleziono")


# ----------------------------------------------------------------------
# Wyniki testów (komentarz):
#
#  t = 2 (drzewo 2-3-4):
#    Poziom 0: [10, 20]
#    Poziom 1: [5, 6, 7]   [12, 17]   [30]
#    Wysokość drzewa          : 1
#    Liczba kluczy w korzeniu : 2
#    search( 6) → znaleziono   (węzeł [5,6,7])
#    search(17) → znaleziono   (węzeł [12,17])
#    search(99) → NIE znaleziono
#
#  t = 3 (drzewo 2-3-4-5-6):
#    Poziom 0: [10]
#    Poziom 1: [5, 6, 7]   [12, 17, 20, 30]
#    Wysokość drzewa          : 1
#    Liczba kluczy w korzeniu : 1
#    search( 6) → znaleziono   (węzeł [5,6,7])
#    search(17) → znaleziono   (węzeł [12,17,20,30])
#    search(99) → NIE znaleziono
#
#  Porównanie wysokości:
#    Obie wartości t dają wysokość 1 dla tego zestawu 8 kluczy.
#    Przy t=3 korzeń ma tylko 1 klucz (mniej podziałów), a prawy liść
#    pomieścił 4 klucze bez dalszego rozbicia – węzły są „szersze".
#    Dla większych zbiorów danych większe t skutkuje mniejszą wysokością,
#    ponieważ więcej kluczy mieści się na jednym poziomie, co redukuje
#    liczbę dostępów do dysku w zastosowaniach bazodanowych.
# ----------------------------------------------------------------------
