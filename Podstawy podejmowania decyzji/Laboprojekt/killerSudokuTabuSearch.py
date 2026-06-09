"""
Solver Killer Sudoku – metaheurystyka Tabu Search.

Format pliku wejściowego:
    BlockHeight = 3;
    BlockWidth  = 3;
    numCages    = 23;
    cageID      = [ [...], ... ];
    cageTarget  = [ ... ];

Użycie:
    python killerSudokuTabuSearch.py              # wbudowany przykładowy puzzle
    python killerSudokuTabuSearch.py puzzle.txt   # wczytanie puzzla z pliku
"""

import random
import sys
import re
import time
from collections import defaultdict, Counter

# Built-in example puzzle
EXAMPLE_PUZZLE = """\
BlockHeight = 3;
BlockWidth = 3;

numCages = 23;

cageID = [
  [  1,   1,   2,   2,   2,   3,   3,   4,   4],
  [  1,   1,   1,   5,   2,   3,   4,   4,   6],
  [  7,   8,   8,   5,   2,   3,   9,   4,   6],
  [  7,   7,   8,   5,  10,   3,   6,   6,   6],
  [  7,  11,   8,  10,  10,  12,  12,  12,  13],
  [  7,  11,  14,  10,  10,  15,  15,  13,  13],
  [ 16,  14,  14,  17,  17,  15,  18,  19,  13],
  [ 16,  20,  14,  21,  21,  15,  18,  18,  13],
  [ 20,  20,  22,  22,  22,  22,  23,  23,  23],
];

cageTarget = [26, 22, 25, 30, 15, 20, 29, 11, 6, 31, 9, 18, 21, 26, 20, 10, 10, 18, 5, 13, 3, 25, 12];
"""

# Puzzle parsing

def parse_puzzle(text: str):
    """Zwraca krotkę (block_height, block_width, cage_id_matrix, cage_targets)."""
    block_height = int(re.search(r'BlockHeight\s*=\s*(\d+)', text).group(1))
    block_width  = int(re.search(r'BlockWidth\s*=\s*(\d+)',  text).group(1))

    cage_id_raw = re.search(r'cageID\s*=\s*\[(.*?)\]\s*;', text, re.DOTALL).group(1)
    cage_id_matrix = [
        [int(x) for x in re.findall(r'\d+', row)]
        for row in re.findall(r'\[([^\]]+)\]', cage_id_raw)
    ]

    cage_target_raw = re.search(r'cageTarget\s*=\s*\[([^\]]+)\]', text).group(1)
    cage_targets = [int(x) for x in re.findall(r'\d+', cage_target_raw)]

    return block_height, block_width, cage_id_matrix, cage_targets


# Data structures

def build_structures(cage_id_matrix: list, cage_targets: list):
    """
    Zwraca:
      cage_map     : cid -> (lista_komórek, cel)
      cell_to_cage : (r, c) -> cid
    Identyfikatory klatek w danych wejściowych są indeksowane od 1.
    """
    N = len(cage_id_matrix)
    cage_cells: dict = defaultdict(list)
    cell_to_cage: dict = {}

    for r in range(N):
        for c in range(N):
            cid = cage_id_matrix[r][c]
            cage_cells[cid].append((r, c))
            cell_to_cage[(r, c)] = cid

    cage_map = {
        cid: (cells, cage_targets[cid - 1])
        for cid, cells in cage_cells.items()
    }
    return cage_map, cell_to_cage


# Board initialisation

def make_board(N: int, block_height: int, block_width: int) -> list:
    """
    Wypełnia każdy blok losową permutacją wartości 1..N.
    Gwarantuje to spełnienie ograniczeń blokowych od samego początku;
    przeszukiwanie musi jedynie eliminować naruszenia wierszy, kolumn i klatek.
    """
    board = [[0] * N for _ in range(N)]
    for br in range(0, N, block_height):
        for bc in range(0, N, block_width):
            nums = list(range(1, N + 1))
            random.shuffle(nums)
            k = 0
            for i in range(block_height):
                for j in range(block_width):
                    board[br + i][bc + j] = nums[k]
                    k += 1
    return board


