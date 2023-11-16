import multiprocessing

from source.main import functions as my_functions
from source.main.sha256 import shared_array_chunk_size


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


def test_bustabit_game_results():
    assert my_functions.calculate_bustabit_result("332901b7b469b69d544597767849b36767fe86925b5d01de04e70c468b60b903") == 1.00
    assert my_functions.calculate_bustabit_result("533473d9e1e0ddc9cabe769c4eff4bf05959a346a770ee7fc580c8eff0300d09") == 36.18
    assert my_functions.calculate_bustabit_result("dd6f372d0a177b83284e3d094676deea6062008ba142aee433e6342ee21de8f4") == 48.93
    assert my_functions.calculate_bustabit_result("3add5306be1ad9679f8aa572cc08a79987de14249f3f582c59d0b4eaff4a390c") == 1.69


def test_ethercrash_game_results():
    assert my_functions.calculate_ethercrash_result("4a9cb9f7d64d5bfaa0d72efc8c73cc01f2dd48ac80bdd5bf758102ea883d3de8") == 1.00
    assert my_functions.calculate_ethercrash_result("d180bccc21ca9003a50c9d65a8f28a2faa51735f9328e60271a97961c19da269") == 76.57
    assert my_functions.calculate_ethercrash_result("a3f3177d7bc5155051a1566c09378a2bf2c8b09e419d279b5e952277f0b25e15") == 1.06


def test_nanogames_game_results():
    assert my_functions.calculate_nanogames_result("de7d6429a7d7cb48fe7a17a5d18b35f8f0bacaf03f1b434bf7e73c329c5785ea") == 371.61
    assert my_functions.calculate_nanogames_result("e84302ca531aa10b82966918ea6f36eec0c4cdb31474f7e2149f1c3e4b62b4a0") == 7.20
    assert my_functions.calculate_nanogames_result("278d960cd7036fac56348819af86e2e324ccae6549b92596cb6ebfd6a030c8d7") == 1.00
    assert my_functions.calculate_nanogames_result("f2ece978c2a532083b8df6ffdc0e68f4f4fd9cd45bf63a246a586ed4888426da") == 1.09



