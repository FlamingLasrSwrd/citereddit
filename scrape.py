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
import logging
import pprint
from datetime import date

# Filenames
URL_OUT = 'urls.txt'
BIB_OUT = 'library.bib'
RAW_OUT = 'raw.txt'

translator_endpoint = 'http://127.0.0.1:1969/'
# TODO: Exception for translator_endpoint unavailable: or start server automatically?
# TODO: move argparse to external source
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

# TODO: move logging to external source
#logging.basicConfig(level=logging.INFO)
logging.basicConfig(level=logging.DEBUG)
#logging.basicConfig(filename='log.log', filemode='w', level=logging.DEBUG)

# Could raise OAuth exception: handle?
reddit = praw.Reddit(user_agent='python/requests:citereddit:1.0 (by /u/brainenhance)',
                    client_id=args.id,
                    client_secret=args.secret,
                    username=args.username,
                    password=args.password,
                    skip_existing=True)
if args.username:
    logging.info(f'Reddit API authenticated as {reddit.user.me()}')
else:
    logging.info(f'Reddit API authenticated anonymously.')
# Cause regex makes everything better
# Another option would be to convert submissions to html and
# use html_parser (BS4?) to locate <a> tags
# Zotero translators have good regexing, so this doesn't have to be perfect
p1 = """\b((?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))"""
p2 = """\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))"""
p3 = r"""^((http[s]?|ftp):\/)?\/?([^:\/\s]+)((\/\w+)*\/)([\w\-\.]+[^#?\s]+)(.*)?(#[\w\-]+)?$"""
p4 = r"""\bhttp[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\,]|(?:%[0-9a-fA-F][0-9a-fA-F]))+\b"""
p = re.compile(p4)

submission_count = 0
url_count = 0
bib_count = 0
sess = str(random.randint(10000,99999))
with open(URL_OUT, 'w') as url_outfile, \
     open(BIB_OUT, 'w') as bib_outfile, \
     open(RAW_OUT, 'w') as raw_outfile:
# TODO: Open files as needed?
# TODO: Add duplicate bib checker via https://github.com/perrette/papers?
# TODO: Feature: pdf file download for free-text items

    for submission in reddit.subreddit(args.subreddit).stream.submissions(limit=None):
        logging.info(f'Scanning {submission.title}')
        submission_count += 1
        if submission_count % 10 == 0:
            logging.info(f'Processed so far: Submissions-{submission_count}; Urls- {url_count}; Bib records- {bib_count}')
            logging.debug(f'Authentication limits: {reddit.auth.limits}')

        text = submission.selftext
        submission.comments.replace_more(limit=None)
        for com in submission.comments.list():
            text += '\n' + com.body
        logging.debug(f'Submission Full Text: \n{text}')
        for u in re.finditer(p, text):
            # skip common links
# TODO: this could skip legitimate links with 'amazon' in the title: regex for domains only?
            common = ['amazon','wikipedia','ebay', 'google', 'reddit']
            if any([c in u.group() for c in common]): # any can be slow: TODO?
                logging.info(f'Found common url... skipping.')
                continue
            # URL is valid and probably a valid reference
            logging.info(f'Found url: {u.group()}')
            url_count += 1
            # Add to url file for possible later duplicate checking
            url_outfile.write(u.group()+'\n')
            # Translate url to Zotero API format
            j = json.dumps({'url': u.group(), 'sessionid': sess})
            h = {'Content-Type': 'application/json'}
            r = requests.post(url=translator_endpoint+'web',
                              headers=h,
                              data=j)
            # Skip the current url if Zotero doesn't find a match
            if r.status_code is not 200:
                logging.info(f'Web Translator Error: {r.text.strip()}')
                continue
# TODO: translation server doesn't always seem to work; build docker from src
            # r.text is now the bib info located by the translator in
            # Zotero API JSON format
            #logging.debug(f'Web Translator Full Response: \n{r.text}')
            # manipulate web translator responses
            zot_bib = json.loads(r.text) # a json list of size 0
            logging.debug(f'Web Translator Bib Item: \n{pprint.pformat(zot_bib)}')
            # skip some unreliable items
            if zot_bib[0]['itemType'] in ['encyclopediaArticle',
                                          'blogPost',
                                          'webpage']:
                logging.info('Unreliable source found... skipping.')
                continue
            if zot_bib[0]['creators'] is []:
                logging.info('No author found... skipping.')
                continue
            # accessDate on translation server doesn't seem to be working
#            if zot_bib[0]['accessDate'] is 'CURRENT_TIMESTAMP':
            zot_bib[0]['accessDate'] = date.today().isoformat()
            # convert back to json
            zot_bib_j = json.dumps(zot_bib)
            # sometimes authors' names are not utf-8
# TODO: could raise conversion error
            data = zot_bib_j.encode(encoding='utf-8')
            r = requests.post(url=translator_endpoint+'export',
                              headers=h,
                              data=data,
                              params={'format': 'bibtex'})
            if r.status_code is not 200:
                logging.info(f'Export Translator Error: {r.text.strip()}')
                break
            bib_outfile.write(r.text+'\n')
            bib_count += 1
# TODO: log item identifier with success statement
            logging.info('Item successfully added to library.')
