import unittest
import os
from unittest import skipUnless

from src.postprocessors import FFmpegExtractAndCutAudioPP
from tests.assets import ASSETS_DIR

MP4_PATH = os.path.join(ASSETS_DIR, "oceans.mp4")


class DownloaderStub(object):

    def __init__(self):
        self.params = {}

    def to_screen(self, *args, **kwargs):
        pass


@skipUnless(os.path.isfile(MP4_PATH), "Run 'make test-assets' to download the test assets first")
class TestFFmpegExtractAndCutAudioPP(unittest.TestCase):
    def test_simple_cut(self):
        ff = FFmpegExtractAndCutAudioPP(downloader=DownloaderStub(), cut_start=5, cut_end=10)
        ff.run({
            "filepath": MP4_PATH
        })


if __name__ == '__main__':
    unittest.main()
