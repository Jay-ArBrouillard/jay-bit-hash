import hashlib

from source.main.functions import calculate_bustabit_result, calculate_ethercrash_result, calculate_nanogames_result

winning_hash = "9b7ef15994122eb6042bc8f9cd5fa770d8a051b5e4b5154fdfc051ba505f9d64"
terminating_hash = "38b2bdcf8402a0403f138333fda75fd15d8062fb1bbfe1566f51de0dc89c8ff9"

iterations = 9000000
print_last_lines = 1000  # Value of 1000 means only print the last 1000 lines to the file. Value of None means print everything

# Use this program to return list of hashes with their corresponding game result
def generate_result_file(name="bustabit"):
    success = False
    f = open(f"{name}_verify.txt", 'w+')
    f.truncate(0)  # need '0' when using r+

    store_last_n_lines = None if print_last_lines is None else []

    m = hashlib.sha256()
    m.update(str.encode(winning_hash))
    hex_digest = m.hexdigest()

    game_result = calculate_bustabit_result(winning_hash) if name == "bustabit" \
        else calculate_ethercrash_result(winning_hash) if name == "ethercrash" \
        else calculate_nanogames_result(winning_hash)

    if store_last_n_lines is not None:
        store_last_n_lines.append(f"{hex_digest} {game_result}\n")
    else:
        f.write(f"{winning_hash} {game_result}\n")

    for i in range(iterations):
        if i % 1000 == 0:
            print(f"{i}/{iterations}")
        game_result = calculate_bustabit_result(hex_digest) if name == "bustabit" \
            else calculate_ethercrash_result(hex_digest) if name == "ethercrash" \
            else calculate_nanogames_result(hex_digest)
        if store_last_n_lines is not None:
            # write to a list, write to list to file later
            store_last_n_lines.append(f"{hex_digest} {game_result}\n")
            if len(store_last_n_lines) > print_last_lines:
                store_last_n_lines.remove(store_last_n_lines[0])
        else:
            # write every line to file
            f.write(f"{hex_digest} {game_result}\n")
        if hex_digest == terminating_hash:
            print("Found matching hash")
            success = True
            break

        m = hashlib.sha256()
        m.update(str.encode(hex_digest))
        hex_digest = m.hexdigest()

    # write to file now if print_last_lines is set
    if store_last_n_lines is not None:
        for line in store_last_n_lines:
            f.write(line)
    f.close()

    print(f"{name} Success" if success else f"{name} Fail")


if __name__ == '__main__':
    generate_result_file("nanogames")
