from decimal import Decimal, getcontext
import math
import sys
from time import time, sleep
from common import find_diff_index

# Constants
C1 = Decimal(545140134)
C2 = Decimal(13591409)
C3 = Decimal(640320)


# Function to compute the k-th term of the Chudnovsky series
def chudnovsky(k):
    # Calculate the factorials
    fac6k = Decimal(math.factorial(6 * k))
    fac3k = Decimal(math.factorial(3 * k))
    fac1k = Decimal(math.factorial(1 * k))

    # Numerator and denominator for the k-th term
    numerator = fac6k * (C1 * k + C2)
    denominator = fac3k * fac1k**3 * C3 ** (3 * k + Decimal(3) / 2)

    # Return the k-th term with the alternating sign (-1)^k
    return Decimal((-1) ** k) * (numerator / denominator)


# Function to compute pi using the Chudnovsky series
def chudnovsky_term(num_terms):
    series_sum = Decimal(0)
    for k in range(num_terms):
        series_sum += chudnovsky(k)
    # Multiply by 12 to get 1/pi
    return Decimal(1) / (Decimal(12) * series_sum)


def chudnovsky_precision(precision):
    getcontext().prec = precision + int(precision * 1 / 10)

    terms = 2
    prev = Decimal(0)

    while True:
        curr = chudnovsky_term(terms)
        diff_idx = find_diff_index(prev, curr)
        if diff_idx > precision:
            return curr, terms, diff_idx

        prev = curr
        terms += 1


if __name__ == "__main__":
    pass