def make_counts(board: list, N: int):
    """
    Zwraca tablice row_cnt i col_cnt jako macierze 2D (N x (N+1)),
    gdzie row_cnt[r][v] = liczba wystąpień wartości v w wierszu r.
    Użycie zwykłych list zapewnia szybszy dostęp niż Counter.
    """
    row_cnt = [[0] * (N + 1) for _ in range(N)]
    col_cnt = [[0] * (N + 1) for _ in range(N)]
    for r in range(N):
        for c in range(N):
            v = board[r][c]
            row_cnt[r][v] += 1
            col_cnt[c][v] += 1
    return row_cnt, col_cnt


# Cost function

def dup_cost(cnt_array, N: int) -> int:
    """Suma max(0, count-1) po wszystkich wartościach 1..N w tablicy zliczeń."""
    return sum(max(0, cnt_array[v] - 1) for v in range(1, N + 1))


def cage_cost(board: list, cells: list, target: int) -> int:
    """Odchyłka sumy od celu + duplikaty wewnątrz klatki."""
    vals = [board[r][c] for r, c in cells]
    s = sum(vals)
    dup = sum(v - 1 for v in Counter(vals).values() if v > 1)
    return abs(s - target) + dup


def full_cost(board: list, N: int, cage_map: dict,
              row_cnt: list, col_cnt: list) -> int:
    """Łączny koszt planszy. Wartość 0 oznacza poprawne rozwiązanie."""
    cost = 0
    for r in range(N):
        cost += dup_cost(row_cnt[r], N)
    for c in range(N):
        cost += dup_cost(col_cnt[c], N)
    for cid, (cells, target) in cage_map.items():
        cost += cage_cost(board, cells, target)
    return cost


# Incremental (delta) cost

def dup_delta(old_cnt: int, change: int) -> int:
    """
    Zmiana wartości max(0, count - 1) gdy count przechodzi z old_cnt na old_cnt+change.
    Używane do szybkiego inkrementalnego obliczania naruszeń w wierszach i kolumnach.
    """
    return max(0, old_cnt + change - 1) - max(0, old_cnt - 1)


def swap_delta(board: list, N: int, cage_map: dict, cell_to_cage: dict,
               row_cnt: list, col_cnt: list,
               r1: int, c1: int, r2: int, c2: int) -> int:
    """
    Oblicza zmianę łącznego kosztu po zamianie komórek (r1,c1) i (r2,c2).

    Optymalizacja wierszy/kolumn:
      - Zamiana w obrębie tego samego wiersza nie zmienia multizbioru tego wiersza.
      - Zamiana w obrębie tej samej kolumny nie zmienia multizbioru tej kolumny.
    """
    v1, v2 = board[r1][c1], board[r2][c2]
    if v1 == v2:
        return 0

    delta = 0

    # Rows
    if r1 != r2:
        # Row r1: loses v1, gains v2
        delta += dup_delta(row_cnt[r1][v1], -1) + dup_delta(row_cnt[r1][v2], +1)
        # Row r2: loses v2, gains v1
        delta += dup_delta(row_cnt[r2][v2], -1) + dup_delta(row_cnt[r2][v1], +1)
    # Same row → multiset unchanged, no row-cost delta.

    # Columns
    if c1 != c2:
        # Col c1: loses v1, gains v2
        delta += dup_delta(col_cnt[c1][v1], -1) + dup_delta(col_cnt[c1][v2], +1)
        # Col c2: loses v2, gains v1
        delta += dup_delta(col_cnt[c2][v2], -1) + dup_delta(col_cnt[c2][v1], +1)
    # Same column → multiset unchanged, no column-cost delta.

    # Cages
    def one_cage_delta(cid: int) -> int:
        cells, target = cage_map[cid]
        vals = [board[r][c] for r, c in cells]
        s_old = sum(vals)
        dup_old = sum(v - 1 for v in Counter(vals).values() if v > 1)

        new_vals = vals[:]
        for i, (r, c) in enumerate(cells):
            if r == r1 and c == c1:
                new_vals[i] = v2
            elif r == r2 and c == c2:
                new_vals[i] = v1

        s_new = sum(new_vals)
        dup_new = sum(v - 1 for v in Counter(new_vals).values() if v > 1)
        return (abs(s_new - target) + dup_new) - (abs(s_old - target) + dup_old)

    cid1 = cell_to_cage[(r1, c1)]
    cid2 = cell_to_cage[(r2, c2)]
    delta += one_cage_delta(cid1)
    if cid2 != cid1:
        delta += one_cage_delta(cid2)

    return delta


