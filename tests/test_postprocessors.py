import os
import unittest
from unittest import skipUnless

from src.postprocessors import FFmpegExtractAndCutAudioPP
from tests.assets import ASSETS_DIR

OCEANS_PATH = os.path.join(ASSETS_DIR, "oceans.mp4")


class DownloaderStub(object):

    def __init__(self):
        self.params = {}

    def to_screen(self, *args, **kwargs):
        pass


@skipUnless(os.path.isfile(OCEANS_PATH), "Run 'make test-assets' to download the test assets first")
class TestFFmpegExtractAndCutAudioPP(unittest.TestCase):

    def setUp(self):
        self.processor = FFmpegExtractAndCutAudioPP(downloader=DownloaderStub())
        self.oceans_probe = self.processor.probe_file(OCEANS_PATH)
        self.oceans_probe["format"]["duration"] = float(self.oceans_probe["format"]["duration"])
        self.oceans_duration = self.oceans_probe["format"]["duration"]
        self.expected_oceans_output = os.path.join(ASSETS_DIR, "oceans.m4a")

    def tearDown(self):
        if os.path.isfile(self.expected_oceans_output):
            os.remove(self.expected_oceans_output)
        self.assertFalse(os.path.isfile(self.expected_oceans_output))

    def _test_cut(self, cut_start=None, cut_end=None):
        ff = FFmpegExtractAndCutAudioPP(downloader=DownloaderStub(), cut_start=cut_start, cut_end=cut_end)
        expected_duration = self.oceans_duration
        if cut_start and cut_end:
            expected_duration = cut_end - cut_start
        elif cut_start:
            expected_duration = expected_duration - cut_start
        elif cut_end:
            expected_duration = cut_end

        ff.run({
            "filepath": OCEANS_PATH
        })
        self.assertTrue(os.path.isfile(self.expected_oceans_output))

        probe = ff.probe_file(self.expected_oceans_output)
        self.assertIsInstance(probe, dict)
        duration = float(probe["format"]["duration"])
        self.assertAlmostEqual(duration, expected_duration, delta=0.2)

    def test_start_and_end(self):
        self._test_cut(5, 10)

    def test_start_no_end(self):
        self._test_cut(5)

    def test_no_start_but_end(self):
        self._test_cut(cut_end=10)

    def test_no_start_no_end(self):
        self._test_cut()


if __name__ == '__main__':
    unittest.main()
