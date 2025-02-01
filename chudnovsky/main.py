import chudnovsky_optimized
import chudnovsky_unoptimized
from decimal import Decimal, getcontext
from time import time
from common import find_diff_index


DECIMAL_PRECISION = 1000


if __name__ == "__main__":
    print(
        f"\033[95mCalculating Pi with Chudnovsky's algorithm and its optimized version using binary splitting.\n"
    )
    prev = Decimal(0)

    start_time = time()
    pi1, terms, diff_idx = chudnovsky_unoptimized.chudnovsky_precision(
        DECIMAL_PRECISION
    )
    end_time = time()
    print(
        f"\033[96mUnoptimized took {end_time - start_time:.2f}s to reach {diff_idx} digits of Pi in {terms} terms.\n"
    )

    start_time = time()
    pi2, terms, diff_idx = chudnovsky_optimized.chudnovsky_precision(DECIMAL_PRECISION)
    end_time = time()
    print(
        f"\033[96mOptimized took {end_time - start_time:.2f}s to reach {diff_idx} digits of Pi in {terms} terms.\n"
    )

    diff_idx = find_diff_index(pi1, pi2)
    print(
        f"\033[92m{str(pi2)[:DECIMAL_PRECISION]}\033[93m{str(pi2)[DECIMAL_PRECISION:diff_idx]}"
    )
