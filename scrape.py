"""Reddit citation scraper."""
# Usage:
# python scrape.py -s seeeccrrettt -i iiiidddddd -r Nootropics

import praw
import re
import argparse

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
p = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'

urls = []
for submission in reddit.subreddit(args.subreddit).stream.submissions():
    text = submission.selftext
    for u in re.findall(p, text):
        if u is not []:
            print(u)
#            urls.append(u)

#    submission.comments.replace_more(limit=None)
#    for comment in submission.comments.list():
#        print(comment.date)
#        print(comment.body)
