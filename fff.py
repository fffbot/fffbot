import base64
import logging
import os
import re
import threading
import time

import html2text
import praw
import requests

import version_info

logger = logging.getLogger(__name__)
comment_delay = int(os.getenv('COMMENT_DELAY_SECONDS', 120))
cooldown_time = int(os.getenv('COOL_DOWN_SECONDS', 5 * 60))
subreddits = os.getenv('SUBREDDITS', 'bottesting+factorio')
imgur_auth_token = os.getenv('IMGUR_AUTH')
github_auth_token = os.getenv('GITHUB_AUTH')
github_base_url = "https://fffbot.github.io/fff/"


def main():
    logger.info("Starting fffbot version " + version_info.git_hash + "/" + version_info.build_date)
    while True:
        try:
            listen_for_submissions()
        except Exception:
            logger.exception("Caught exception while listening for submissions")
            logger.error("Sleeping " + str(cooldown_time) + "s to cool down")
            time.sleep(cooldown_time)
            logger.error("Done sleeping, going to start listening again")


def listen_for_submissions():
    reddit = praw.Reddit(user_agent='fffbot/2.0 (by /u/fffbot; PRAW; https://github.com/fffbot/fffbot)')
    subs = reddit.subreddit(subreddits)

    logger.info("Starting to listen for submissions in " + subreddits)
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
    logger.info(
        "Encountered submission; id: " + submission.id + "; title: " + submission.title + "; url: " + submission.url)
    if 'factorio.com/blog/post/fff' in submission.url:
        logger.info("Submission identified as FFF post, starting thread to sleep and process")
        thread = threading.Thread(target=sleep_and_process, args=(submission,))
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


def convert_web_videos_to_img(clipped):
    return re.sub(r'<video.+?<source\s+?src="(.+?)\.(webm|mp4)".*?>.*?</video>', r'<img src="\g<1>.webm"/>', clipped,
                  flags=re.IGNORECASE | re.MULTILINE | re.DOTALL)

def convert_youtube_embed(clipped):
    # <iframe.+?youtube\.com\/embed\/(\w+).*?<\/iframe>
    return re.sub(r'<iframe.+?youtube\.com/embed/(\w+).*?</iframe>', r'<a href="https://www.youtube.com/watch?v=\g<1>">https://www.youtube.com/watch?v=\g<1></a>', clipped,
                  flags=re.IGNORECASE | re.MULTILINE | re.DOTALL)


def to_markdown(html):
    md = html2text.html2text(html, bodywidth=1000)
    images_to_urls = re.sub(r'!\[\]\((.+)\)', r'(\g<1>)', md)
    return images_to_urls.replace(r'(/blog/)', r'(https://www.factorio.com/blog/)').strip()


def create_imgur_album(fff_url):
    title = 'Factorio Friday Facts #' + extract_fff_number(fff_url)
    description = fff_url

    logger.info('Creating Imgur album with title: ' + title + '; description: ' + description)
    data = {'title': title, 'description': description, 'privacy': 'public'}
    headers = {'Authorization': 'Bearer ' + imgur_auth_token}

    r = requests.post('https://api.imgur.com/3/album', data=data, headers=headers)
    logger.info('Imgur album response ' + str(r.status_code) + '; body: ' + r.text)

    if r.status_code != 200:
        raise Exception('Non-OK response from Imgur creating album ' + title)

    return r.json()['data']['id']


def upload_to_imgur(album, url):
    logger.info('Uploading image to Imgur: ' + url)
    data = {'image': url, 'type': 'URL', 'album': album}
    headers = {'Authorization': 'Bearer ' + imgur_auth_token}

    r = requests.post('https://api.imgur.com/3/image', data=data, headers=headers)
    logger.info('Imgur image response ' + str(r.status_code) + '; body: ' + r.text)

    if r.status_code != 200:
        logger.error('Non-OK response from Imgur uploading ' + url + ', using original')
        return url
    else:
        return r.json()['data']['link']


def filter_factorio_com(urls):
    for url in urls:
        if "factorio.com" in url: yield url


def find_images(html):
    urls = re.findall(r'<img.+?src="(.+?)".+?>', html, flags=re.IGNORECASE | re.MULTILINE | re.DOTALL)
    return set(filter_factorio_com(urls))


def to_dict(urls):
    r = {}
    for url in urls:
        r[url] = url
    return r


