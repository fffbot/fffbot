import logging
import re
import threading
import time

import html2text
import os
import praw
import requests


logger = logging.getLogger(__name__)
comment_delay = int(os.getenv('COMMENT_DELAY_SECONDS', 120))
cooldown_time = int(os.getenv('COOL_DOWN_SECONDS', 5*60))
subreddits = os.getenv('SUBREDDITS', 'bottesting+factorio')
imgur_auth_token = os.getenv('IMGUR_AUTH')


def main():
    while True:
        try:
            listen_for_submissions()
        except Exception:
            logger.exception("Caught exception while listening for submissions")
            logger.error("Sleeping " + str(cooldown_time) + "s to cool down")
            time.sleep(cooldown_time)
            logger.error("Done sleeping, going to start listening again")


def listen_for_submissions():
    reddit = praw.Reddit(user_agent='fffbot/2.0 (by /u/fffbot; pyfff; PRAW)')
    subs = reddit.subreddit(subreddits)

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


def process_submission(submission):
    logger.info("Encountered submission; id: " + submission.id + "; title: " + submission.title + "; url: " + submission.url)
    if 'factorio.com/blog/post/fff' in submission.url:
        logger.info("Submission identified as FFF post, starting thread to sleep and process")
        thread = threading.Thread(target=sleep_and_process, args=(submission, ))
        thread.daemon = True
        thread.start()
        logger.info("Thread started")


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
    md = html2text.html2text(html, bodywidth=1000)
    images_to_urls = re.sub(r'!\[\]\((.+)\)', r'(\g<1>)', md)
    return images_to_urls.replace(r'(/blog/)', r'(https://www.factorio.com/blog/)').strip()


def upload_to_imgur(url):
    if imgur_auth_token is None:
        logger.warning('No Imgur auth, not rehosting ' + url)
        return url

    logger.info('Uploading image to Imgur: ' + url)
    data = {'image': url, 'type': 'URL'}
    headers = {'Authorization': 'Bearer ' + imgur_auth_token}

    r = requests.post('https://api.imgur.com/3/image', data=data, headers=headers)
    logger.info('Imgur response ' + str(r.status_code) + '; body: ' + r.text)

    if r.status_code != 200:
        raise Exception('Non-OK response from Imgur')

    return r.json()['data']['link']


def filter_factorio_com(urls):
    for url in urls:
        if "factorio.com" in url: yield url


def find_images(html):
    urls = re.findall(r'<img.+?src="(.+?)".+?>', html, flags=re.IGNORECASE | re.MULTILINE | re.DOTALL)
    return set(filter_factorio_com(urls))


def upload_all_to_imgur(urls):
    try:
        r = {}
        for url in urls:
            imgurl = upload_to_imgur(url)
            r[url] = imgurl
        return r
    except Exception:
        logger.exception("Caught exception uploading to imgur, using original images")
        r = {}
        for url in urls:
            r[url] = url
        return r


def replace_images(html, images):
    for key, value in images.items():
        html = html.replace(key, value)
    return html


def rehost_all_images(html):
    images = find_images(html)
    rehosted = upload_all_to_imgur(images)
    return replace_images(html, rehosted)


def sleep_and_process(submission):
    logger.info("Sleeping for " + str(comment_delay) + "s")
    time.sleep(comment_delay)

    logger.info("Done sleeping, processing " + submission.id + "; Fetching url: " + submission.url)
    html = requests.get(submission.url).text
    logger.info("Fetched data (" + str(len(html)) + ") bytes")

    clipped = clip(html)
    if clipped is None:
        logger.error("Unable to clip html data: " + html)
        return

    rehosted = rehost_all_images(clipped)

    markdown = to_markdown(rehosted)
    logger.info("Data clipped and converted to " + str(len(markdown)) + " total bytes")

    reply = markdown if len(markdown) <= 9980 else markdown[:9980] + ' _(...)_'
    if len(markdown) > 9980:
        logger.warning("Markdown text was longer than 9980 characters, abbreviated to 9980 characters")

    logger.info("Adding comment to " + submission.id + ": " + reply)
    comment = submission.reply(reply)
    logger.info('Added comment: ' + comment.id)


if __name__ == '__main__':
    logging.basicConfig(format='%(levelname)8s [%(asctime)s] [%(thread)d] %(name)s: %(message)s', level=logging.INFO)
    main()
