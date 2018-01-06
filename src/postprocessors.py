"""

"""
import json
import subprocess

from youtube_dl.compat import compat_subprocess_get_DEVNULL
from youtube_dl.postprocessor import FFmpegExtractAudioPP
from youtube_dl.utils import PostProcessingError, encodeFilename, encodeArgument, shell_quote, get_subprocess_encoding

__author__ = "LoveIsGrief"


class FFmpegExtractAndCutAudioPP(FFmpegExtractAudioPP):

    def __init__(self, downloader=None, preferredcodec=None, preferredquality=None, nopostoverwrites=False,
                 cut_start=None,
                 cut_end=None,
                 ):
        super().__init__(downloader, preferredcodec, preferredquality, nopostoverwrites)
        self.cut_start = cut_start
        self.cut_end = cut_end

    def probe_file(self, path):
        """
        Gets information about a media file

        :param path:
        :type path: str
        :return: json
        :rtype: dict
        """
        if not self.probe_available:
            raise PostProcessingError('ffprobe or avprobe not found. Please install one.')
        args = "-v quiet -print_format json -show_format -show_streams".split(" ")
        args = [encodeArgument(arg) for arg in args]
        try:
            cmd = [encodeFilename(self.probe_executable, True)] + args \
                  + [encodeFilename(self._ffmpeg_filename_argument(path), True)]
            if self._downloader.params.get('verbose', False):
                self._downloader.to_screen('[debug] %s command line: %s' % (self.basename, shell_quote(cmd)))
            handle = subprocess.Popen(cmd, stderr=compat_subprocess_get_DEVNULL(), stdout=subprocess.PIPE,
                                      stdin=subprocess.PIPE)
            output = handle.communicate()[0]
            if handle.wait() != 0:
                return None
        except (IOError, OSError):
            return None
        decoded_output = output.decode(get_subprocess_encoding(), 'ignore')
        return json.loads(decoded_output)

    def run_ffmpeg(self, path, out_path, codec, more_opts):

        if self.cut_start:
            more_opts = more_opts + ["-ss", str(self.cut_start)]

        if self.cut_end:
            duration = self.cut_end
            if self.cut_start:
                duration -= self.cut_start
            more_opts = more_opts + ["-t", str(duration)]

        super(FFmpegExtractAndCutAudioPP, self).run_ffmpeg(path, out_path, codec, more_opts)
