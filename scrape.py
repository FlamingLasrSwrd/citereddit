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
                    help="Reddit API username.",
                    default='')
parser.add_argument("-p", "--password", type=str,
                    help="Reddit API password.",
                    default='')

args = parser.parse_args()

reddit = praw.Reddit(user_agent='Extraction (by /u/BrainEnhance et. al.)',
                    client_id=args.id,
                    client_secret=args.secret,
                    username=args.username,
                    password=args.password)

p = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'

urls = []
for submission in reddit.subreddit('Nootropics').stream.submissions():
    text = submission.selftext

    for u in re.findall(p, text):
        if u is not []:
            print(u)
#            urls.append(u)

#    submission.comments.replace_more(limit=None)
#    for comment in submission.comments.list():
#        print(comment.date)
#        print(comment.body)
