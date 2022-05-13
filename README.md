# jay-bit-hash
## Overview
jay-bit-hash is a terminal based, Python application attempting to crack future results in an online casino game called Bustabit. The terminal application uses the Rich Python library for neatly formatted output in the terminal, such that the user can get relevant information about the hash cracking process. Keep in mind, this is multithreaded application and will consume a significant portion of your computers resources. This application is not meant to be used while you're doing anything CPU intensive.  

![Terminal](https://github.com/Jay-ArBrouillard/jay-bit-hash/blob/master/terminal.PNG?raw=true)

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
