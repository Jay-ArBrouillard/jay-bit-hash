import ctypes
import hashlib
import multiprocessing.managers
import os
import random
import string
import struct
import time
from datetime import datetime
from multiprocessing import Process

from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, track
from rich.table import Table
from rich.text import Text
from rich.theme import Theme
from rich.live import Live

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

# Global Variables #
console = Console(record=True, theme=Theme({'success': 'green', 'error': 'bold red', 'init': 'yellow'}))
start_time = time.time()
start_time_2 = time.time()


def make_layout() -> Layout:
    """Define the layout."""
    layout = Layout()
    layout.split_column(
        Layout(name="upper", size=6),
        Layout(name="lower")
    )
    layout["upper"].split_column(
        Layout(name="header", minimum_size=3),
        Layout(name="hash"),
        Layout(name="iterations"),
        Layout(name="winner")
    )
    layout["lower"].split_column(
        Layout(name="overall", size=6),
        Layout(name="progress"),
    )

    return layout


def generate_overall_progress_table(num_hashes) -> Table:
    global start_time
    overall_table = Table(title="Overall Progress", expand=True, border_style="green")
    overall_table.add_column("Hashes Checked")
    overall_table.add_column("Hashes Per Minute")
    overall_table.add_column("Hashes Per Hour")
    overall_table.add_column("Elapsed Time")

    elapsed = time.time() - start_time
    days, hours = divmod(elapsed, 86400)
    hours, minutes = divmod(elapsed, 3600)
    minutes, seconds = divmod(elapsed, 60)
    overall_table.add_row(
        num_hashes,
        str(round(int(num_hashes) / max(1, elapsed / 60), 4)),
        str(round(int(num_hashes) / max(1, elapsed / 3600), 4)),
        "{:0>2}:{:0>2}:{:0>2}:{:05.2f}".format(int(days), int(hours), int(minutes), seconds)
    )
    return overall_table


def generate_thread_table(thread_progress: Progress) -> Table:
    progress_table = Table.grid(expand=True)
    progress_table.add_row(
        Panel(thread_progress, title="[b]Threads", border_style="red", padding=(1, 2)),
    )
    return progress_table


def get_latest_hash_from_site(LATEST_TERMINATING_HASH):
    """Attempt to set LATEST_TERMINATING_HASH from bustabit.com website.
       Be careful not to run this too often as to prevent ip block.
    """
    tries = 3
    for i in range(tries):
        try:
            selenium_options = Options()
            selenium_options.headless = True
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=selenium_options)
            driver.get('https://bustabit.com/play')

            history_tab = driver.find_element(by=By.XPATH,
                                              value="//*[@id=\"root\"]/div/div/div[6]/div/div[1]/ul/li[2]")
            history_tab.click()

            first_row_fifth_col = WebDriverWait(driver, 20).until(
                expected_conditions.visibility_of_element_located((
                    By.XPATH, "//*[@id=\"root\"]/div/div/div[6]/div/div[2]/div/table/tbody/tr[1]/td[5]/input")))
            latest_hash_from_site = first_row_fifth_col.get_attribute('value')
            if latest_hash_from_site is not None and len(latest_hash_from_site) == 64:
                console.print("Successfully found hash from Bustabit.com", style='success')
                return latest_hash_from_site
            else:
                console.print("Did not find hash from Bustabit.com", style='error')
                return LATEST_TERMINATING_HASH
        except:
            if i < tries - 1:  # i is zero indexed
                continue
            else:
                console.print_exception()
        return LATEST_TERMINATING_HASH


