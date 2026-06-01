import random

def get_options(board, r, c, N, block_size):
    used = set(board[r])
    used.update(board[i][c] for i in range(N))
    br, bc = (r // block_size) * block_size, (c // block_size) * block_size
    for i in range(block_size):
        for j in range(block_size):
            used.add(board[br + i][bc + j])
    return [x for x in range(1, N + 1) if x not in used and x != 0]

def generate_solved_sudoku(N, block_size):
    board = [[0] * N for _ in range(N)]
    def solve():
        best_r, best_c, min_opts = -1, -1, N + 1
        for r in range(N):
            for c in range(N):
                if board[r][c] == 0:
                    opts = get_options(board, r, c, N, block_size)
                    if len(opts) < min_opts:
                        min_opts, best_r, best_c = len(opts), r, c
        if best_r == -1: return True
        if min_opts == 0: return False
        for num in random.sample(get_options(board, best_r, best_c, N, block_size), min_opts):
            board[best_r][best_c] = num
            if solve(): return True
            board[best_r][best_c] = 0
        return False
    solve()
    return board

def generate_killer_cages(board, N):
    cage_id_matrix = [[0] * N for _ in range(N)]
    current_cage_id, cage_targets = 1, []
    for r in range(N):
        for c in range(N):
            if cage_id_matrix[r][c] == 0:
                size = random.randint(2, 5)
                cells, vals = [(r, c)], {board[r][c]}
                cage_id_matrix[r][c] = current_cage_id
                while len(cells) < size:
                    neighbors = []
                    for cr, cc in cells:
                        for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
                            nr, nc = cr + dr, cc + dc
                            if 0 <= nr < N and 0 <= nc < N and cage_id_matrix[nr][nc] == 0:
                                if board[nr][nc] not in vals: neighbors.append((nr, nc))
                    if not neighbors: break
                    nr, nc = random.choice(list(set(neighbors)))
                    cage_id_matrix[nr][nc] = current_cage_id
                    cells.append((nr, nc))
                    vals.add(board[nr][nc])
                cage_targets.append(sum(board[cr][cc] for cr, cc in cells))
                current_cage_id += 1
    return cage_id_matrix, cage_targets

side = int(input("Podaj bok bloku (np. 3 dla planszy 9x9): "))
N = side * side
board = generate_solved_sudoku(N, side)
cage_ids, targets = generate_killer_cages(board, N)

print(f"\nBlockHeight = {side};")
print(f"BlockWidth = {side};\n")
print(f"numCages = {len(targets)};\n")
print("cageID = [")
for row in cage_ids: print("  [" + ", ".join(f"{x:3d}" for x in row) + "],")
print("];\n")
print("cageTarget = [" + ", ".join(str(x) for x in targets) + "];")