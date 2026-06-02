# btree.py – Implementacja drzewa AVL
#
# Wyniki testów dla kluczy [10, 20, 30, 40, 50, 25]:
#   Wysokość drzewa  : 3
#   Liczba rotacji   : 4  (2x RR pojedyncza + 1x RL podwójna = 4 operacje rotate)
#
# Kolejność rotacji podczas wstawiania:
#   insert(30) → RR (brak równowagi w 10)       → rotate_left(10)
#   insert(50) → RR (brak równowagi w 30)       → rotate_left(30)
#   insert(25) → RL (brak równowagi w 20)       → rotate_right(40) + rotate_left(20)
#
# Końcowa struktura drzewa:
#         30
#        /  \
#      20    40
#     /  \     \
#   10   25    50

rotation_count = 0  # globalny licznik pojedynczych rotacji


class AVLNode:
    """Węzeł drzewa AVL."""

    def __init__(self, key):
        self.key = key     # klucz węzła
        self.left = None   # lewe dziecko
        self.right = None  # prawe dziecko
        self.height = 1    # wysokość węzła (liść ma wysokość 1)


# ---------------------------------------------------------------------------
# Funkcje pomocnicze
# ---------------------------------------------------------------------------

def get_height(node):
    """Zwraca wysokość węzła; węzeł None ma wysokość 0."""
    return 0 if node is None else node.height


def get_bf(node):
    """Zwraca współczynnik zrównoważenia (balance factor) węzła: h(left) - h(right)."""
    return 0 if node is None else get_height(node.left) - get_height(node.right)


def update_height(node):
    """Aktualizuje pole height węzła na podstawie wysokości jego dzieci."""
    if node is not None:
        node.height = 1 + max(get_height(node.left), get_height(node.right))


# ---------------------------------------------------------------------------
# Rotacje
# ---------------------------------------------------------------------------

def rotate_right(z):
    """Rotacja w prawo wokół węzła z (przypadek LL). Zwraca nowy korzeń poddrzewa."""
    global rotation_count
    rotation_count += 1
    y = z.left
    t3 = y.right   # środkowe poddrzewo
    y.right = z
    z.left = t3
    update_height(z)
    update_height(y)
    return y


def rotate_left(z):
    """Rotacja w lewo wokół węzła z (przypadek RR). Zwraca nowy korzeń poddrzewa."""
    global rotation_count
    rotation_count += 1
    y = z.right
    t2 = y.left    # środkowe poddrzewo
    y.left = z
    z.right = t2
    update_height(z)
    update_height(y)
    return y


# ---------------------------------------------------------------------------
# Wstawianie z przywracaniem równowagi AVL
# ---------------------------------------------------------------------------

def avl_insert(node, key):
    """Wstawia klucz do drzewa AVL i przywraca równowagę przez rotacje LL/RR/LR/RL."""
    # Standardowe wstawianie BST
    if node is None:
        return AVLNode(key)
    if key < node.key:
        node.left = avl_insert(node.left, key)
    elif key > node.key:
        node.right = avl_insert(node.right, key)
    else:
        return node  # duplikat – ignorujemy

    update_height(node)
    bf = get_bf(node)

    # LL – lewe dziecko, lewa gałąź
    if bf > 1 and key < node.left.key:
        return rotate_right(node)

    # RR – prawe dziecko, prawa gałąź
    if bf < -1 and key > node.right.key:
        return rotate_left(node)

    # LR – lewe dziecko, prawa gałąź
    if bf > 1 and key > node.left.key:
        node.left = rotate_left(node.left)
        return rotate_right(node)

    # RL – prawe dziecko, lewa gałąź
    if bf < -1 and key < node.right.key:
        node.right = rotate_right(node.right)
        return rotate_left(node)

    return node


# ---------------------------------------------------------------------------
# Wyświetlanie drzewa
# ---------------------------------------------------------------------------

def print_tree(node, prefix="", connector="Root"):
    """Wyświetla strukturę drzewa AVL w postaci tekstowej z informacją o BF."""
    if node is None:
        return
    print(f"{prefix}{connector}: {node.key}  (h={node.height}, bf={get_bf(node)})")
    child_prefix = prefix + "    "
    if node.left or node.right:
        print_tree(node.left,  child_prefix, "L")
        print_tree(node.right, child_prefix, "R")


# ---------------------------------------------------------------------------
# Weryfikacja własności AVL
# ---------------------------------------------------------------------------

def verify_avl(node):
    """Sprawdza, czy BF każdego węzła należy do {-1, 0, 1}. Zwraca True/False."""
    if node is None:
        return True
    bf = get_bf(node)
    if bf not in (-1, 0, 1):
        print(f"  [BŁĄD] węzeł {node.key}: BF = {bf}")
        return False
    return verify_avl(node.left) and verify_avl(node.right)


# ---------------------------------------------------------------------------
# Test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    rotation_count = 0          # resetujemy licznik przed testem
    keys = [10, 20, 30, 40, 50, 25]

    root = None
    for k in keys:
        root = avl_insert(root, k)

    print("=== Struktura drzewa AVL ===")
    print_tree(root)
    print()
    print(f"Wysokość drzewa       : {get_height(root)}")
    print(f"Liczba rotacji        : {rotation_count}")
    print(f"Weryfikacja AVL       : {'OK' if verify_avl(root) else 'BŁĄD'}")
