# rbtree.py – Implementacja drzewa czerwono-czarnego
#
# Testy dla [7, 3, 18, 10, 22, 8, 11, 26]:
#   Po każdym wstawieniu wywołano verify_properties() – wyniki w komentarzach na dole.


class RBNode:
    """Węzeł drzewa czerwono-czarnego."""

    def __init__(self, key, color="RED"):
        self.key = key       # klucz węzła
        self.color = color   # kolor: "RED" lub "BLACK"
        self.left = None     # lewe dziecko
        self.right = None    # prawe dziecko
        self.parent = None   # rodzic


class RBTree:
    """Drzewo czerwono-czarne z węzłem wartowniczym NIL."""

    def __init__(self):
        self.NIL = RBNode(key=None, color="BLACK")  # węzeł wartowniczy NIL
        self.root = self.NIL                         # puste drzewo

    # ------------------------------------------------------------------
    # Rotacje
    # ------------------------------------------------------------------

    def left_rotate(self, x):
        """Rotacja w lewo wokół węzła x (x.right staje się nowym korzeniem)."""
        y = x.right
        x.right = y.left
        if y.left != self.NIL:
            y.left.parent = x
        y.parent = x.parent
        if x.parent == self.NIL:
            self.root = y
        elif x == x.parent.left:
            x.parent.left = y
        else:
            x.parent.right = y
        y.left = x
        x.parent = y

    def right_rotate(self, x):
        """Rotacja w prawo wokół węzła x (x.left staje się nowym korzeniem)."""
        y = x.left
        x.left = y.right
        if y.right != self.NIL:
            y.right.parent = x
        y.parent = x.parent
        if x.parent == self.NIL:
            self.root = y
        elif x == x.parent.right:
            x.parent.right = y
        else:
            x.parent.left = y
        y.right = x
        x.parent = y

    # ------------------------------------------------------------------
    # Wstawianie
    # ------------------------------------------------------------------

    def insert(self, key):
        """Wstawia węzeł z kluczem key i wywołuje naprawę kolorowania."""
        z = RBNode(key, color="RED")
        z.left = self.NIL
        z.right = self.NIL
        z.parent = self.NIL

        y = self.NIL
        x = self.root
        while x != self.NIL:
            y = x
            if z.key < x.key:
                x = x.left
            else:
                x = x.right

        z.parent = y
        if y == self.NIL:
            self.root = z
        elif z.key < y.key:
            y.left = z
        else:
            y.right = z

        self._fix_insert(z)

    def _fix_insert(self, z):
        """Naprawia własności RB-drzewa po wstawieniu (RB-INSERT-FIXUP wg CLRS)."""
        while z.parent.color == "RED":
            if z.parent == z.parent.parent.left:
                # Ojciec jest lewym dzieckiem dziadka
                y = z.parent.parent.right   # wujek
                if y.color == "RED":
                    # Przypadek 1: wujek czerwony – rekolorowanie
                    z.parent.color = "BLACK"
                    y.color = "BLACK"
                    z.parent.parent.color = "RED"
                    z = z.parent.parent
                else:
                    if z == z.parent.right:
                        # Przypadek 2: z jest prawym dzieckiem – LR → sprowadź do LL
                        z = z.parent
                        self.left_rotate(z)
                    # Przypadek 3: z jest lewym dzieckiem – LL
                    z.parent.color = "BLACK"
                    z.parent.parent.color = "RED"
                    self.right_rotate(z.parent.parent)
            else:
                # Symetryczny przypadek: ojciec jest prawym dzieckiem dziadka
                y = z.parent.parent.left    # wujek
                if y.color == "RED":
                    # Przypadek 1 (sym.): wujek czerwony – rekolorowanie
                    z.parent.color = "BLACK"
                    y.color = "BLACK"
                    z.parent.parent.color = "RED"
                    z = z.parent.parent
                else:
                    if z == z.parent.left:
                        # Przypadek 2 (sym.): z jest lewym dzieckiem – RL → sprowadź do RR
                        z = z.parent
                        self.right_rotate(z)
                    # Przypadek 3 (sym.): z jest prawym dzieckiem – RR
                    z.parent.color = "BLACK"
                    z.parent.parent.color = "RED"
                    self.left_rotate(z.parent.parent)
        self.root.color = "BLACK"

    # ------------------------------------------------------------------
    # Weryfikacja własności
    # ------------------------------------------------------------------

    def verify_properties(self):
        """Sprawdza wszystkie 5 własności RB-drzewa i wypisuje wynik każdej z nich."""
        ok1 = self._check_prop1(self.root)
        ok2 = (self.root == self.NIL) or (self.root.color == "BLACK")
        ok3 = self.NIL.color == "BLACK"
        ok4 = self._check_prop4(self.root)
        bh  = self._black_height(self.root)
        ok5 = (bh != -1)

        print(f"    W1 (każdy węzeł RED lub BLACK)         : {'OK' if ok1 else 'BŁĄD'}")
        print(f"    W2 (korzeń jest czarny)                 : {'OK' if ok2 else 'BŁĄD'}")
        print(f"    W3 (każdy liść NIL jest czarny)         : {'OK' if ok3 else 'BŁĄD'}")
        print(f"    W4 (czerwony węzeł → czarne dzieci)     : {'OK' if ok4 else 'BŁĄD'}")
        print(f"    W5 (jednakowa czarna wysokość)          : {'OK' if ok5 else 'BŁĄD'}"
              + (f"  [bh={bh}]" if ok5 else ""))

        all_ok = ok1 and ok2 and ok3 and ok4 and ok5
        print(f"    → Wszystkie własności: {'SPEŁNIONE' if all_ok else 'NARUSZONE'}")
        return all_ok

    def _check_prop1(self, node):
        """Rekurencyjnie sprawdza, czy każdy węzeł ma kolor RED lub BLACK."""
        if node == self.NIL:
            return True
        if node.color not in ("RED", "BLACK"):
            return False
        return self._check_prop1(node.left) and self._check_prop1(node.right)

    def _check_prop4(self, node):
        """Rekurencyjnie sprawdza, czy czerwony węzeł ma wyłącznie czarne dzieci."""
        if node == self.NIL:
            return True
        if node.color == "RED":
            if node.left.color != "BLACK" or node.right.color != "BLACK":
                return False
        return self._check_prop4(node.left) and self._check_prop4(node.right)

    def _black_height(self, node):
        """Zwraca czarną wysokość poddrzewa lub -1 jeśli własność 5 jest naruszona."""
        if node == self.NIL:
            return 1  # NIL liczy się jako czarny
        lbh = self._black_height(node.left)
        rbh = self._black_height(node.right)
        if lbh == -1 or rbh == -1 or lbh != rbh:
            return -1
        return lbh + (1 if node.color == "BLACK" else 0)

    # ------------------------------------------------------------------
    # Wyszukiwanie
    # ------------------------------------------------------------------

    def search(self, k, x=None):
        """Szuka klucza k w drzewie; zwraca węzeł lub None."""
        if x is None:
            x = self.root
        while x != self.NIL:
            if k == x.key:
                return x
            x = x.left if k < x.key else x.right
        return None

    # ------------------------------------------------------------------
    # Wyświetlanie
    # ------------------------------------------------------------------

    def print_tree(self, node=None, prefix="", connector="Root"):
        """Wyświetla strukturę drzewa z kolorami węzłów (R=czerwony, B=czarny)."""
        if node is None:
            node = self.root
        if node == self.NIL:
            return
        tag = "R" if node.color == "RED" else "B"
        print(f"{prefix}{connector}: {node.key}({tag})")
        if node.left != self.NIL or node.right != self.NIL:
            self.print_tree(node.left,  prefix + "    ", "L")
            self.print_tree(node.right, prefix + "    ", "R")