# def calculate_hashes_left_in_chain(LATEST_TERMINATING_HASH):
#     """Return the number of hashes left to play in Bustabit game
#        This is calculated by taking the latest hash played and hashing it until we reach the first hash of the chain
#        86728f5fc3bd99db94d3cdaf105d67788194e9701bf95d049ad0e1ee3d004277. After we reach that, we know how many games
#        have been played. At this point just do 10 million subtracted by how games have been played.
#     """
#     m = hashlib.sha256()
#     m.update(str.encode(LATEST_TERMINATING_HASH))
#     hex_digest = m.hexdigest()
#
#     iteration = 1
#     while iteration < 10000000:
#         m = hashlib.sha256()
#         m.update(str.encode(hex_digest))
#         hex_digest = m.hexdigest()
#         if hex_digest == "86728f5fc3bd99db94d3cdaf105d67788194e9701bf95d049ad0e1ee3d004277":
#             break
#         iteration += 1
#     GAMES_LEFT = 10000000 - iteration
#     console.log(f"Bustabit games left to play {GAMES_LEFT}")
#     return GAMES_LEFT


def calculate_hash(terminating_hash_list, MAX_ITERATIONS, random_hash, index_in_array, shared_array):
    m = hashlib.sha256()
    m.update(str.encode(random_hash))
    hex_digest = m.hexdigest()

    # Each Process will use 3 sequential elements in shared_array
    # Index 0 = iteration, Index 1 = found winning hash, Index 2 = loop has completed

    shared_array[3 * index_in_array + 1] = 0
    shared_array[3 * index_in_array + 2] = 0
    for iteration in range(MAX_ITERATIONS + 1):
        shared_array[3 * index_in_array] = iteration
        m = hashlib.sha256()
        m.update(str.encode(hex_digest))
        hex_digest = m.hexdigest()
        if hex_digest in terminating_hash_list:
            shared_array[3 * index_in_array + 1] = 1
            break
    shared_array[3 * index_in_array + 2] = 1


def populate_terminating_hashes(LATEST_TERMINATING_HASH, list_size: int):
    m = hashlib.sha256()
    m.update(str.encode(LATEST_TERMINATING_HASH))
    hex_digest = m.hexdigest()

    list = []
    list.append(LATEST_TERMINATING_HASH)
    list.append(hex_digest)
    for _ in range(list_size-2):
        m = hashlib.sha256()
        m.update(str.encode(hex_digest))
        hex_digest = m.hexdigest()
        list.append(hex_digest)

    return list


def temp(LATEST_TERMINATING_HASH, MAX_ITERATIONS):
    m = hashlib.sha256()
    # m.update(str.encode(random_hash))
    m.update(str.encode("7o8a2mdivghx81b0ju9soed7b45zx0qaem8vkc0vy9f9a1hklas3szjcmut90cnz"))
    hex_digest = m.hexdigest()

    for iteration in range(MAX_ITERATIONS + 1):
        m = hashlib.sha256()
        m.update(str.encode(hex_digest))
        hex_digest = m.hexdigest()
        if hex_digest == "257fdaca2e271dacc231d276e496b929a99bbd0a7d3cb9ce86177d2a789bdb11":
            stop = "s"
            break


