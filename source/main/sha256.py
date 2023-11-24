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
from rich.progress import track, Progress, MofNCompleteColumn
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
latest_terminating_hashes = ['', '', '14a5c73b736ed13cabdeeb9bea454a2502c204e3d19e87d9a5955d23ba3daf1e']
latest_game_number = [1, 1, 5843793]
latest_game_multiplier = ['', '', '4.44']
sha_iterations_per_hash = 86400


def make_layout() -> Layout:
    """Define the layout."""
    layout = Layout(name="root")

    layout.split(
        Layout(name="header", size=3),
        Layout(name="stats", size=5),
        Layout(name="section1", size=5),
        Layout(name="section2", size=5),
        Layout(name="section3", size=5),
        Layout(name="threads")
    )
    return layout


def generate_stats_panel(num_hashes) -> Panel:
    elapsed = time.time() - start_time

    stats_table = Table(
        Column(header="Hashes (H)", justify="center"),
        Column(header="H/Min", justify="center"),
        Column(header="H/Hour", justify="center"),
        Column(header="Elapsed Time", justify="center"),
        Column(header="Hashes per Thread", justify="center"),
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
        str(sha_iterations_per_hash)
    )

    stats_panel = Panel(
        stats_table,
        box=box.ROUNDED,
        title="Stats",
        border_style="white"
    )

    return stats_panel


def generate_bustabit_panel(winning_hash=None) -> Panel:
    style_column2 = "bold green" if winning_hash else ""
    bustabit_table = Table.grid(expand=True)
    bustabit_table.add_column(justify="left")
    bustabit_table.add_column(justify="center", no_wrap=True, style=style_column2)
    bustabit_table.add_row(f"Latest Terminating Hash (Game #{latest_game_number[0]} @ {latest_game_multiplier[0]})", latest_terminating_hashes[0])
    bustabit_table.add_row("Winning Hash", winning_hash if winning_hash else "N/A")

    bustabit_panel = Panel(
        bustabit_table,
        box=box.ROUNDED,
        title="bustabit",
        border_style="#e58929"
    )

    return bustabit_panel


def generate_ethercrash_panel(winning_hash=None) -> Panel:
    style_column2 = "bold green" if winning_hash else ""
    ethercrash_table = Table.grid(expand=True)
    ethercrash_table.add_column(justify="left")
    ethercrash_table.add_column(justify="center", no_wrap=True, style=style_column2)
    ethercrash_table.add_row(f"Latest Terminating Hash (Game #{latest_game_number[1]} @ {latest_game_multiplier[1]})", latest_terminating_hashes[1])
    ethercrash_table.add_row("Winning Hash", winning_hash if winning_hash else "N/A")

    ethercrash_panel = Panel(
        ethercrash_table,
        box=box.ROUNDED,
        title="ethercrash",
        border_style="#5A6EBF"
    )
    return ethercrash_panel


def generate_nanogames_panel(winning_hash=None) -> Panel:
    style_column2 = "bold green" if winning_hash else ""
    nanogames_table = Table.grid(expand=True)
    nanogames_table.add_column(justify="left")
    nanogames_table.add_column(justify="center", no_wrap=True, style=style_column2)
    nanogames_table.add_row(f"Latest Terminating Hash (Game #{latest_game_number[2]} @ {latest_game_multiplier[2]})", latest_terminating_hashes[2])
    nanogames_table.add_row("Winning Hash", winning_hash if winning_hash else "N/A")

    nanogames_panel = Panel(
        nanogames_table,
        box=box.ROUNDED,
        title="nanogames",
        border_style="#31343c"
    )

    return nanogames_panel


