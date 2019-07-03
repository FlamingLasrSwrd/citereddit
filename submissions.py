import praw

def submissions(reddit=None, subreddit=None):
    if reddit == None:
        raise ValueError # Please pass an authenticated reddit object
    if subreddit == None:
        raise ValueError # Please pass a subreddit name
