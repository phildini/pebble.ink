#!/bin/bash

cd /home/phildini/pebble.ink/twittering_machine/
rm tweets.json
virtualenv .
. bin/activate
pip install -r requirements.txt
python fetch_links.py
cp styles.css $TWEET_HTML_PATH