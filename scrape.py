"""Reddit citation scraper."""
# Requires: reddit API secret and id
# Usage:
# python scrape.py -s seeeccrrettt -i iiiidddddd -r Nootropics

import praw
import json
import requests
import random
import logging
import logging.handlers
import pprint
import datetime
from bs4 import BeautifulSoup
from config import parser

# Version
version = '1.2'

translator_endpoint = 'http://127.0.0.1:1969/'
# TODO: Exception for translator_endpoint unavailable: or start server automatically?
# TODO: Translator uses tons of RAM if left running in console.
def test_translator():
    """Test Zotero translation server with simple web lookup."""
    j = json.dumps({
        'url': 'http://www.tandfonline.com/doi/abs/10.1080/15424060903167229',
        'session': 'abc123'})
    h = {'Content-Type': 'application/json'}
    r = requests.post(url=translator_endpoint+'web',
                      headers=h,
                      data=j)
    if r.status_code == 200:
        return True
    return False

# TODO: move argparse to external source

args = parser.parse_args()

file_prefix = args.subreddit + '_'

# Filenames
URL_OUT = file_prefix + 'urls.txt'
BIB_OUT = file_prefix + 'library.bib'
logfile = file_prefix +__name__.strip('_')+'.log'

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
format_long = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
format_short = logging.Formatter('%(levelname)s - %(message)s')
ch.setFormatter(format_short)
ch.setLevel(logging.INFO)
#fh = logging.handlers.RotatingFileHandler(logfile, maxBytes=1000000, backupCount=10)
fh = logging.FileHandler(logfile)
fh.setFormatter(format_long)
fh.setLevel(logging.DEBUG)
logger.addHandler(ch)
logger.addHandler(fh)

# Could raise OAuth exception: handle?
# reddit = _praw.reddit()
reddit = praw.Reddit(user_agent=f'python/requests:citereddit:{version} (by /u/brainenhance)',
                    client_id=args.id,
                    client_secret=args.secret,
                    username=args.username,
                    password=args.password,
                    skip_existing=True)
if not reddit:
    logger.error('Unable to create praw.Reddit instance.')

# Setup info:
_info = {
    'Description': __doc__,
#    'Reddit API authenticated as ': reddit.user.me(),
    'Scanning subreddit: ': args.subreddit,
    'URLs exported to ': URL_OUT,
    'Library exported to ': BIB_OUT,
    'Logfile located at ': logfile,
    'Scraping started at ': datetime.datetime.now().isoformat()}
logger.info('Startup Info: \n'+pprint.pformat(_info))

submission_count = 0
url_count = 0
bib_count = 0
sess = str(random.randint(10000,99999))
with open(URL_OUT, 'w') as url_outfile, open(BIB_OUT, 'w') as bib_outfile:
# TODO: Open/Close files as needed to reduce RAM usage
# TODO: Feature: duplicate bib checker via https://github.com/perrette/papers?
# TODO: Feature: pdf file download for free-text items
    # Main loop:
    # Iterate through subreddit submissions + comments and search for urls
    # Filter out common urls and poor references
    # Request bibliographic data from Zotero translation server
    # Add bibtex style reference to output file
# TODO: still limited to 1000 submissions
    for submission in reddit.subreddit(args.subreddit).stream.submissions():
        urls = []
        text = ''
        logger.info(f'Scanning "{submission.title}"')
        submission_count += 1
        # Report the item counts every ten submissions processed
        if submission_count % 10 == 0:
            logger.info(f'Processed so far: Submissions-{submission_count}; Urls- {url_count}; Bib records- {bib_count}')
            logger.debug(f'Authentication limits: {reddit.auth.limits}')
        # detect url submission
        if submission.selftext_html is None:
            urls.append(submission.url)
        else:
            text = submission.selftext_html
        submission.comments.replace_more(limit=None)
        for com in submission.comments.list():
            text += '\n' + com.body_html
# TODO: organize line spacing better: remove duplicate '\n'
        logger.debug(f'Submission Full Text: \n"{text}"')
        soup = BeautifulSoup(text, 'lxml')
        # Extracting all the <a> tags into a list.
        tags = soup.find_all('a')
        # get the urls
        for tag in tags:
            urls.append(tag.get('href'))
        for u in urls:
            logger.info(f'Found url: <{u}>')
            url_count += 1
            # Add to url file for possible later duplicate checking
            url_outfile.write('\n' + u)
            # skip common links
# TODO: this could skip legitimate links with 'amazon' in the title: regex for domains only?
            common = ['amazon','wikipedia','ebay', 'github',
                      'google', 'reddit', 'longecity', 'youtube']
            if any([c in u for c in common]): # any can be slow: TODO?
                logger.info('Common url... skipping.')
                continue
            # Translate url to Zotero API format
            j = json.dumps({'url': u, 'session': sess})
            h = {'Content-Type': 'application/json'}
            r = requests.post(url=translator_endpoint+'web',
                              headers=h,
                              data=j)
            # Sometimes web translator responds with an empty list
            # even though url is valid reference. A second call sometimes works.
            # seems to only occur with wiley items: could be broken translator
            if r.text == '[]':
                logger.warning(f'Unknown web translator error processing url: {u}. Trying once more.')
                r = requests.post(url=translator_endpoint+'web',
                                  headers=h,
                                  data=j)
            if r.text == '[]':
                logger.warning('Second attempt yielded no results... skipping.')
                continue
            logger.debug(f'Translator response: {r.text}')
            # Skip the current url if Zotero doesn't find a match
            if r.status_code is not 200:
                logger.info(f'Web Translator Error: {r.text.strip()}')
                continue

            # r.text is now the bib info located by the translator in
            # Zotero API JSON format
            #logger.debug(f'Web Translator Full Response: \n{r.text}')
            # manipulate web translator responses
            zot_bib = json.loads(r.text) # a json list of size 0
            logger.debug(f'Web Translator Bib Item: \n{pprint.pformat(zot_bib)}')
            # skip some unreliable items
# TODO: don't skip some webpages (e.g. .gov domains)
            if zot_bib[0]['itemType'] in ['encyclopediaArticle',
                                          'blogPost',
                                          'webpage']:
                logger.info('Unreliable source... skipping.')
                continue
            # skip items without metadata
            if zot_bib[0]['creators'] == []:
                logger.info('No author found... skipping.')
                continue
            # accessDate on translation server doesn't seem to be working
#            if zot_bib[0]['accessDate'] is 'CURRENT_TIMESTAMP':
#            zot_bib[0]['accessDate'] = datetime.date.today().isoformat()
# Fixed with latest version of translation server
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
                logger.info(f'Export Translator Error: {r.text.strip()}')
                break
            bib_outfile.write(r.text+'\n')
            bib_count += 1
# TODO: log item identifier with success statement
            logger.info('Item successfully added to library.')
            url_outfile.write(' **(successful)**')
# TODO: add log 'search completed without locating url'

if __name__ == '__main__':
    # verify configuration
    # verify translation server is running
    # verify praw.Reddit instance is properly authenticated
# TODO: iterate through list of subreddits?
    pass
