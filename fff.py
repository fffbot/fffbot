import praw
import requests

reddit = praw.Reddit(user_agent='fffbot/2.0 (by /u/fffbot; pyfff; PRAW)')

subs = reddit.subreddit('bottesting+factorio')

print("Starting to listen for submissions")
for submission in subs.stream.submissions():
    print("Encountered submission: " + submission.title + "; " + submission.url)
    if 'factorio.com/blog/post/fff' in submission.url:
        print("FFF submission found; title: " + submission.title + "; url: " + submission.url)
        data = requests.get(submission.url).text
        print("Fetched data: " + data)
