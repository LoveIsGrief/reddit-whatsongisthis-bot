"""

"""
import logging
import os
from os import makedirs, chdir, getcwd, scandir
from shutil import rmtree

import acoustid
from youtube_dl import DownloadError, YoutubeDL

__author__ = "LoveIsGrief"

DOWNLOAD_SECTION = "download_and_extract_audio"
ACOUSTID_SECTION = "acoustid"

IGNORED_DOWNLOAD_ERRORS = [
    "ERROR: No media found"
]


def process_submission(submission, config):
    logger = logging.getLogger("bot.process_submission")
    try:
        downloaded_file = download_and_extract_audio(submission, config)
        logger.info("Download for %s '%s' '%s'", submission.shortlink, submission.url, downloaded_file)

        acoustid_key = config.get(ACOUSTID_SECTION, "apikey")
        for score, recording_id, title, artist in acoustid.match(acoustid_key, downloaded_file):
            logger.info("results from acoustid %s - %s https://musicbrainz.org/recording/%s", artist, title, recording_id)

        # TODO cleanup the directory once processing is done
    except DownloadError as de:
        if str(de) not in IGNORED_DOWNLOAD_ERRORS:
            logger.warning("DownloadError during download_and_extract_audio %s", de, exc_info=True)
    except Exception as e:
        logger.warning("Untreated error during download_and_extract_audio %s", e, exc_info=True)


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
            "postprocessors": [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': "best"
            }]
        }) as ydl:
            logger.info("Downloading file for %s from %s",submission.shortlink, submission.url)
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
