import praw
import requests
import html2text
import re
import logging


logger = logging.getLogger(__name__)


def process_submission(submission):
    logger.info("Encountered submission; id: " + submission.id + "; title: " + submission.title + "; url: " + submission.url)
    if 'factorio.com/blog/post/fff' in submission.url:
        logger.info("Submission identified as FFF post")

        html = requests.get(submission.url).text
        logger.info("Fetched data: " + str(len(html)))

        clipped = clip(html)
        if clipped is None:
            logger.error("Unable to clip html data: " + html)
            return

        markdown = to_markdown(clipped)
        logger.info('Output markdown:\n' + markdown + '\nLength: ' + str(len(markdown)))
        comment = submission.reply(markdown[:9990] + ' (...)')
        logger.info('Added comment: ' + comment.id)


def clip(html):
    h2_index = html.find('<h2')
    if h2_index == -1:
        logger.error("No <h2 found in text: " + html)
        return

    footer_index = html.find('"footer"', h2_index)
    if footer_index == -1:
        logger.error('No "footer" found in text: ' + html)
        return

    div_index = html.rfind('<div', 0, footer_index)
    if div_index == -1:
        logger.error('<div not found in text: ' + html)
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

    logger.info("Starting to listen for submissions")
    logger.info("Skipping first 100 submissions")
    i = 1
    # TODO: use skip_existing in PRAW 6
    for submission in subs.stream.submissions():
        if i > 100:
            process_submission(submission)
        else:
            logger.info("Skipping submission #" + str(i) + ": " + submission.id + " (" + submission.title + ")")
            i = i + 1


if __name__ == '__main__':
    logging.basicConfig(format='%(levelname)8s [%(asctime)s] [%(thread)d] %(name)s: %(message)s', level=logging.INFO)
    do_eet()
