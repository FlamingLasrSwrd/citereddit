"""Reddit citation scraper."""
# Requires: reddit API secret and id
# Usage:
# python scrape.py -s seeeccrrettt -i iiiidddddd -r Nootropics

import praw
import re
import argparse
import json
import requests
import random
from pprint import pprint

translator_endpoint = 'http://127.0.0.1:1969/'

parser = argparse.ArgumentParser()
parser.add_argument("-s", "--secret",
                    type=str,
                    help="Reddit API client secret.",
                    default='')
parser.add_argument("-i", "--id",
                    type=str,
                    help="Reddit API client id.",
                    default='')
parser.add_argument("-u", "--username",
                    type=str,
                    help="Optional reddit username.",
                    default='')
parser.add_argument("-p", "--password",
                    type=str,
                    help="Optional reddit password.",
                    default='')
parser.add_argument("-r", "--subreddit",
                    type=str,
                    help="Target subreddit.",
                    default='all')

args = parser.parse_args()

reddit = praw.Reddit(user_agent='Extraction (by /u/BrainEnhance et. al.)',
                    client_id=args.id,
                    client_secret=args.secret,
                    username=args.username,
                    password=args.password)

# Cause regex makes everything better
# From: https://www.w3resource.com/python-exercises/re/python-re-exercise-42.php
p1 = """\b((?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))"""
p2 = """\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))"""
p3 = r"""^((http[s]?|ftp):\/)?\/?([^:\/\s]+)((\/\w+)*\/)([\w\-\.]+[^#?\s]+)(.*)?(#[\w\-]+)?$"""
p4 = r"""\bhttp[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\,]|(?:%[0-9a-fA-F][0-9a-fA-F]))+\b"""
p = re.compile(p4)

sess = str(random.randint(10000,99999))
with open('output.bib', 'w') as outfile:
    for submission in reddit.subreddit(args.subreddit).stream.submissions():
        text = submission.selftext
        submission.comments.replace_more(limit=None)
        for com in submission.comments.list():
            text += com.body
        for u in re.finditer(p, text):
                print(u.group())
                j = json.dumps({'url': u.group(), 'sessionid': sess})
                h = {'Content-Type': 'application/json'}
                # Get zotero API format json doc
                r = requests.post(url=translator_endpoint+'web', headers=h, data=j)
                if r.text.find('No translators available') is not -1:
                    break
                if r.text.find('@misc') is not -1:
                    break #TODO: @misc still doesn't work
                data = r.text.encode(encoding='utf-8')
                r = requests.post(url=translator_endpoint+'export', headers=h, data=data, params={'format': 'bibtex'})
                if r.text.find('Invalid JSON provided') is not -1:
                    break
                outfile.write(r.text)
