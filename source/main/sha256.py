import hashlib
import multiprocessing.managers
import os
import random
import string
import time
import threading
import psutil
from datetime import datetime
from multiprocessing import Process

from rich import box
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.progress import track
from rich.table import Column, Table
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
from source.main.functions import calculate_hash

console = Console(record=True, theme=Theme({'success': 'green', 'error': 'bold red', 'init': 'yellow'}))
start_time = time.time()
start_time_2 = time.time()
shared_array_chunk_size = 4
latest_terminating_hashes = ['', '']


def make_layout() -> Layout:
    """Define the layout."""
    layout = Layout(name="root")

    layout.split(
        Layout(name="header", size=3),
        Layout(name="stats", size=5),
        Layout(name="section1", size=5),
        Layout(name="section2", size=5),
        Layout(name="threads")
    )
    return layout


def generate_stats_panel(num_hashes) -> Panel:
    global start_time
    elapsed = time.time() - start_time

    stats_table = Table(
        Column(header="Hashes (H)", justify="center"),
        Column(header="H/Min", justify="center"),
        Column(header="H/Hour", justify="center"),
        Column(header="Elapsed Time", justify="center"),
        box=None,
        expand=True,
        header_style="underline",
        show_footer=False,
    )

    total_minutes = elapsed / 60.0
    days = elapsed / 86400
    elapsed %= 86400
    hours = elapsed / 3600
    elapsed %= 3600
    minutes = elapsed / 60
    elapsed %= 60
    hashes_per_minute = float(num_hashes) / float(total_minutes)
    hashes_per_hour = hashes_per_minute * 60

    stats_table.add_row(
        num_hashes,
        str(round(hashes_per_minute, 2)),
        str(round(hashes_per_hour, 2)),
        "{:0>2}:{:0>2}:{:0>2}:{:05.2f}".format(int(days), int(hours), int(minutes), elapsed),
    )

    stats_panel = Panel(
        stats_table,
        box=box.ROUNDED,
        title="Stats",
        border_style="white"
    )

    return stats_panel


def generate_bustabit_panel(winning_hash=None) -> Panel:
    current_hash = latest_terminating_hashes[0]
    style_column2 = "bold green" if winning_hash else ""
    bustabit_table = Table.grid(expand=True)
    bustabit_table.add_column(justify="left")
    bustabit_table.add_column(justify="center", no_wrap=True, style=style_column2)
    bustabit_table.add_row("Latest Terminating Hash", current_hash)
    bustabit_table.add_row("Winning Hash", winning_hash if winning_hash else "N/A")

    bustabit_panel = Panel(
        bustabit_table,
        box=box.ROUNDED,
        title="bustabit",
        border_style="#e58929"
    )

    return bustabit_panel


def generate_ethercrash_panel(winning_hash=None) -> Panel:
    current_hash = latest_terminating_hashes[1]
    style_column2 = "bold green" if winning_hash else ""
    ethercrash_table = Table.grid(expand=True)
    ethercrash_table.add_column(justify="left")
    ethercrash_table.add_column(justify="center", no_wrap=True, style=style_column2)
    ethercrash_table.add_row("Latest Terminating Hash", current_hash)
    ethercrash_table.add_row("Winning Hash", winning_hash if winning_hash else "N/A")

    ethercrash_panel = Panel(
        ethercrash_table,
        box=box.ROUNDED,
        title="ethercrash",
        border_style="#5A6EBF"
    )

    return ethercrash_panel


def generate_threads_panel(processes: [Process], hashes: [string]) -> Panel:
    threads_table = Table(
        Column(header="Thread #", justify="center"),
        Column(header="Process Id", justify="center"),
        Column(header="Memory (MiB)", justify="center"),
        Column(header="State", justify="center"),
        Column(header="Hash", justify="center"),
        box=None,
        expand=True,
        header_style="underline",
        show_footer=False,
    )

    for idx, proc in enumerate(processes):
        try:
            p = psutil.Process(proc.pid)
            memory_usage = p.memory_info().rss / 1024 ** 2
            state = p.status()
            threads_table.add_row(str(idx), str(proc.pid), "{0:.2f}".format(memory_usage), state, hashes[idx])
        except psutil.NoSuchProcess:
            threads_table.add_row(str(idx), "-", "-", "not_alive", hashes[idx])

    threads_panel = Panel(
        threads_table,
        title="threads",
        border_style="red",
        padding=(1, 2),
    )

    return threads_panel