def generate_threads_panel(processes: [Process], progress_objects: [Progress]) -> Panel:
    threads_table = Table(
        Column(header="Thread #", justify="center"),
        Column(header="Process Id", justify="center"),
        Column(header="State", justify="center"),
        Column(header="Progress", justify="center"),
        box=None,
        expand=True,
        header_style="underline",
        show_footer=False,
    )

    for idx, proc in enumerate(processes):
        try:
            p = psutil.Process(proc.pid)
            state = p.status()
            threads_table.add_row(str(idx), str(proc.pid), state, progress_objects[idx])
        except psutil.NoSuchProcess:
            threads_table.add_row(str(idx), "-", "-", "not_alive", progress_objects[idx])

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
            selenium_options.add_argument('--no-sandbox')
            selenium_options.add_argument('--disable-dev-shm-usage')
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=selenium_options)
            driver.get('https://bustabit.com/play')

            waiter = WebDriverWait(driver, 20)
            history_tab = waiter.until(
                expected_conditions.visibility_of_element_located((
                    By.XPATH, "//*[@id=\"root\"]/div[1]/div/div[5]/div/div[1]/ul/li[2]")
                )
            )
            history_tab.click()

            first_row_fifth_col = waiter.until(
                expected_conditions.visibility_of_element_located((
                    By.XPATH, "//*[@id=\"root\"]/div[1]/div/div[5]/div/div[2]/div/table/tbody/tr[1]/td[5]/input")))
            latest_hash_from_site = first_row_fifth_col.get_attribute('value')

            bust_anchor = waiter.until(
                expected_conditions.visibility_of_element_located((
                    By.XPATH, "//*[@id=\"root\"]/div[1]/div/div[5]/div/div[2]/div/table/tbody/tr[1]/td[1]/a"
                ))
            )
            bust_multiplier = bust_anchor.text
            bust_anchor.click()

            game_number_h3 = waiter.until(
                expected_conditions.visibility_of_element_located((
                    By.XPATH, "/html/body/div[3]/div/div/div[2]/div/div[1]/div[1]/h3"
                ))
            )
            game_number = game_number_h3.text.split("#")[1]

            if latest_hash_from_site is not None and len(latest_hash_from_site) == 64 and \
                    game_number is not None and str(game_number).isnumeric():
                console.print("Successfully found hash and game number from bustabit.com", style='success')
                return latest_hash_from_site, game_number, bust_multiplier
            else:
                raise Exception("Failed to find hash and game number from bustabit.com")
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
            selenium_options.add_argument('--no-sandbox')
            selenium_options.add_argument('--disable-dev-shm-usage')
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

            crash_anchor = waiter.until(
                expected_conditions.visibility_of_element_located((
                    By.XPATH, "//*[@id=\"games-log-container\"]/div[2]/table/tbody/tr[1]/td[1]/a"
                ))
            )
            crash_multiplier = crash_anchor.text
            crash_anchor.click() # this opens a new tab

            driver.switch_to.window(driver.window_handles[1])

            game_number_h4 = waiter.until(
                expected_conditions.visibility_of_element_located((
                    By.XPATH, "/html/body/div[1]/div/h4"
                ))
            )
            game_number = game_number_h4.text.split(" ")[1]

            if latest_hash_from_site is not None and len(latest_hash_from_site) == 64 and \
                    game_number is not None and str(game_number).isnumeric():
                console.print("Successfully found hash and game number from ethercrash.io", style='success')
                return latest_hash_from_site, game_number, crash_multiplier
            else:
                raise Exception("Failed to find hash and game number from ethercrash.io")
        except Exception as e:
            if i < tries - 1:  # i is zero indexed
                continue
            else:
                raise


def get_latest_hash_from_nanogames(tries=3) -> string:
    """Attempt to find the latest hash from nanogames.io.
       Be careful not to run this too often as to prevent ip block.
    """
    for i in range(tries):
        try:
            selenium_options = Options()
            selenium_options.headless = True
            selenium_options.add_argument('--no-sandbox')
            selenium_options.add_argument('--disable-dev-shm-usage')
            selenium_options.add_argument("--disable-blink-features=AutomationControlled")
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=selenium_options)
            driver.get('https://nanogames.io/crash')

            waiter = WebDriverWait(driver, 20)
            # redirect back to /crash
            time.sleep(2)
            if driver.current_url.endswith("/spin"):
                driver.get('https://nanogames.io/crash')

            history_tab = waiter.until(
                expected_conditions.visibility_of_element_located((
                    By.XPATH, "//button[text()='History']")))
            history_tab.click()
            driver.execute_script("arguments[0].scrollIntoView();", history_tab)

            history_table = waiter.until(
                expected_conditions.visibility_of_element_located((
                    By.XPATH, "//*[@id=\"game-crash\"]/div[3]/div[2]/div/div[2]/table")))
            first_row_columns = history_table.find_element(By.CSS_SELECTOR, "tbody > tr:first-child").find_elements(By.TAG_NAME, "td")

            latest_hash_from_site = first_row_columns[2].find_element(By.TAG_NAME, "input").get_attribute('value')
            bang_multiplier = first_row_columns[1].text
            game_number = first_row_columns[0].text

            if latest_hash_from_site is not None and len(latest_hash_from_site) == 64 and \
                    game_number is not None and str(game_number).isnumeric():
                console.print("Successfully found hash and game number from nanogames.io", style='success')
                return latest_hash_from_site, game_number, bang_multiplier
            else:
                raise Exception("Failed to find hash and game number from nanogames.io")
        except Exception as e:
            if i < tries - 1:  # i is zero indexed
                continue
            else:
                raise


