# Calculate where two calculatins of Pi differ in precision
def find_diff_index(n1, n2):
    for i, (d1, d2) in enumerate(zip(str(n1), str(n2))):
        if d1 != d2:
            return i
    return len(str(n1))