def get_latest_hash_from_bustabit(tries=3) -> string:
    """Attempt to find the latest hash from bustabit.com.
       Be careful not to run this too often as to prevent ip block.
    """
    for i in range(tries):
        try:
            selenium_options = Options()
            selenium_options.headless = True
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=selenium_options)
            driver.get('https://bustabit.com/play')

            waiter = WebDriverWait(driver, 20)
            history_tab = waiter.until(
                expected_conditions.visibility_of_element_located((
                    By.XPATH, "//*[@id=\"root\"]/div[1]/div/div[5]/div/div[1]/ul/li[2]")))
            history_tab.click()

            first_row_fifth_col = waiter.until(
                expected_conditions.visibility_of_element_located((
                    By.XPATH, "//*[@id=\"root\"]/div[1]/div/div[5]/div/div[2]/div/table/tbody/tr[1]/td[5]/input")))
            latest_hash_from_site = first_row_fifth_col.get_attribute('value')

            if latest_hash_from_site is not None and len(latest_hash_from_site) == 64:
                console.print("Successfully found hash from bustabit.com", style='success')
                return latest_hash_from_site
            else:
                raise Exception("Failed to find hash from bustabit.com")
        except Exception as e:
            if i < tries - 1:  # i is zero indexed
                continue
            else:
                raise


def get_latest_hash_from_ethercrash(tries=3) -> string:
    """Attempt to find the latest hash from ethercrash.io.
       Be careful not to run this too often as to prevent ip block.
    """
    for i in range(tries):
        try:
            selenium_options = Options()
            selenium_options.headless = True
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=selenium_options)
            driver.get('https://www.ethercrash.io/play')

            waiter = WebDriverWait(driver, 20)
            history_tab = waiter.until(
                expected_conditions.visibility_of_element_located((
                    By.XPATH, "//*[@id=\"tabs-inner-container\"]/div[1]/ul/li[1]")))
            history_tab.click()

            first_row_fifth_col = waiter.until(
                expected_conditions.visibility_of_element_located((
                    By.XPATH, "//*[@id=\"games-log-container\"]/div[2]/table/tbody/tr[1]/td[5]/input")))
            latest_hash_from_site = first_row_fifth_col.get_attribute('value')

            if latest_hash_from_site is not None and len(latest_hash_from_site) == 64:
                console.print("Successfully found hash from ethercrash.io", style='success')
                return latest_hash_from_site
            else:
                raise Exception("Failed to find hash from ethercrash.io")
        except Exception as e:
            if i < tries - 1:  # i is zero indexed
                continue
            else:
                raise


def get_latest_hashes_from_all_sites(list) -> None:
    """
        Find new latest hashes from each website and return tuple
    """
    # bustabit
    original = latest_terminating_hashes[0]
    new_bustabit_terminating_hash = get_latest_hash_from_bustabit()
    if original != new_bustabit_terminating_hash:
        list[0] = new_bustabit_terminating_hash

    # ethercrash
    original = latest_terminating_hashes[1]
    new_ethercrash_terminating_hash = get_latest_hash_from_ethercrash()
    if original != new_ethercrash_terminating_hash:
        list[1] = new_ethercrash_terminating_hash


def temp(LATEST_TERMINATING_HASH, MAX_ITERATIONS):
    m = hashlib.sha256()
    # m.update(str.encode(random_hash))
    m.update(str.encode(LATEST_TERMINATING_HASH))
    hex_digest = m.hexdigest()

    for _ in range(MAX_ITERATIONS + 1):
        m = hashlib.sha256()
        m.update(str.encode(hex_digest))
        hex_digest = m.hexdigest()
        if hex_digest == "f9f628b794c374558d6923fee19b71ed43e924414a5e4eced3a780fe12970495":
            stop = "s"
            print("success")
            break


