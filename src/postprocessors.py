"""

"""
from youtube_dl.postprocessor import FFmpegExtractAudioPP

__author__ = "LoveIsGrief"


class FFmpegExtractAndCutAudioPP(FFmpegExtractAudioPP):

    def __init__(self, downloader=None, preferredcodec=None, preferredquality=None, nopostoverwrites=False,
                 cut_start=None,
                 cut_end=None,
                 ):
        super().__init__(downloader, preferredcodec, preferredquality, nopostoverwrites)
        self.cut_start = cut_start
        self.cut_end = cut_end

    def run_ffmpeg(self, path, out_path, codec, more_opts):

        if self.cut_start:
            more_opts = more_opts + ["-ss", str(self.cut_start)]

        if self.cut_end:
            duration = self.cut_end
            if self.cut_start:
                duration -= self.cut_start
            more_opts = more_opts + ["-t", str(duration)]

        super(FFmpegExtractAndCutAudioPP, self).run_ffmpeg(path, out_path, codec, more_opts)
