# jay-bit-hash
## Overview
jay-bit-hash is a terminal based, Python application attempting to crack future results in an online casino game called Bustabit. The terminal application uses the Rich Python library for neatly formatted output in the terminal, such that the user can get relevant information about the hash cracking process. Keep in mind, this is multithreaded application and will consume a significant portion of your computers resources. This application is not meant to be used while you're doing anything CPU intensive.  

![Terminal](https://github.com/Jay-ArBrouillard/jay-bit-hash/blob/master/terminal.PNG?raw=true)

## Terminology
Latest Terminating Hash - is a SHA256 hash pulled from Bustabit.com. This application will periodically update this value.  
Maximum Hashes Executed Per Thread - is the amount of hashes to look into the future. This is set to 2880 hashes which is estimated to be about 1 days worth of hashes ahead. The higher this value is set to the less hashes per minute will be tested per hour. Currently, this value is not changable by the user.  
Winning Hash - if this value is not N/A, then you won. You can use this hash to find the result of all games that came before it. See the open-source [verification tool](https://jsfiddle.net/Dexon95/2fmuxLza/show).  
Threads (Section) - shows the hash each thread is currently checking. There will a line per thread available on your CPU.

## Compatibility
Works with Linux, OSX, and Windows. Requires Python 3.6.3 or later.

## Requirements
Install the required Python packages. I'd suggest creating an virtual environment, activating the environment, and then installing dependencies there instead of installing the dependencies globally.

```sh
# Optionally create and activate virtual environment
virtualenv venv
source venv/bin/activate ## This is the linux syntax. For windows it look something like: venv\Scripts\activate

pip install -r requirements.txt
```

## Run it
Run the main python file.
```sh
py main.py
```

## Donations
If you win the jackpot with this code, feel free to donate as a token of appreciation :)  
BTC: `17mXG71RKDGN14YFtAb1mM2cUPctvvuFsp`