def upload_webms_to_github(urls, fff_url):
    if not urls:
        return {}

    if github_auth_token is None:
        logger.warning("No Github auth, not rehosting webms")
        return to_dict(urls)

    try:
        fff = extract_fff_number(fff_url)

        r = {}
        for url in urls:
            r[url] = upload_to_github(fff, url)
        return r
    except Exception:
        logger.exception("Caught exception uploading to Github, using original webms")
        return to_dict(urls)


def upload_file_to_github(filename, contents, message):
    logger.info("Uploading file to Github: " + filename)
    encoded = base64.b64encode(contents).decode('utf-8')
    data = {
        'message': message,
        'committer': {
            'name': "fffbot",
            'email': "38205055+fffbot@users.noreply.github.com"
        },
        'content': encoded
    }
    headers = {'Authorization': 'token ' + github_auth_token}

    r = requests.put('https://api.github.com/repos/fffbot/fff/contents/' + filename, json=data, headers=headers)
    logger.info("Github contents response " + str(r.status_code) + "; body: " + r.text)

    if r.status_code >= 400:
        raise Exception("Non-OK response from Github uploading " + filename)

    return r.json()['content']['path']


def upload_to_github(fff, url):
    logger.info("Downloading to memory: " + url)
    req = requests.get(url)
    if req.status_code >= 400:
        raise Exception("Unexpected status downloading " + url + ": " + str(req.status_code) + "; body:" + req.text)

    filename = "images/" + fff + "/" + url[url.rfind("/") + 1:]

    logger.info("Uploading image file to Github: " + filename)
    try:
        return github_base_url + upload_file_to_github(filename, req.content,
                                                       "Uploading " + filename + "\n\nSource: " + url)
    except Exception:
        logger.error("Exception uploading " + url + " to Github, using original")
        return url


def upload_all_to_imgur(urls, fff_url):
    if not urls:
        return {}

    if imgur_auth_token is None:
        logger.warning('No Imgur auth, not rehosting images')
        return to_dict(urls)

    try:
        album = create_imgur_album(fff_url)

        r = {}
        for url in urls:
            r[url] = upload_to_imgur(album, url)
        return r
    except Exception:
        logger.exception("Caught exception uploading to Imgur, using original images")
        return to_dict(urls)


def replace_images(html, images):
    for key, value in images.items():
        html = html.replace(key, value)
    return html


def rehost_all_images(html, url):
    all_images = find_images(html)

    webms = [img for img in all_images if img.lower().endswith('.webm')]  # [x for x in mylist if x in goodvals]
    others = [img for img in all_images if not img.lower().endswith('.webm')]  # [x for x in mylist if x in goodvals]

    github_rehosted = upload_webms_to_github(webms, url)
    imgur_rehosted = upload_all_to_imgur(others, url)

    return replace_images(html, {**imgur_rehosted, **github_rehosted})


def extract_fff_number(url):
    return url.split('fff-')[1][:4]


def process(url):
    html = requests.get(url).text
    logger.info("Fetched data (" + str(len(html)) + ") bytes")

    clipped = clip(html)
    if clipped is None:
        logger.error("Unable to clip html data: " + html)
        return

    converted_videos = convert_web_videos_to_img(clipped)
    converted_youtube_embed = convert_youtube_embed(converted_videos)

    rehosted = rehost_all_images(converted_youtube_embed, url)

    markdown = to_markdown(rehosted)
    logger.info("Data clipped and converted to " + str(len(markdown)) + " total bytes")

    reply = markdown if len(markdown) <= 9980 else markdown[:9980] + ' _(...)_'
    if len(markdown) > 9980:
        logger.warning("Markdown text was longer than 9980 characters, abbreviated to 9980 characters")
    return reply


def sleep_and_process(submission):
    logger.info("Sleeping for " + str(comment_delay) + "s")
    time.sleep(comment_delay)

    logger.info("Done sleeping, processing " + submission.id + "; Fetching url: " + submission.url)
    reply = process(submission.url)

    logger.info("Adding top-level comment to " + submission.id)
    top_level_comment = submission.reply("(Expand to view FFF contents. Or don't, I'm not your master... yet.)")
    logger.info("Added top-level comment: " + top_level_comment.id + ", adding reply: " + reply)

    reply_comment = top_level_comment.reply(reply)
    logger.info("Added reply comment: " + reply_comment.id)

    logger.info("All done")


if __name__ == '__main__':
    logging.basicConfig(format='%(levelname)8s [%(asctime)s] [%(thread)d] %(name)s: %(message)s', level=logging.INFO)
    main()
