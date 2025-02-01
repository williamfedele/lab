from bitarray import bitarray
from faker import Faker
import mmh3
import math
import sys
import random

# Bloom filters are probabilistic data strucures that can be used in place
# of a set (if rare false positives are acceptable) for considerable space
# complexity improvements


# The Bloom filter is represented as an array of bits
# Items are added to the Bloom filter using numerous hashing functions
# Each hash function value for the item dictates which index of the bit array
#   is set to 1
# False positives are possible if the item's hash values have already been
#   set to 1 by other items over time
# False negative are impossible. A false negative would occur if any of the
#   item's hash values are not 1. Though since a bit set to 1 stays set to 1,
#   we can assuredly say that the item is not in the set
class BloomFilter:
    def __init__(self, false_pos_prob, num_items):
        self.filter_size = self.calculate_filter_size(false_pos_prob, num_items)
        self.num_hashes = math.ceil(self.calculate_number_hashes(false_pos_prob))
        self.filter_size = math.ceil(self.filter_size)

        self.bit_array = bitarray(self.filter_size)
        self.bit_array.setall(0)

    # Size of the bloom filter depends on the number of items and tolerable false positive rate
    # Calculated as m = -(n*ln(p))/(ln(2))^2 where n is the number of items
    #   and p is the target false positive probability
    def calculate_filter_size(self, false_pos_prob, num_items):
        return -(num_items * math.log(false_pos_prob)) / (math.log(2)) ** 2

    # Number of hash functions to use depends on the target false positive probability
    # Calculated as -ln(p)/ln(2) where p is the target false positive probability
    def calculate_number_hashes(self, false_pos_prob):
        return -math.log(false_pos_prob) / math.log(2)

    # Using 0..num_hashes as a seed for the MurmurHash, we get multiple different hash values
    #   for the same index and set each to 1
    def add(self, item):
        for i in range(self.num_hashes):
            hash = mmh3.hash(item, i) % self.filter_size
            self.bit_array[hash] = 1

    # Using 0..num_hashes as a seed for the MurmurHash, we get the items's associated hash
    #   values and make sure each is 1 to determine if the item is possibly in the set
    # If any index is 0, we can say with certainty that the item is not in the set
    def contains(self, item):
        for i in range(self.num_hashes):
            hash = mmh3.hash(item, i) % self.filter_size
            if self.bit_array[hash] == 0:
                return False  # 100% not in the filter
        return True  # Possibly in the filter


def generate_emails(num_items=1000):
    fake = Faker()

    valid_emails = set()  # emails inserted into Bloom filter
    test_emails = set()  # subset of emails in the Bloom filter
    invalid_emails = set()  # emails that are not in the Bloom filter

    while len(valid_emails) < num_items:
        email = fake.email()
        valid_emails.add(email)
        # Take roughly have the dataset for testing membership
        if random.choice([0, 1]) == 1:
            test_emails.add(email)

    # Non existent elements for testing non membership
    while len(invalid_emails) < num_items:
        email = fake.email()
        if email not in valid_emails:
            invalid_emails.add(fake.email())

    return list(valid_emails), list(test_emails), list(invalid_emails)


if __name__ == "__main__":
    # Random data
    valid_emails, test_emails, invalid_emails = generate_emails(10000)

    false_pos_prob = 0.01
    bloom_filter = BloomFilter(false_pos_prob, len(valid_emails))
    for email in valid_emails:
        bloom_filter.add(email)

    false_positives = 0
    false_negatives = 0

    # Check if invalid emails are in the bloom filter -> false positives
    for email in invalid_emails:
        if bloom_filter.contains(email):
            false_positives += 1

    # Check if valid emails are not in the bloom filter -> false negatives
    for email in test_emails:
        if not bloom_filter.contains(email):
            false_negatives += 1

    # Estimate size of a set implementation
    # A set would not have false positives but would take up much more space
    email_set = set(valid_emails)
    set_size = sys.getsizeof(email_set)
    set_total_email_size = sum(sys.getsizeof(email) for email in email_set)
    total_set_size = set_size + set_total_email_size

    # Get size of bloom filter
    bf_instance_size = sys.getsizeof(bloom_filter)  # Instance size
    bf_bitarray_size = sys.getsizeof(bloom_filter.bit_array)
    bf_num_hashes_size = sys.getsizeof(bloom_filter.num_hashes)
    total_bf_size = bf_instance_size + bf_bitarray_size + bf_num_hashes_size

    size_diff = (total_set_size - total_bf_size) / (total_set_size) * 100

    print("Memory:")
    print(f"    Bloom filter memory: {total_bf_size} bytes")
    print(f"    Set version  memory: {total_set_size} bytes")
    print(f"    Saved {size_diff:.2f}% space!")

    print()

    print("Bloom Filter Stats:")
    print(f"    Filter size: {bloom_filter.filter_size}")
    print(f"    Number of hash functions: {bloom_filter.num_hashes}")
    print(f"    False positives: {false_positives}")
    print(f"    False positive rate: {false_positives / len(valid_emails)}")
    print(f"    False negatives: {false_negatives}")
    print(f"    False negative rate: {false_negatives / len(invalid_emails)}")
