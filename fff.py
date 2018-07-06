import praw
import requests
import html2text
import re


def process_submission(submission):
    print("Encountered submission; id: " + submission.id + "; title: " + submission.title + "; url: " + submission.url)
    if 'factorio.com/blog/post/fff' in submission.url:
        print("Submission identified as FFF post")
        if 'test' in submission.title:
            print('Title contains "test"')
            html = requests.get(submission.url).text
            print("Fetched data: ", len(html))
            clipped = clip(html)
            markdown = to_markdown(clipped)
            print('Output markdown:\n' + markdown + '\nLength: ', len(markdown))
            comment = submission.reply(markdown[:9990] + ' (...)')
            print('Added comment ' + comment.id)


def clip(html):
    h2_index = html.find('<h2')
    if h2_index == -1:
        print("No <h2 found in text: ", html)
        return

    footer_index = html.find('"footer"', h2_index)
    if footer_index == -1:
        print('No "footer" found in text: ', html)
        return

    div_index = html.rfind('<div', 0, footer_index)
    if div_index == -1:
        print('<div not found in text: ', html)
        return

    header_to_div = html[h2_index:div_index]
    return header_to_div


def to_markdown(html):
    md = html2text.html2text(html)
    images_to_urls = re.sub(r'!\[\]\((.+)\)', r'(\g<1>)', md)
    return images_to_urls.replace(r'(/blog/)', r'(https://www.factorio.com/blog/)').strip()


def do_eet():
    reddit = praw.Reddit(user_agent='fffbot/2.0 (by /u/fffbot; pyfff; PRAW)')

    subs = reddit.subreddit('bottesting+factorio')

    print("Starting to listen for submissions")
    print("Skipping first 100 submissions")
    i = 1
    for submission in subs.stream.submissions():
        if i > 100:
            process_submission(submission)
        else:
            print("Skipping submission #" + str(i) + ": " + submission.id + " (" + submission.title + ")")
            i = i + 1


if __name__ == '__main__':
    do_eet()
