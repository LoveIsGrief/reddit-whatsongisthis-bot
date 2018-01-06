"""

"""
import logging

import acoustid

__author__ = "LoveIsGrief"
ACOUSTID_SECTION = "acoustid"


class Suggestion(object):
    """
    What we will be suggesting to the user.

    It should be linked to a recording-id in musicbrainz
    """

    def __init__(self, recording_id, artist, title):
        self._recording_id = recording_id
        self._artist = artist or ""
        self._title = title or ""

    @property
    def recording_id(self):
        return self._recording_id

    @property
    def artist(self):
        return self._artist

    @property
    def title(self):
        return self._title

    def __hash__(self):
        return hash(self._recording_id)

    def __eq__(self, other):
        if isinstance(other, Suggestion):
            return other.__hash__() == self.__hash__()
        return False

    def __str__(self):
        return "%s - %s (%s)" % (self.artist, self.title, self.recording_id)


def get_suggestions(filename, config):
    logger = logging.getLogger("bot.get_suggestions")
    suggestions = set()
    acoustid_key = config.get(ACOUSTID_SECTION, "apikey")
    for score, recording_id, title, artist in acoustid.match(acoustid_key, filename):
        suggestions.add(Suggestion(recording_id, artist, title))
        logger.info("results from acoustid %s - %s https://musicbrainz.org/recording/%s", artist, title,
                    recording_id)
    return suggestions

