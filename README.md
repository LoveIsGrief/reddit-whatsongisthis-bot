# reddit-whatsongisthis-bot
A bot that will automatically try to identify songs posted to https://reddit.com/r/WhatSongIsThis

# Requirements

 - Python > 3.5
 - [ffmpeg](https://ffmpeg.org/download.html) (a dependency of youtube-dl)



# Setup

**Ubuntu / Debian**

```bash
sudo apt-get install virtualenv
virtualenv -p python3 env
pip install -r requirements.txt
```

# How to run

```bash
source env/bin/activate # If you're using a virtual env
python src/main.py
```