def apply_swap(board: list, row_cnt: list, col_cnt: list,
               r1: int, c1: int, r2: int, c2: int) -> None:
    """Wykonuje zamianę w miejscu i aktualizuje tablice zliczeń."""
    v1, v2 = board[r1][c1], board[r2][c2]
    board[r1][c1], board[r2][c2] = v2, v1
    if v1 != v2:
        if r1 != r2:
            row_cnt[r1][v1] -= 1;  row_cnt[r1][v2] += 1
            row_cnt[r2][v2] -= 1;  row_cnt[r2][v1] += 1
        if c1 != c2:
            col_cnt[c1][v1] -= 1;  col_cnt[c1][v2] += 1
            col_cnt[c2][v2] -= 1;  col_cnt[c2][v1] += 1


# Tabu Search

def tabu_search(N: int, block_height: int, block_width: int,
                cage_map: dict, cell_to_cage: dict,
                max_iter: int = 10000,
                tabu_tenure: int = 15,
                max_restarts: int = 100,
                stagnation_limit: int = 600,
                time_limit: float = 120):
    """
    Tabu Search dla Killer Sudoku.

    Strategia
    ---------
    * Sąsiedztwo    : wszystkie zamiany par komórek wewnątrz każdego bloku
                      block_height×block_width. Ograniczenia blokowe są zawsze
                      spełnione z racji inicjalizacji.
    * Lista tabu    : słownik odwzorowujący ruch (r1,c1,r2,c2) na pierwszą
                      iterację, w której ruch przestaje być tabu.
                      Zarówno ruch, jak i jego odwrotność są zakazane przez
                      `tabu_tenure` iteracji.
    * Aspiracja     : ruch tabu jest akceptowany, gdy daje koszt ściśle niższy
                      od aktualnego globalnego optimum.
    * Restart       : po `stagnation_limit` iteracjach bez poprawy generowana
                      jest nowa losowa plansza.

    Zwraca (najlepsza_plansza, najlepszy_koszt).
    """
    # Precompute per-block cell lists once.
    blocks = [
        [(br + i, bc + j)
         for i in range(block_height)
         for j in range(block_width)]
        for br in range(0, N, block_height)
        for bc in range(0, N, block_width)
    ]

    best_overall: list | None = None
    best_overall_cost: int = 10**9
    t0 = time.time()

    for restart in range(max_restarts):
        if time.time() - t0 > time_limit:
            break

        board = make_board(N, block_height, block_width)
        row_cnt, col_cnt = make_counts(board, N)
        current_cost = full_cost(board, N, cage_map, row_cnt, col_cnt)

        best_local = [row[:] for row in board]
        best_local_cost = current_cost

        tabu: dict = {}   # move -> expiry iteration
        no_improve = 0

        for it in range(max_iter):
            if best_overall_cost == 0:
                break
            if time.time() - t0 > time_limit:
                break

            best_move = None
            best_d = 10**9

            for blk in blocks:
                n_cells = len(blk)
                for i in range(n_cells):
                    r1, c1 = blk[i]
                    for j in range(i + 1, n_cells):
                        r2, c2 = blk[j]
                        d = swap_delta(board, N, cage_map, cell_to_cage,
                                       row_cnt, col_cnt, r1, c1, r2, c2)
                        move = (r1, c1, r2, c2)
                        is_tabu = tabu.get(move, 0) > it

                        # Accept if not tabu, or aspiration criterion.
                        if not is_tabu or (current_cost + d < best_overall_cost):
                            if d < best_d:
                                best_d = d
                                best_move = move

            if best_move is None:
                break  # Neighbourhood exhausted (shouldn't happen normally).

            r1, c1, r2, c2 = best_move
            apply_swap(board, row_cnt, col_cnt, r1, c1, r2, c2)
            current_cost += best_d

            # Update tabu list (both directions).
            tabu[best_move] = it + tabu_tenure
            tabu[(r2, c2, r1, c1)] = it + tabu_tenure

            # Track local best.
            if current_cost < best_local_cost:
                best_local_cost = current_cost
                best_local = [row[:] for row in board]
                no_improve = 0
            else:
                no_improve += 1

            # Update global best.
            if best_local_cost < best_overall_cost:
                best_overall_cost = best_local_cost
                best_overall = [row[:] for row in best_local]

            if best_overall_cost == 0:
                break
            if no_improve >= stagnation_limit:
                break

        elapsed = time.time() - t0
        print(
            f"  restart {restart + 1:3d} | local best {best_local_cost:4d} "
            f"| global best {best_overall_cost:4d} | {elapsed:6.1f}s",
            file=sys.stderr, flush=True,
        )

        if best_overall_cost == 0:
            break

    return best_overall, best_overall_cost


