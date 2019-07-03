import requests
import json
import random
from pprint import pprint
import praw

def translator():
    translator_endpoint = 'http://127.0.0.1:1969/'
    url = 'https://onlinelibrary.wiley.com/doi/full/10.1046/j.1365-2605.1999.00196.x'

    sess = str(random.randint(10000,99999))
    j = json.dumps({'url': url, 'sessionid': sess})
    h = {'Content-Type': 'application/json'}
    r = requests.post(url=translator_endpoint+'web',
                      headers=h,
                      data=j)
    print(r.status_code)
    print(r.text)
    print(type(r.text))

    response = r.text

reddit = praw.Reddit(user_agent='python/requests:citereddit:0.1 (by /u/brainenhance)',
                    client_id='GFJ1GoVsJecCyg',
                    client_secret='28nXzvKg90Cj6opJMAiTc8ZPZoo',
                    username='brainenhance',
                    password='SgLX-2o8',
                    skip_existing=True)
#subs = []
#for submission in reddit.subreddit('Nootropics').stream.submissions(limit=10):
