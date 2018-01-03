"""
A simple bot that checks SUBREDDITS every DEFAULT_INTERVAL seconds and take an action.
"""
import argparse
from configparser import ConfigParser
from threading import Timer

import praw
import signal
import sys
import logging

__author__ = "LoveIsGrief"
__version__ = "0.0.1"

CONFIG_FILENAME = "bot.ini"
AUTH_SECTION = "authentication"
AUTH_SECTION_OPTIONS = ["client_id", "client_secret", "username", "password"]
KEEPER_SECTION = "subreddit_keepers"
USER_AGENT = "reddit-whatsongisthis-bot_%s" % __version__

DEFAULT_INTERVAL = 60.0

SUBREDDITS = [
    "namethissong",
    "whatsongisthis",
    "whatsthissong"
]

logging.basicConfig(level=logging.INFO)


def main(client_id, client_secret, username, password, config_path):
    reddit = praw.Reddit(client_id=client_id,
                         client_secret=client_secret,
                         username=username,
                         password=password,
                         user_agent=USER_AGENT,
                         )

    logging.info("Starting up")
    t = {"timer": None}

    def signal_handler(signal, frame):
        print('You pressed Ctrl+C! Canceling timer or waiting for operation to end')
        t["timer"].cancel()
        t["timer"].join()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    print('Press Ctrl+C to cancel')

    def dat_loop():
        config = ConfigParser()
        config.read(config_path)
        for subreddit in SUBREDDITS:

            if KEEPER_SECTION not in config:
                config.add_section(KEEPER_SECTION)
            before = config.get(KEEPER_SECTION, subreddit, fallback="")

            # So reddit decided to sort everything in temporal line yet and name their paging params using temporal prepositions
            # #1 = most recent, N = oldest ; after=N --> next request #1 = N+1, #100 = N100
            # ==> using after means going backwards in time
            # ==> using before means going forwards in time
            # totally makes sense... stellar
            logging.info("Requesting new from '%s' after '%s'", subreddit, before)
            news = reddit.subreddit(subreddit).new(limit=100, params=dict(before=before))
            first = None
            counter = 0
            for post in news:
                if not first:
                    first = post.fullname
                logging.debug("%s | self: %s, video: %s @ %s", post.title, post.is_self, post.is_video, post.url)
                counter += 1
            logging.info("Treated %s submissions", counter)
            config.set(KEEPER_SECTION, subreddit, first or before)

        with open(config_path, "w") as f:
            config.write(f)

        logging.info("Looping in %s seconds", DEFAULT_INTERVAL)
        t["timer"] = Timer(DEFAULT_INTERVAL, dat_loop)
        t["timer"].start()

    dat_loop()
    signal.pause()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Starts the bot"
    )
    parser.add_argument("-v", "--verbose", action='store_true')
    parser.add_argument("config_path", help="Location of the config file")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    config_path = args.config_path

    # Make sure the config is alright
    config = ConfigParser()
    if not config.read(config_path):
        print("Couldn't open %s" % config_path)
        exit(1)

    if AUTH_SECTION not in config:
        print("!!!MISSING '%s' section in config file" % AUTH_SECTION)
        exit(1)

    missing_auth_params = [options for options in AUTH_SECTION_OPTIONS
                           if not config.has_option(AUTH_SECTION, options)]
    if missing_auth_params:
        print("!!!MISSING %s options in '%s' section" % (" , ".join(missing_auth_params), AUTH_SECTION))
        exit(1)

    main(
        config.get(AUTH_SECTION, "client_id"),
        config.get(AUTH_SECTION, "client_secret"),
        config.get(AUTH_SECTION, "username"),
        config.get(AUTH_SECTION, "password"),
        config_path
    )
