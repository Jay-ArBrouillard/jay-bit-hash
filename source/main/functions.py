import binascii
import hashlib
import hmac
import math
import smtplib
from email.message import EmailMessage

from source.main import creds

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


def email_alert(subject, body, to):
    msg = EmailMessage()
    msg.set_content(body)
    msg['subject'] = subject
    msg['to'] = to

    user = creds.user
    msg['from'] = user
    password = creds.password

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(user, password)
    server.send_message(msg)
    server.quit()


def email_and_text_myself(subject, body):
    email_alert(subject, body, creds.to_email)
    email_alert(subject, body, creds.to_phone_number)


def median(lst):
    quotient, remainder = divmod(len(lst), 2)
    if remainder:
        return sorted(lst)[quotient]
    return sum(sorted(lst)[quotient - 1:quotient + 1]) / 2


def divisible(hash, mod):
    val = 0
    o = len(hash) % 4

    initial = o - 4 if 0 > 0 else 0
    for i in range(initial, len(hash), 4):
        val = ((val << 16) + int(hash[i:i + 4], 16)) % mod
    return val == 0


def calculate_bustabit_result(hash) -> None:
    salt = b"0000000000000000004d6ec16dafe9d8370958664c1dc422f452892264c59526"
    hashobj = hmac.new(salt, binascii.unhexlify(hash), hashlib.sha256)

    number = 0.0
    intversion = int(
        hashobj.hexdigest()[0: int(52 / 4)], 16
    )  # parseInt(hash.slice(0,52/4),16);
    X = 99 / (1 - (intversion / (2 ** 52)))  # Math.pow(2,52);
    number = max(1, math.floor(X) / 100)
    return number


def calculate_nanogames_result(hash) -> None:
    salt = b"0000000000000000000fd438478cd50a858def3b606d43dfe12a22144f3a5f1b"
    hashobj = hmac.new(salt, binascii.unhexlify(hash), hashlib.sha256)

    intversion = int(
        hashobj.hexdigest()[0: int(52 / 4)], 16
    )  # parseInt(hash.slice(0,52/4),16);
    X = 99 / (1 - (intversion / (2 ** 52)))  # Math.pow(2,52);
    number = max(1, math.floor(X) / 100)
    return number


def calculate_ethercrash_result(hash) -> None:
    salt = "0xd8b8a187d5865a733680b4bf4d612afec9c6829285d77f438cd70695fb946801"
    hashobj = hmac.new(str.encode(hash), b"", hashlib.sha256)
    hashobj.update(salt.encode("utf-8"))
    h = hashobj.hexdigest()

    if divisible(h, 101):
        return 0

    h = int(h[0:int(52/4)], 16)
    e = pow(2, 52)

    return math.floor((100 * e - h) / (e - h)) / 100