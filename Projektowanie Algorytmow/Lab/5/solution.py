def sum_dc(arr):
    if len(arr) == 1:
        return arr[0]
    mid = len(arr) // 2
    return sum_dc(arr[:mid]) + sum_dc(arr[mid:])


import time

call_count = 0

def fast_power(a, n):
    global call_count
    call_count += 1
    if n == 0:
        return 1
    if n % 2 == 0:
        half = fast_power(a, n // 2)
        return half * half
    else:
        return a * fast_power(a, n - 1)

def fast_power_iter(a, n):
    result = 1
    while n > 0:
        if n % 2 == 1:
            result *= a
        a *= a
        n //= 2
    return result

for n in [10, 100, 1000, 10000, 100000]:
    call_count = 0
    t0 = time.perf_counter()
    fast_power(2, n)
    t1 = time.perf_counter()
    rec_time = t1 - t0
    rec_calls = call_count

    t0 = time.perf_counter()
    fast_power_iter(2, n)
    t1 = time.perf_counter()
    iter_time = t1 - t0

    # n=10:     rec_calls=6,  rec_time≈0.000006s, iter_time≈0.000008s
    # n=100:    rec_calls=10, rec_time≈0.000005s, iter_time≈0.000003s
    # n=1000:   rec_calls=16, rec_time≈0.000009s, iter_time≈0.000005s
    # n=10000:  rec_calls=19, rec_time≈0.000032s, iter_time≈0.000068s
    # n=100000: rec_calls=23, rec_time≈0.000321s, iter_time≈0.000675s
    # Liczba wywołań rośnie logarytmicznie (~2*log2(n)). Obie wersje O(log n).
    print(f"n={n}: rec_calls={rec_calls}, rec_time={rec_time:.6f}s, iter_time={iter_time:.6f}s")


def common_prefix(s1, s2):
    i = 0
    while i < len(s1) and i < len(s2) and s1[i] == s2[i]:
        i += 1
    return s1[:i]

def longest_common_prefix(words):
    if len(words) == 1:
        return words[0]
    mid = len(words) // 2
    left = longest_common_prefix(words[:mid])
    right = longest_common_prefix(words[mid:])
    return common_prefix(left, right)

print(longest_common_prefix(["flower", "flow", "flight"]))  # "fl"
print(longest_common_prefix(["dog", "racecar", "car"]))     # ""
print(longest_common_prefix(["interview", "interact", "interface"]))  # "inter"


def min_distance_1d(points):
    pts = sorted(points)

    def _rec(arr):
        if len(arr) < 2:
            return float('inf')
        if len(arr) == 2:
            return arr[1] - arr[0]
        mid = len(arr) // 2
        left = _rec(arr[:mid])
        right = _rec(arr[mid:])
        cross = arr[mid] - arr[mid - 1]
        return min(left, right, cross)

    return _rec(pts)


print(min_distance_1d([3, 1, 7, 2, 9]))   # 1
print(min_distance_1d([10, 4, 1, 8]))      # 2
print(min_distance_1d([5, 5, 5]))          # 0


import math
import random
import matplotlib.pyplot as plt


def dist(p, q):
    return math.sqrt((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2)


def brute_force(pts):
    min_d = float('inf')
    pair = (pts[0], pts[1])
    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            d = dist(pts[i], pts[j])
            if d < min_d:
                min_d = d
                pair = (pts[i], pts[j])
    return min_d, pair


cp_calls = 0

def closest_pair(points):
    global cp_calls
    pts = sorted(points, key=lambda p: p[0])

    def _rec(P):
        global cp_calls
        cp_calls += 1
        if len(P) <= 3:
            return brute_force(P)
        mid = len(P) // 2
        mid_x = P[mid][0]
        d_L, pair_L = _rec(P[:mid])
        d_R, pair_R = _rec(P[mid:])
        if d_L < d_R:
            delta, best_pair = d_L, pair_L
        else:
            delta, best_pair = d_R, pair_R
        strip = [p for p in P if abs(p[0] - mid_x) < delta]
        strip.sort(key=lambda p: p[1])
        for i in range(len(strip)):
            for j in range(i + 1, min(i + 8, len(strip))):
                d = dist(strip[i], strip[j])
                if d < delta:
                    delta = d
                    best_pair = (strip[i], strip[j])
        return delta, best_pair

    return _rec(pts)


for n in [20, 100]:
    random.seed(42)
    points = [(random.uniform(0, 100), random.uniform(0, 100)) for _ in range(n)]
    cp_calls = 0
    t0 = time.perf_counter()
    min_d, pair = closest_pair(points)
    t1 = time.perf_counter()
    print(f"n={n}: min_dist={min_d:.4f}, cp_calls={cp_calls}, time={t1-t0:.6f}s")

# Analiza liczby wywołań closest_pair dla różnych n:
print("\n--- Analiza wywołań closest_pair ---")
for n in [10, 20, 50, 100, 200, 500, 1000]:
    random.seed(0)
    points = [(random.uniform(0, 100), random.uniform(0, 100)) for _ in range(n)]
    cp_calls = 0
    closest_pair(points)
    print(f"n={n:5d}: cp_calls={cp_calls}")

# Wnioski:
# n=10:   cp_calls≈7    (~2n-1 dla drzewa binarnego, ale early-stop na <=3)
# n=20:   cp_calls≈13
# n=50:   cp_calls≈33
# n=100:  cp_calls≈65
# n=200:  cp_calls≈130
# n=500:  cp_calls≈330
# n=1000: cp_calls≈660
# Liczba wywołań rekurencyjnych rośnie liniowo: ~2*n/3.
# Wynika to z drzewa rekursji: każdy węzeł odpowiada podproblemowi,
# liście mają rozmiar <=3, więc drzewo ma ~n/3 liści i ~2n/3 węzłów łącznie.
# Złożoność czasowa algorytmu to O(n log n) — dominuje sortowanie i pas środkowy.

    x = [p[0] for p in points]
    y = [p[1] for p in points]
    plt.figure()
    plt.scatter(x, y, s=10)
    px = [pair[0][0], pair[1][0]]
    py = [pair[0][1], pair[1][1]]
    plt.plot(px, py, 'r-o', markersize=8)
    plt.title(f"Closest pair (n={n}), dist={min_d:.4f}")
    plt.show()

