import base64
import logging
import os
import re
import threading
import time
import re

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
max_comment_length = int(os.getenv("MAX_COMMENT_LENGTH", 9900))


def main():
    logger.info("Starting fffbot version " + version_info.git_hash + "/" + version_info.build_date)
    logger.info("Comment delay: " + str(comment_delay) + "s; cooldown time: " + str(cooldown_time) + "s; subreddits: "
                + subreddits + "; max comment length: " + str(max_comment_length))
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
    for submission in subs.stream.submissions(skip_existing=True):
        process_submission(submission)


def is_altf4(url):
    return 'alt-f4.blog' in url


def process_submission(submission):
    logger.info(
        "Encountered submission; id: " + submission.id + "; title: " + submission.title + "; url: " + submission.url)
    if 'factorio.com/blog/post/fff' in submission.url or is_altf4(submission.url):
        logger.info("Submission identified as FFF/ALT-F4 post (URL: " + submission.url + "), starting thread to sleep and process")
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
    return re.sub(r'<video.+?<source\s+?src="(.+?)\.(webm|mp4)".*?>.*?</video>', r'<img src="\g<1>.\g<2>"/>', clipped,
                  flags=re.IGNORECASE | re.MULTILINE | re.DOTALL)


def convert_youtube_embed(clipped):
    return re.sub(r'<iframe.+?youtube\.com/embed/(\w+).*?</iframe>',
                  r'<a href="https://www.youtube.com/watch?v=\g<1>">https://www.youtube.com/watch?v=\g<1></a>', clipped,
                  flags=re.IGNORECASE | re.MULTILINE | re.DOTALL)


def to_markdown(html):
    md = html2text.html2text(html, bodywidth=1000)
    images_to_urls = re.sub(r'!\[\]\((.+)\)', r'(\g<1>)', md)
    return images_to_urls.replace(r'(/blog/)', r'(https://www.factorio.com/blog/)').strip()


def create_imgur_album(fff_url):
    nr = extract_fff_number(fff_url)
    title = 'ALT-F4 #' + nr if is_altf4(fff_url) else 'Factorio Friday Facts #' + extract_fff_number(fff_url)
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


def filter_relevant_image_urls(urls):
    for url in urls:
        if 'factorio.com' in url or 'alt-f4.blog' in url or not url.startswith('http'):
            yield url


def find_images(html):
    urls = re.findall(r'<img.+?src="(.+?)".+?>', html, flags=re.IGNORECASE | re.MULTILINE | re.DOTALL)
    return set(filter_relevant_image_urls(urls))


def upload_all_to_github(urls, fff_url):
    if not urls:
        return {}

    if github_auth_token is None:
        logger.warning("No Github auth, not rehosting videos")
        return urls

    try:
        nr = extract_fff_number(fff_url)
        name = 'altf4-' + nr if is_altf4(fff_url) else extract_fff_number(fff_url)

        r = {}
        for k, v in urls.items():
            r[k] = upload_to_github(name, v)
        return r
    except Exception:
        logger.exception("Caught exception uploading to Github, using original videos")
        return urls


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


def upload_to_github(name, url):
    logger.info("Downloading to memory: " + url)
    req = requests.get(url)
    if req.status_code >= 400:
        raise Exception("Unexpected status downloading " + url + ": " + str(req.status_code) + "; body:" + req.text)

    filename = "images/" + name + "/" + url[url.rfind("/") + 1:]

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
        return urls

    try:
        album = create_imgur_album(fff_url)

        r = {}
        for k, v in urls.items():
            r[k] = upload_to_imgur(album, v)
        return r
    except Exception:
        logger.exception("Caught exception uploading to Imgur, using original images")
        return urls


def replace_images(html, images):
    for key, value in images.items():
        html = html.replace(key, value)
    return html


def rehost_all_images(html, url):
    images = find_images(html)
    baseurl = extract_base_url(url)

    videos = {}
    others = {}
    for imgurl in images:
        resolved = imgurl
        if not imgurl.startswith('http'): # relative URL
            resolved = baseurl + imgurl if imgurl.startswith('/') else baseurl + '/' + imgurl

        ext = imgurl.lower()
        if ext.endswith('.webm') or ext.endswith('.mp4'):
            videos[imgurl] = resolved
        else:
            others[imgurl] = resolved

    imgur_rehosted = upload_all_to_imgur(others, url)
    videos_rehosted = upload_all_to_github(videos, url)

    return replace_images(html, {**imgur_rehosted, **videos_rehosted})


def extract_base_url(url):
    return 'https://alt-f4.blog' # for now assume only ALT+F4 uses relative image URLs...


def extract_fff_number(url):
    if 'alt-f4' in url:
        return url.split('ALTF4-')[1][:6]
    else:
        return url.split('fff-')[1][:4]


def slice_replies(markdown, maxlen):
    """
    slices markdown on logical boundries.
    logical boundries in order of precedence:
    - end of string
    - end of paragraph
    - fallback on a maxlen

    if len(markdown) == 0 returns empty list
    """
    # end of string so slice_replies("x\n\nx", 9000) is one reply
    # end of paragraph so slice_replies("xxx\n\nxxx", 6) splits ["xxx\n\n", "xxx"] rather then ["xxx\n\nx", "xx"]
    # fallback so slice_replies("xxxxxx", 3) splits ["xxx", "xxx"]
    pattern = re.compile(
        r"""
            # [\w\W] = any character(including newline)
            # {1,maxlen} = at least one character and up to maxlen characters
            # \Z = end of string
            # \n\n = end of paragraph
            # | = logical or
            [\w\W]{1,maxlen}\Z
            | [\w\W]{1,maxlen}\n\n
            | [\w\W]{1,maxlen}
        """.replace("maxlen", str(int(maxlen))),
        re.MULTILINE | re.VERBOSE
    )
    replies = pattern.findall(markdown)
    # add continue characters to replies
    for i, reply in enumerate(replies):
        prefix = "«\n\n" if i > 0 else ""
        postfix = "\n\n»" if i < len(replies)-1 else ""
        replies[i] = prefix + reply + postfix
    return replies


def process(url):
    r = requests.get(url)
    r.encoding = 'UTF-8'  # https://github.com/fffbot/fffbot/issues/2
    html = r.text
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

    return slice_replies(markdown, max_comment_length)


def sleep_and_process(submission):
    logger.info("Sleeping for " + str(comment_delay) + "s")
    time.sleep(comment_delay)

    logger.info("Done sleeping, processing " + submission.id + "; Fetching url: " + submission.url)
    replies = process(submission.url)

    reply_count = len(replies)
    logger.info(str(reply_count) + " replies returned")

    if replies is None or reply_count == 0:
        logger.error("No replies returned, not posting anything")
        return

    logger.info("Adding top-level comment to " + submission.id)
    top_level_comment = submission.reply("(Expand to view contents, if you would like.)")
    logger.info("Added top-level comment: " + top_level_comment.id + ", going to add " + str(reply_count) + " replies")

    previous_reply = top_level_comment
    for reply in replies:
        logger.info("Posting reply using parent " + previous_reply.id + ": " + reply)
        previous_reply = previous_reply.reply(reply)
        logger.info("Added reply: " + previous_reply.id)

    logger.info("All done")


if __name__ == '__main__':
    logging.basicConfig(format='%(levelname)8s [%(asctime)s] [%(thread)d] %(name)s: %(message)s', level=logging.INFO)
    main()
