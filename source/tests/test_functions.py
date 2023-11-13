import multiprocessing

import functions as my_functions
from main import shared_array_chunk_size


def test_calculate_hash_1_1_iteration_success():
    latest_terminating_hashes = ["0228480a1ef589025a923f66ff628157e7ac14f03d9d82bcf6c2c98c1751f4df"]
    current_hash = "4b271f3f2260c8ae88968131ceb6ed9837c1449818b0ab492237995d28debd3f"
    shared_array = multiprocessing.Array('i', shared_array_chunk_size)
    my_functions.calculate_hash(latest_terminating_hashes, 1, current_hash, 0, shared_array)

    assert shared_array[0] == 0
    assert shared_array[1] == 1
    assert shared_array[2] == 1
    assert shared_array[3] == 0


def test_calculate_hash_1_1_iteration_fail():
    latest_terminating_hashes = ["634efe362ead8929fe79d4f42a9cc6c592cbe1ac9568fe04daca675c9f162abd"]
    current_hash = "4cd119efb2319abd647f512af48b6940f1b99d3db0a24b8b9367e1677eedc200"
    shared_array = multiprocessing.Array('i', shared_array_chunk_size)
    my_functions.calculate_hash(latest_terminating_hashes, 1, current_hash, 0, shared_array)

    assert shared_array[0] == 0
    assert shared_array[1] == 0
    assert shared_array[2] == 1
    assert shared_array[3] == 0


def test_calculate_hash_1_1000_iteration_success():
    latest_terminating_hashes = ["86728f5fc3bd99db94d3cdaf105d67788194e9701bf95d049ad0e1ee3d004277"]
    current_hash = "216f014579a1cff543b210d0b03967a107a81f6a6240bb39927b453cb9791fa6"
    shared_array = multiprocessing.Array('i', shared_array_chunk_size)
    my_functions.calculate_hash(latest_terminating_hashes, 1000, current_hash, 0, shared_array)

    assert shared_array[0] == 999
    assert shared_array[1] == 1
    assert shared_array[2] == 1
    assert shared_array[3] == 0


def test_calculate_hash_1_1000_iteration_fail():
    latest_terminating_hashes = ["86728f5fc3bd99db94d3cdaf105d67788194e9701bf95d049ad0e1ee3d004277"]
    current_hash = "49d2ebb0eeca3aa71594172f55f9a0e369962014a5961a1251b56008ce9fa761"
    shared_array = multiprocessing.Array('i', shared_array_chunk_size)
    my_functions.calculate_hash(latest_terminating_hashes, 1000, current_hash, 0, shared_array)

    assert shared_array[0] == 999
    assert shared_array[1] == 0
    assert shared_array[2] == 1
    assert shared_array[3] == 0


def test_calculate_hash_2_1_iteration_success():
    latest_terminating_hashes = ["dummy", "0228480a1ef589025a923f66ff628157e7ac14f03d9d82bcf6c2c98c1751f4df"]
    current_hash = "4b271f3f2260c8ae88968131ceb6ed9837c1449818b0ab492237995d28debd3f"
    shared_array = multiprocessing.Array('i', 2 * shared_array_chunk_size)
    my_functions.calculate_hash(latest_terminating_hashes, 1, current_hash, 1, shared_array)

    assert shared_array[4] == 0
    assert shared_array[5] == 1
    assert shared_array[6] == 1
    assert shared_array[7] == 1


def test_calculate_hash_2_1_iteration_fail():
    latest_terminating_hashes = ["dummy", "0228480a1ef589025a923f66ff628157e7ac14f03d9d82bcf6c2c98c1751f4df"]
    current_hash = "4b271f3f2260c8ae88968131ceb6ed9837c1449818b0ab492237995d28debd3f"
    shared_array = multiprocessing.Array('i', 2 * shared_array_chunk_size)
    my_functions.calculate_hash(latest_terminating_hashes, 1, current_hash, 0, shared_array)

    assert shared_array[4] == 0
    assert shared_array[5] != 1
    assert shared_array[6] != 1
    assert shared_array[7] != 1


def test_calculate_hash_2_1000_iteration_success():
    latest_terminating_hashes = ["dummy", "86728f5fc3bd99db94d3cdaf105d67788194e9701bf95d049ad0e1ee3d004277"]
    current_hash = "216f014579a1cff543b210d0b03967a107a81f6a6240bb39927b453cb9791fa6"
    shared_array = multiprocessing.Array('i', 2 * shared_array_chunk_size)
    my_functions.calculate_hash(latest_terminating_hashes, 1000, current_hash, 1, shared_array)

    assert shared_array[4] == 999
    assert shared_array[5] == 1
    assert shared_array[6] == 1
    assert shared_array[7] == 1


def test_calculate_hash_2_1000_iteration_fail():
    latest_terminating_hashes = ["dummy", "86728f5fc3bd99db94d3cdaf105d67788194e9701bf95d049ad0e1ee3d004277"]
    current_hash = "49d2ebb0eeca3aa71594172f55f9a0e369962014a5961a1251b56008ce9fa761"
    shared_array = multiprocessing.Array('i', 2 * shared_array_chunk_size)
    my_functions.calculate_hash(latest_terminating_hashes, 1000, current_hash, 0, shared_array)

    assert shared_array[4] == 0
    assert shared_array[5] != 1
    assert shared_array[6] != 1
    assert shared_array[7] != 1