def execute():
    global start_time_2
    # MAX_ITERATIONS = 2880  # About 1 day ahead based on about 30 seconds per game
    MAX_ITERATIONS = 20160  # About 7 days ahead based on about 30 seconds per game
    processes = []
    # index 0 is bustabit, index 1 is ethercrash
    latest_terminating_hashes[0] = get_latest_hash_from_bustabit(5)
    latest_terminating_hashes[1] = get_latest_hash_from_ethercrash(5)

    console.log("latest_terminating_hashes: %s" % latest_terminating_hashes)
    # temp(LATEST_TERMINATING_HASH, MAX_ITERATIONS)

    cpu_count = os.cpu_count()
    shared_array = multiprocessing.Array('i', cpu_count * shared_array_chunk_size)
    hashes = []  # The 64 character hash list. One hash given to each process. These are randomly generated

    for i in track(range(cpu_count), description="Register and Start Processes..."):
        random_hash = ''.join(random.SystemRandom().choice('abcdef' + string.digits) for _ in range(64))
        hashes.append(random_hash)
        processes.append(Process(target=calculate_hash,
                                 args=(latest_terminating_hashes, MAX_ITERATIONS, random_hash, i, shared_array)))
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
    layout["stats"].update(generate_stats_panel("0"))
    layout["section1"].update(generate_bustabit_panel())
    layout["section2"].update(generate_ethercrash_panel())
    layout["threads"].update(generate_threads_panel(processes, hashes))
    hashes_checked = 0
    continue_loop = True
    return_list = ['', '']
    webdriver_thread = threading.Thread(target=get_latest_hashes_from_all_sites, args=[return_list])
    webdriver_thread_started = False
    winner_found = False
    with Live(layout, refresh_per_second=4, screen=True):
        while continue_loop:
            for process_idx, process in enumerate(processes):
                # Thread completed
                if shared_array[shared_array_chunk_size * process_idx + 2] == 1:
                    shared_array[shared_array_chunk_size * process_idx] = 0  # reset iteration to 0
                    shared_array[shared_array_chunk_size * process_idx + 2] = 0  # reset completed to false
                    if shared_array[shared_array_chunk_size * process_idx + 1] == 1:  # winner
                        winner_index = shared_array[shared_array_chunk_size * process_idx + 3]
                        winning_hash = hashes[winner_index]
                        console.log(f"WINNER, WINNER CHICKEN DINNER: {winning_hash}")
                        winner_found = True
                        # bustabit
                        if winner_index == 0:
                            layout["section1"].update(generate_bustabit_panel(winning_hash))
                        # ethercrash
                        elif winner_index == 1:
                            layout["section2"].update(generate_ethercrash_panel(winning_hash))
                        console.save_html("output_winner.html")
                        # Kill all Processes
                        for p in processes:
                            p.kill()
                    elif not winner_found:  # loser
                        # If a winner has not been found then,
                        # Start up a new process with a new random hash
                        random_hash = ''.join(random.SystemRandom().choice('abcdef' + string.digits) for _ in range(64))
                        hashes[process_idx] = random_hash

                        process.terminate()  # ensure current process is terminated
                        processes[process_idx] = Process(target=calculate_hash,
                                                         args=(latest_terminating_hashes, MAX_ITERATIONS, random_hash,
                                                               process_idx, shared_array))
                        processes[process_idx].start()

                    hashes_checked += 1
                    layout["threads"].update(generate_threads_panel(processes, hashes))
                layout["stats"].update(generate_stats_panel(str(hashes_checked)))

            # Grab the latest terminating hash from each website every x minutes
            elapsed_seconds = time.time() - start_time_2
            if elapsed_seconds / 60 >= 1:
                if not winner_found and not webdriver_thread_started and not webdriver_thread.is_alive():
                    webdriver_thread.start()
                    webdriver_thread_started = True

                start_time_2 = time.time()

            # webdriver thread completed
            if webdriver_thread_started and not webdriver_thread.is_alive():
                latest_terminating_hashes[0] = return_list[0]
                latest_terminating_hashes[1] = return_list[1]
                webdriver_thread = threading.Thread(target=get_latest_hashes_from_all_sites,
                                                    args=[return_list])
                layout["section1"].update(generate_bustabit_panel())
                layout["section2"].update(generate_ethercrash_panel())
                webdriver_thread_started = False

    console.save_html("output_all.html")


if __name__ == '__main__':
    execute()