"""

"""
import logging
import os
from os import makedirs, chdir, getcwd, scandir
from shutil import rmtree

from jinja2 import Environment, PackageLoader
from youtube_dl import DownloadError, YoutubeDL

from src.postprocessors import FFmpegExtractAndCutAudioPP
from src.suggestion import get_suggestions
from src.title_parser import get_range_from_string

__author__ = "LoveIsGrief"

DOWNLOAD_SECTION = "download_and_extract_audio"

IGNORED_DOWNLOAD_ERRORS = [
    "ERROR: No media found"
]

JINJA_ENV = Environment(loader=PackageLoader("src"))


def process_submission(submission, config, reddit):
    """

    :param submission:
    :type submission: praw.models.reddit.submission.Submission
    :param config:
    :type config:
    :param reddit:
    :type reddit:
    :return:
    :rtype:
    """
    logger = logging.getLogger("bot.process_submission")
    try:
        downloaded_file = download_and_extract_audio(submission, config)
        logger.info("Download for %s '%s' '%s'", submission.shortlink, submission.url, downloaded_file)
        if not downloaded_file:
            return
        suggestions = get_suggestions(downloaded_file, config)
        if len(suggestions) > 0 and not already_commented(submission, reddit):
            comment = construct_reddit_comment(suggestions)
            submission.reply(comment)

        # TODO cleanup the directory once processing is done
    except DownloadError as de:
        if str(de) not in IGNORED_DOWNLOAD_ERRORS:
            logger.warning("DownloadError during download_and_extract_audio %s", de, exc_info=True)
    except Exception as e:
        logger.warning("Untreated error during download_and_extract_audio %s", e, exc_info=True)


def already_commented(submission, reddit):
    return len([
        comment for comment in reddit.redditor(reddit.config.username).comments.new(limit=None)
        if comment.submission.fullname == submission.fullname
    ]) > 0


def construct_reddit_comment(suggestions):
    """
    :param suggestions:
    :type suggestions: Suggestion[]
    :return:
    :rtype: str
    """
    return JINJA_ENV.get_template("comment.jinja2").render({
        "suggestions": suggestions,
        "searches": {
            "Youtube": "https://www.youtube.com/results?search_query=",
            "Soundcloud": "https://soundcloud.com/search?q=",
            "DuckDuckGo": "https://duckduckgo.com/?iax=videos&ia=videos&q=",
            "Google": "https://encrypted.google.com/search?source=lnms&tbm=vid&q="
        }
    })


def list_visible_files(directory="."):
    visible_files = [entry for entry in scandir(directory) if not entry.name.startswith('.') and entry.is_file()]
    return visible_files


def download_and_extract_audio(submission, config):
    logger = logging.getLogger("bot.download_and_extract_audio")
    filename = None

    # Moves to a temporary directory for downloading the file
    # because youtube-dl doesn't return the name of the downloaded file
    cwd = getcwd()
    download_root = config.get(DOWNLOAD_SECTION, "root_dir", fallback="downloads")
    makedirs(download_root, exist_ok=True)
    download_dir = os.path.join(download_root, submission.subreddit.display_name, submission.fullname)
    makedirs(download_dir, exist_ok=True)
    chdir(download_dir)

    try:
        with YoutubeDL(params={
            "format": "worstaudio/worstvideo/worst",
        }) as ydl:
            logger.info("Downloading file for %s from %s", submission.shortlink, submission.url)

            # Parse args from title to cut if necessary
            start, end = get_range_from_string(submission.title)
            if start or end:
                ydl.add_post_processor(FFmpegExtractAndCutAudioPP(
                    preferredcodec="best",
                    cut_start=start,
                    cut_end=end,
                    suffix="_cut"
                ))
            ret_code = ydl.download([submission.url])
            if ret_code > 0:
                raise RuntimeError("Unknown retcode from ydl: %s" % ret_code)

            # Maybe more checks have to be done to be sure it's an audio file otherwise it might crash elsewhere...
            files = list_visible_files()
            num_files = len(files)
            if num_files > 1:
                logger.warning(">1 files for %s: %s/ -> %s", submission.url, download_dir, files)
            elif num_files == 0:
                logger.warning("no files for %s")
            else:
                filename = os.path.normpath(os.path.join(download_dir, files[0].path))
    except Exception as e:
        chdir(cwd)
        if str(e) != "ERROR: Conversion failed!":
            try:
                rmtree(download_dir)
            except:
                logger.warning("Couldn't remove %s", download_dir)
        raise
    finally:
        chdir(cwd)
    return filename