# ----------------------------------------------------------------------
# Testy
# ----------------------------------------------------------------------

if __name__ == "__main__":
    keys = [7, 3, 18, 10, 22, 8, 11, 26]
    tree = RBTree()

    for k in keys:
        tree.insert(k)
        print(f"\n=== Po wstawieniu {k} ===")
        tree.print_tree()
        tree.verify_properties()

# ----------------------------------------------------------------------
# Wyniki testów (komentarz):
#
#  insert(7)  → korzeń 7(B); bh=2                              – W1–W5 SPEŁNIONE
#  insert(3)  → 7(B), L:3(R); bh=2                            – W1–W5 SPEŁNIONE
#  insert(18) → 7(B), L:3(R), R:18(R); bh=2                  – W1–W5 SPEŁNIONE
#  insert(10) → wujek 3(R) → Case 1: rekolorowanie 3,18→B, 7→R→B(root);
#               wynik: 7(B), L:3(B), R:18(B), L:10(R); bh=3  – W1–W5 SPEŁNIONE
#  insert(22) → 22(R) jako prawe dziecko 18(B); bh=3          – W1–W5 SPEŁNIONE
#  insert(8)  → wujek 22(R) → Case 1: rekolorowanie 10,22→B, 18→R;
#               wynik: 18(R), L:10(B), L:8(R), R:22(B); bh=3 – W1–W5 SPEŁNIONE
#  insert(11) → 11(R) prawe dziecko 10(B); bh=3               – W1–W5 SPEŁNIONE
#  insert(26) → 26(R) prawe dziecko 22(B); bh=3               – W1–W5 SPEŁNIONE
#
#  Końcowa struktura:
#      7(B)
#     /    \
#   3(B)  18(R)
#         /    \
#       10(B)  22(B)
#       /  \      \
#     8(R) 11(R)  26(R)
#
#  Czarna wysokość końcowego drzewa: 3
#  We wszystkich 8 krokach własności 1–5 były SPEŁNIONE.
# ----------------------------------------------------------------------