def get_latest_hashes_from_all_sites(list) -> None:
    """
        Find new latest hashes and game numbers from each website and return list
        [hash1, gamenumber1, bust, hash2, gamenumber2, crash, hash3, gamenumber3, etc...]
    """
    # bustabit
    original = latest_terminating_hashes[0]
    bustabit_hash, bustabit_game_number, bust = get_latest_hash_from_bustabit(5)
    if original != bustabit_hash:
        list[0] = bustabit_hash
        list[1] = bustabit_game_number
        list[2] = bust

    # ethercrash
    original = latest_terminating_hashes[1]
    ethercrash_hash, ethercrash_game_number, crash = get_latest_hash_from_ethercrash(5)
    if original != ethercrash_hash:
        list[3] = ethercrash_hash
        list[4] = ethercrash_game_number
        list[5] = crash

    # nanogmaes
    original = latest_terminating_hashes[2]
    nanogames_hash, nanogames_game_number, bang = get_latest_hash_from_nanogames(5)
    if original != nanogames_hash:
        list[6] = nanogames_hash
        list[7] = nanogames_game_number
        list[8] = bang


def update_sha_iterations_per_hash():
    global sha_iterations_per_hash
    bustabit_games_left = 10000000 - int(latest_game_number[0])
    ethercrash_games_left = 10000000 - int(latest_game_number[1])
    nanogames_games_left = 10000000 - int(latest_game_number[2])
    sha_iterations_per_hash = min([bustabit_games_left, ethercrash_games_left, nanogames_games_left])


