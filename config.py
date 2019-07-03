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
