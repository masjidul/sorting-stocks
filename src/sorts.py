from typing import List, Callable, Any

def _cmp(a, b, reverse: bool) -> bool:
    """Return True if a should come after b (i.e., swap needed)."""
    return (a > b) if not reverse else (a < b)

def bubble_sort(arr: List[Any], reverse: bool=False) -> List[Any]:
    A = arr.copy()
    n = len(A)
    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            if _cmp(A[j], A[j+1], reverse):
                A[j], A[j+1] = A[j+1], A[j]
                swapped = True
        if not swapped:
            break
    return A

def merge_sort(arr: List[Any], reverse: bool=False) -> List[Any]:
    A = arr.copy()

    def merge(left: List[Any], right: List[Any]) -> List[Any]:
        i = j = 0
        out = []
        while i < len(left) and j < len(right):
            if _cmp(left[i], right[j], reverse):
                out.append(right[j])
                j += 1
            else:
                out.append(left[i])
                i += 1
        out.extend(left[i:])
        out.extend(right[j:])
        return out

    def msort(xs: List[Any]) -> List[Any]:
        if len(xs) <= 1:
            return xs
        mid = len(xs) // 2
        return merge(msort(xs[:mid]), msort(xs[mid:]))

    return msort(A)

def quick_sort(arr, reverse: bool=False):
    """
    Robust QuickSort using 3-way (Dutch National Flag) partitioning + random pivot.
    This avoids worst-case recursion on arrays with many equal keys (e.g., 'Company').
    """
    import random
    A = arr.copy()

    def less(a, b):
        return a < b if not reverse else a > b

    def greater(a, b):
        return a > b if not reverse else a < b

    def qsort(lo: int, hi: int):
        if lo >= hi:
            return

        pivot = A[random.randint(lo, hi)]

        lt = lo
        i = lo
        gt = hi

        while i <= gt:
            if less(A[i], pivot):
                A[lt], A[i] = A[i], A[lt]
                lt += 1
                i += 1
            elif greater(A[i], pivot):
                A[i], A[gt] = A[gt], A[i]
                gt -= 1
            else:
                i += 1

        qsort(lo, lt - 1)
        qsort(gt + 1, hi)

    qsort(0, len(A) - 1)
    return A