def execute():
    global start_time_2
    processes = []
    # index 0 is bustabit, index 1 is ethercrash, index 2 is nanogames
    bustabit_hash, bustabit_game_number, bust = get_latest_hash_from_bustabit(5)
    latest_terminating_hashes[0] = bustabit_hash
    latest_game_number[0] = bustabit_game_number
    latest_game_multiplier[0] = bust
    ethercrash_hash, ethercrash_game_number, crash = get_latest_hash_from_ethercrash(5)
    latest_terminating_hashes[1] = ethercrash_hash
    latest_game_number[1] = ethercrash_game_number
    latest_game_multiplier[1] = crash
    # nanogames_hash, nanogames_game_number, bang = get_latest_hash_from_nanogames(5)
    # latest_terminating_hashes[2] = nanogames_hash
    # latest_game_number[2] = nanogames_game_number
    # latest_game_multiplier[2] = bang
    update_sha_iterations_per_hash()

    console.log("latest_terminating_hashes: %s" % latest_terminating_hashes)

    cpu_count = os.cpu_count()
    shared_array = multiprocessing.Array('i', cpu_count * shared_array_chunk_size)
    # Progress object is the status bar for each thread
    progress_objects: [Progress] = []

    for i in track(range(cpu_count), description="Register and Start Processes..."):
        random_hash = ''.join(random.SystemRandom().choice('abcdef' + string.digits) for _ in range(64))
        progress_object = Progress(
            *Progress.get_default_columns(),
            MofNCompleteColumn()
        )
        progress_object.add_task(description=random_hash, total=sha_iterations_per_hash)
        progress_objects.append(progress_object)
        processes.append(Process(target=calculate_hash,
                                 args=(
                                     latest_terminating_hashes, sha_iterations_per_hash, random_hash, i, shared_array)))
        processes[i].start()

    grid = Table.grid(expand=True)
    grid.add_column(justify="center", ratio=1)
    grid.add_column(justify="right")
    grid.add_row(
        "[b]Jay-Ar's[/b] sha256 Hash Cracker Terminal Application",
        "Start Date: " + datetime.now().ctime(),
    )

    layout = make_layout()
    layout["header"].update(Panel(grid, style="white"))
    layout["stats"].update(generate_stats_panel("0"))
    layout["section1"].update(generate_bustabit_panel())
    layout["section2"].update(generate_ethercrash_panel())
    layout["section3"].update(generate_nanogames_panel())
    layout["threads"].update(generate_threads_panel(processes, progress_objects))
    hashes_checked = 0
    continue_loop = True
    return_list = ['', '', '', '', '', '', '', '', '']
    webdriver_thread = threading.Thread(target=get_latest_hashes_from_all_sites, args=[return_list])
    webdriver_thread_started = False
    winner_found = False
    iterations_list = [0.0] * len(processes)  # Store the last retrieve iteration for each process
    with Live(layout, refresh_per_second=4, screen=True):
        while continue_loop:
            for process_idx, process in enumerate(processes):
                progress = progress_objects[process_idx]
                task = progress.tasks[0]
                # Thread completed
                if shared_array[shared_array_chunk_size * process_idx + 2] == 1:
                    shared_array[shared_array_chunk_size * process_idx] = 0  # reset iteration to 0
                    shared_array[shared_array_chunk_size * process_idx + 2] = 0  # reset completed to false
                    if shared_array[shared_array_chunk_size * process_idx + 1] == 1:  # winner
                        winner_index = shared_array[shared_array_chunk_size * process_idx + 3]
                        winning_hash = task.description
                        console.log(f"WINNER, WINNER CHICKEN DINNER: {winning_hash}")
                        winner_found = True
                        # bustabit
                        if winner_index == 0:
                            layout["section1"].update(generate_bustabit_panel(winning_hash))
                        # ethercrash
                        elif winner_index == 1:
                            layout["section2"].update(generate_ethercrash_panel(winning_hash))
                        # nanogames
                        elif winner_index == 2:
                            layout["section3"].update(generate_nanogames_panel(winning_hash))
                        console.save_html("output_winner.html")
                        # Kill all Processes
                        for p in processes:
                            p.kill()
                        # Complete all Tasks
                        for p in progress_objects:
                            p.update(p.tasks[0].id, completed=True)
                    elif not winner_found:  # loser
                        # If a winner has not been found then,
                        # Start up a new process with a new random hash
                        random_hash = ''.join(random.SystemRandom().choice('abcdef' + string.digits) for _ in range(64))

                        process.terminate()  # ensure current process is terminated
                        processes[process_idx] = Process(target=calculate_hash,
                                                         args=(latest_terminating_hashes,
                                                               sha_iterations_per_hash,
                                                               random_hash,
                                                               process_idx, shared_array))
                        processes[process_idx].start()
                        progress.reset(task_id=task.id, description=random_hash, total=sha_iterations_per_hash)

                    iterations_list[process_idx] = 0.0
                    hashes_checked += 1
                    layout["threads"].update(generate_threads_panel(processes, progress_objects))
                else:
                    # update Progress
                    shared_array[shared_array_chunk_size * process_idx + 2] == 1
                    new_iteration = shared_array[shared_array_chunk_size * process_idx]
                    delta: float = new_iteration - iterations_list[process_idx]
                    # since the processes are concurrent we check if processes is done a second time before advancing
                    # the progress bar
                    if task.completed + delta >= task.total:
                        random_hash = ''.join(random.SystemRandom().choice('abcdef' + string.digits) for _ in range(64))
                        progress.reset(task_id=task.id, description=random_hash, total=sha_iterations_per_hash)
                        iterations_list[process_idx] = 0.0
                    else:
                        progress.update(task_id=task.id, advance=delta)
                        iterations_list[process_idx] = new_iteration

                layout["stats"].update(generate_stats_panel(str(hashes_checked)))

            update_sha_iterations_per_hash()

            # Grab the latest terminating hash from each website every x minutes
            elapsed_seconds = time.time() - start_time_2
            if elapsed_seconds / 60 >= 2.5:
                if not winner_found and not webdriver_thread_started and not webdriver_thread.is_alive():
                    webdriver_thread.start()
                    webdriver_thread_started = True

                start_time_2 = time.time()

            # webdriver thread completed
            if webdriver_thread_started and not webdriver_thread.is_alive():
                latest_terminating_hashes[0] = return_list[0]
                latest_game_number[0] = return_list[1]
                latest_game_multiplier[0] = return_list[2]
                latest_terminating_hashes[1] = return_list[3]
                latest_game_number[1] = return_list[4]
                latest_game_multiplier[1] = return_list[5]
                latest_terminating_hashes[2] = return_list[6]
                latest_game_number[2] = return_list[7]
                latest_game_multiplier[2] = return_list[8]
                webdriver_thread = threading.Thread(target=get_latest_hashes_from_all_sites,
                                                    args=[return_list])
                update_sha_iterations_per_hash()
                layout["section1"].update(generate_bustabit_panel())
                layout["section2"].update(generate_ethercrash_panel())
                layout["section3"].update(generate_nanogames_panel())
                webdriver_thread_started = False


if __name__ == '__main__':
    execute()
