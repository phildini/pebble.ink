#!/bin/bash

rm tweets.json
. bin/activate
pip install -r requirements.txt
python fetch_links.py
cp index.html $TWEET_HTML_PATH