# Output helpers

def print_board(board: list, N: int, block_height: int, block_width: int) -> None:
    """Wypisuje planszę z separatorami bloków."""
    cell_w = len(str(N)) + 1          # width of one cell including leading space
    seg_w  = block_width * cell_w + 1 # width of one block segment incl. trailing space
    h_sep  = '+' + '+'.join(['-' * seg_w] * (N // block_width)) + '+'
    for r in range(N):
        if r % block_height == 0:
            print(h_sep)
        row_str = '|'
        for c in range(N):
            row_str += f' {board[r][c]:>{len(str(N))}}'
            if (c + 1) % block_width == 0:
                row_str += ' |'
        print(row_str)
    print(h_sep)


def verify(board: list, N: int, block_height: int, block_width: int,
           cage_map: dict) -> bool:
    """Sprawdza wszystkie ograniczenia Killer Sudoku i wypisuje naruszenia."""
    digits = set(range(1, N + 1))
    ok = True

    for r in range(N):
        if set(board[r]) != digits:
            print(f"  Row {r} FAIL: {board[r]}")
            ok = False

    for c in range(N):
        col = {board[r][c] for r in range(N)}
        if col != digits:
            print(f"  Column {c} FAIL")
            ok = False

    for br in range(0, N, block_height):
        for bc in range(0, N, block_width):
            blk = {board[br + i][bc + j]
                   for i in range(block_height)
                   for j in range(block_width)}
            if blk != digits:
                print(f"  Block ({br},{bc}) FAIL")
                ok = False

    for cid, (cells, target) in cage_map.items():
        vals = [board[r][c] for r, c in cells]
        s = sum(vals)
        if s != target:
            print(f"  Cage {cid}: sum {s} ≠ target {target}  cells={vals}")
            ok = False
        if len(set(vals)) != len(vals):
            print(f"  Cage {cid}: duplicate values {vals}")
            ok = False

    return ok


def explain_cost(board: list, N: int, block_height: int, block_width: int,
                 cage_map: dict) -> None:
    """Wypisuje szczegółowy rozkład naruszeń ograniczeń składających się na koszt."""
    row_cnt, col_cnt = make_counts(board, N)
    total = 0

    row_issues = []
    for r in range(N):
        c = dup_cost(row_cnt[r], N)
        if c:
            row_issues.append(f"    wiersz {r + 1}: {c} kara (duplikaty: "
                              f"{[v for v in range(1, N+1) if row_cnt[r][v] > 1]})") 
            total += c

    col_issues = []
    for c in range(N):
        cost = dup_cost(col_cnt[c], N)
        if cost:
            col_issues.append(f"    kolumna {c + 1}: {cost} kara (duplikaty: "
                              f"{[v for v in range(1, N+1) if col_cnt[c][v] > 1]})")
            total += cost

    cage_issues = []
    for cid, (cells, target) in sorted(cage_map.items()):
        vals = [board[r][c] for r, c in cells]
        s = sum(vals)
        dup = sum(v - 1 for v in Counter(vals).values() if v > 1)
        cage_c = abs(s - target) + dup
        if cage_c:
            msg = f"    klatka {cid:3d}: {cage_c} kara"
            if s != target:
                msg += f" (suma {s} ≠ cel {target}, różnica {s - target:+d})"
            if dup:
                msg += f" (duplikaty: {vals})"
            cage_issues.append(msg)
            total += cage_c

    print(f"\nRozkład kosztu (łącznie: {total}):")
    if row_issues:
        print(f"  Wiersze ({sum(int(l.split(':')[1].split()[0]) for l in row_issues)} pkt):")
        for line in row_issues:
            print(line)
    else:
        print("  Wiersze: brak naruszeń")

    if col_issues:
        print(f"  Kolumny ({sum(int(l.split(':')[1].split()[0]) for l in col_issues)} pkt):")
        for line in col_issues:
            print(line)
    else:
        print("  Kolumny: brak naruszeń")

    if cage_issues:
        print(f"  Klatki ({sum(int(l.split(':')[1].split()[0]) for l in cage_issues)} pkt):")
        for line in cage_issues:
            print(line)
    else:
        print("  Klatki: brak naruszeń")


# Entry point

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description="Killer Sudoku solver - Tabu Search",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "puzzle", nargs="?", metavar="FILE",
        help="Plik z puzzlem w formacie .dat (domyślnie: wbudowany przykład)",
    )
    parser.add_argument(
        "--time-limit", type=float, default=300.0, metavar="SEKUNDY",
        help="Maksymalny czas działania solvera w sekundach",
    )
    parser.add_argument(
        "--tabu-tenure", type=int, default=15, metavar="ITERACJE",
        help="Liczba iteracji, przez którą ruch pozostaje na liście tabu",
    )
    parser.add_argument(
        "--max-iter", type=int, default=10000, metavar="N",
        help="Maksymalna liczba iteracji w jednym restarcie",
    )
    parser.add_argument(
        "--max-restarts", type=int, default=100, metavar="N",
        help="Maksymalna liczba restartów",
    )
    parser.add_argument(
        "--stagnation-limit", type=int, default=600, metavar="ITERACJE",
        help="Liczba iteracji bez poprawy po której następuje restart",
    )
    args = parser.parse_args()

    if args.puzzle:
        with open(args.puzzle) as fh:
            text = fh.read()
    else:
        text = EXAMPLE_PUZZLE

    block_height, block_width, cage_id_matrix, cage_targets = parse_puzzle(text)
    N = block_height * block_width
    cage_map, cell_to_cage = build_structures(cage_id_matrix, cage_targets)

    print(
        f"Puzzle: {N}x{N}, block {block_height}x{block_width}, {len(cage_map)} klatek\n"
        f"  limit czasu:      {args.time_limit} s\n"
        f"  rozmiar listy tabu: {args.tabu_tenure}\n"
        f"  max iteracji:     {args.max_iter}\n"
        f"  max restartów:    {args.max_restarts}\n"
        f"  limit stagnacji:  {args.stagnation_limit}",
        file=sys.stderr,
    )
    print("", file=sys.stderr)

    board, cost = tabu_search(
        N, block_height, block_width, cage_map, cell_to_cage,
        max_iter=args.max_iter,
        tabu_tenure=args.tabu_tenure,
        max_restarts=args.max_restarts,
        stagnation_limit=args.stagnation_limit,
        time_limit=args.time_limit,
    )

    print("", file=sys.stderr)
    if cost == 0:
        print("Solution found!\n")
    else:
        print(f"Best solution found (cost = {cost}):\n")

    print_board(board, N, block_height, block_width)
    explain_cost(board, N, block_height, block_width, cage_map)

    if cost == 0:
        ok = verify(board, N, block_height, block_width, cage_map)
        print("\nVerification:", "PASSED" if ok else "FAILED")
