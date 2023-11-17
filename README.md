# jay-bit-hash
## Overview
jay-bit-hash is a terminal based, Python application attempting to crack future results in online casino game(s) (bustabit and ethercrash currently). The terminal application uses the Rich Python library for neatly formatted output in the terminal, such that the user can get relevant information about the hash cracking process. Keep in mind, this is a multithreaded application and will consume a significant portion of your computers resources. This application is not meant to be used while you're doing anything CPU intensive.  

Please keep in mind that running this application in no way is a guarantee of winning. In fact, the chance of finding a winning hash is equal to: 2^256 / the number of games left in the chain (< 2 million for bustabit). I would like to think of it as more of a proof of concept with the possibility of winning the jackpot. This is your warning not to fry your computer running this application.  

![terminal.gif](https://github.com/Jay-ArBrouillard/jay-bit-hash/blob/master/blur.gif)
![terminal.PNG](https://github.com/Jay-ArBrouillard/jay-bit-hash/blob/master/terminal.PNG)
![terminal.gif](https://github.com/Jay-ArBrouillard/jay-bit-hash/blob/master/terminal.gif)

## Terminology
Hashes (H) - The number of hashes checked by this program. Keep in mind this is not guaranteed to be unique hashes, in fact the hashes that are checked are randomly generated, as it is computationally infeasible to sequentially check every possible permutation of a 256 bit hash.
H/Min - The number of hashes (H) / total number of minutes that have passed since the program started
H/Hour - The number of hashes (H) / total number of hours that have passed since the program started
Elapsed Time - Amount of time that has passed since the program started. Displayed in format days:hours:minutes:seconds:milliseconds
Hashes per Thread - The number of time a each thread will hash against this self. This number will decrease as games are completed.
Latest Terminating Hash - For a given casino (i.e bustabit), the latest SHA256 hash that was pulled. This application will periodically update this value.  
Winning Hash - if this value is not N/A, then you won. You can use this hash to find the result of all games that came before it. See the open-source [verification tool](https://jsfiddle.net/Dexon95/2fmuxLza/show).  
Threads (Section) - shows the randomly generated hash each thread is currently checking. There will be a thread per CPU Core available on your system. Thus, more threads and/or more powerful CPU cores will result in more hashes per hour checked.  

## Share Your Results!
I'm interested to know what kind of speeds your systems achieving in terms of hashes per hour.  
With my Intel(R) Core(TM) i7-10700K CPU @ 3.80GHz I am able to get around 257 H/Hour at 3.3 million Hashes per Thread.

## Compatibility
Works with Linux, OSX, and Windows. Requires Python 3.7 or later.

## Requirements
Install the required Python packages. I'd suggest creating an virtual environment, activating the environment, and then installing dependencies there instead of installing the dependencies globally.

```sh
# Optionally create and activate virtual environment
virtualenv venv ## You can force the Python version i.e: virtualenv -p python3.9 venv
source venv/bin/activate ## This is the linux syntax. For windows it look something like: venv\Scripts\activate

pip install -r requirements.txt
```
## Known Errors
ValueError: There is no such driver by url
https://chromedriver.storage.googleapis.com/LATEST_RELEASE_119.0.6045

Fixed using: python3 -m pip install webdriver-manager --upgrade


## Run it
Run the top level python file.
```sh
py run.py
```

## Donations
If you win the jackpot with this code, feel free to donate as a token of appreciation :)  
BTC: `17mXG71RKDGN14YFtAb1mM2cUPctvvuFsp`
