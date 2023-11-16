import hashlib

shared_array_chunk_size = 4


def calculate_hash(latest_terminating_hashes, max_iterations, hash_in_decimal, index_in_array, shared_array) -> None:
    m = hashlib.sha256()
    m.update(str.encode(hash_in_decimal))
    hex_digest = m.hexdigest()

    # Each Process will use 4 sequential elements in shared_array
    # Index 0 = iteration, Index 1 = found winning hash, Index 2 = loop has completed
    # Index 3 = if there is a winner, index of that winner in terminating_hash_list
    # Example cpu_count was 2
    # shared_array = [0, 0, 0, 0, 0, 0, 0, 0]
    # shared_array = [idx0-0, idx0-1, idx0-2, idx0-3, idx1-0, idx1-1, idx1-2, idx1-3]

    shared_array[shared_array_chunk_size * index_in_array + 1] = 0
    shared_array[shared_array_chunk_size * index_in_array + 2] = 0
    for iteration in range(max_iterations):
        shared_array[shared_array_chunk_size * index_in_array] = iteration
        if hex_digest in latest_terminating_hashes:
            winning_index = latest_terminating_hashes.index(hex_digest)
            shared_array[shared_array_chunk_size * index_in_array + 1] = 1  # indicates winner is found
            shared_array[shared_array_chunk_size * index_in_array + 3] = winning_index
            break

        m = hashlib.sha256()
        m.update(str.encode(hex_digest))
        hex_digest = m.hexdigest()

    shared_array[shared_array_chunk_size * index_in_array + 2] = 1


def median(lst):
    quotient, remainder = divmod(len(lst), 2)
    if remainder:
        return sorted(lst)[quotient]
    return sum(sorted(lst)[quotient - 1:quotient + 1]) / 2