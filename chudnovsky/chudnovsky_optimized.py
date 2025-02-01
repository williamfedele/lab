from decimal import Decimal, getcontext
from time import time
import sys
from common import find_diff_index


# C1 = Decimal(426880) * Decimal(10005).sqrt()
C2 = Decimal(13591409)


def binary_split(a, b):
    # Base case
    if b == a + 1:
        Pab = (-1) * (6 * a - 1) * (2 * a - 1) * (6 * a - 5)
        Qab = 10939058860032000 * a**3
        Rab = Pab * (545140134 * a + 13591409)
    else:
        m = (a + b) // 2
        Pam, Qam, Ram = binary_split(a, m)
        Pmb, Qmb, Rmb = binary_split(m, b)

        Pab = Pam * Pmb
        Qab = Qam * Qmb
        Rab = Qmb * Ram + Pam * Rmb

    return Pab, Qab, Rab


# Function to compute pi using the Chudnovsky series optimized with binary splitting.
def chudnovsky_term(num_terms):
    P1n, Q1n, R1n = binary_split(1, num_terms)
    return (C1 * Q1n) / (C2 * Q1n + R1n)


def chudnovsky_precision(precision):
    getcontext().prec = precision + int(precision * 1 / 10)

    # Need to increase precision before performing sqrt
    global C1
    C1 = Decimal(426880) * Decimal(10005).sqrt()

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