if __name__ == '__main__':
    # Default values
    LATEST_TERMINATING_HASH = '563afff49ef50536280ab566f094211a3f9fe74c0067c73371c59a064d5e965c'
    MAX_ITERATIONS = 20160  # About 1 week(s) ahead based on about 30 seconds per game
    processes = []

    LATEST_TERMINATING_HASH = get_latest_hash_from_site(LATEST_TERMINATING_HASH)
    # List of hashes after the LATEST_TERMINATING_HASH. This will improve chances we find a
    # winning hash at the cost of searching through this list in calculate_hash
    terminating_hashes = populate_terminating_hashes(LATEST_TERMINATING_HASH, 100)
    console.log("Using LATEST_TERMINATING_HASH: %s" % LATEST_TERMINATING_HASH)
    # temp(LATEST_TERMINATING_HASH, MAX_ITERATIONS)

    cpu_count = os.cpu_count()
    thread_progress = Progress(
        "{task.description}",
        SpinnerColumn(),
        expand=True
    )

    shared_array = multiprocessing.Array('i', cpu_count * 3)

    for i in track(range(cpu_count), description="Register and Start Processes..."):
        random_hash = ''.join(random.SystemRandom().choice('abcdef' + string.digits) for _ in range(64))
        task_id = thread_progress.add_task(description=f"Thread {i}: {random_hash}", total=MAX_ITERATIONS)
        processes.append(Process(target=calculate_hash,
                                 args=(LATEST_TERMINATING_HASH, MAX_ITERATIONS, random_hash, i, shared_array)))
        processes[i].start()

    grid = Table.grid(expand=True)
    grid.add_column(justify="center", ratio=1)
    grid.add_column(justify="right")
    grid.add_row(
        "[b]Jay-Ar's[/b] Bustabit Hash Cracker Application (Terminal program)",
        "Start Date: " + datetime.now().ctime(),
    )

    layout = make_layout()
    layout["header"].update(Panel(grid, style="white"))
    layout["hash"].update(Text(f"Terminating Hash List: [{terminating_hashes[0]} ... {terminating_hashes[len(terminating_hashes)-1]}]", style="bold magenta"))
    layout["iterations"].update(Text(f"Maximum Hashes Executed Per Thread: {MAX_ITERATIONS}", style="bold magenta"))
    layout["winner"].update(Text("Winning hash: N/A", style="bold yellow"))
    layout["overall"].update(generate_overall_progress_table("0"))
    layout["progress"].update(generate_thread_table(thread_progress))

    hashes_checked = 0
    with Live(layout, refresh_per_second=1, screen=True):
        while True:
            time.sleep(0.1)
            for index, task in enumerate(thread_progress.tasks):
                # Task not done yet
                if shared_array[3 * index + 2] == 0:
                    task.completed = shared_array[3 * index]
                else:
                    shared_array[3 * index + 2] = 0
                    shared_array[3 * index] = 0
                    if shared_array[3 * index + 1] == 1:
                        # splitting description i.e. Thread i: <hash>
                        hash = task.description.split(" ")[2]
                        console.log(f"WINNER, WINNER CHICKEN DINNER: {hash}")
                        layout["winner"].update(Text(f"Winning hash: {hash}", style="bold cyan"))
                        console.save_html("output_winner.html")
                        # Remove all threads/tasks
                        for temp in thread_progress.tasks:
                            thread_progress.remove_task(task_id=temp.id)
                        for process in processes:
                            process.terminate()
                    else:
                        random_hash = ''.join(
                            random.SystemRandom().choice('abcdef' + string.digits) for _ in range(64))
                        for idx, task_id in enumerate(thread_progress.task_ids):
                            if task_id == task.id:
                                processes[index].terminate()
                                thread_progress.tasks[task_id].completed = 0
                                thread_progress.tasks[task_id].total = MAX_ITERATIONS
                                thread_progress.tasks[task_id].description = f"Thread {idx}: {random_hash}"
                                processes[index] = Process(target=calculate_hash, args=(
                                    LATEST_TERMINATING_HASH, MAX_ITERATIONS, random_hash, idx, shared_array))
                                processes[index].start()
                                break
                        hashes_checked += 1
                        layout["overall"].update(generate_overall_progress_table(str(hashes_checked)))

                        # Grab the latest terminating hash from bustabit.com every x minutes
                        elapsed_seconds = time.time() - start_time_2
                        if elapsed_seconds / 60 >= 5:
                            original = LATEST_TERMINATING_HASH
                            LATEST_TERMINATING_HASH = get_latest_hash_from_site(LATEST_TERMINATING_HASH)
                            if original != LATEST_TERMINATING_HASH:
                                terminating_hashes = populate_terminating_hashes(LATEST_TERMINATING_HASH, 100)
                                layout["hash"].update(Text(
                                    f"Terminating Hash List: [{terminating_hashes[0]} ... {terminating_hashes[len(terminating_hashes) - 1]}]",
                                    style="bold magenta"))
                            start_time_2 = time.time()

            layout["progress"].update(generate_thread_table(thread_progress))

    console.save_html("output_all.html")
