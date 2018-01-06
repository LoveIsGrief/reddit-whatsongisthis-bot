"""

"""
import json
import subprocess

import os
from youtube_dl.compat import compat_subprocess_get_DEVNULL
from youtube_dl.postprocessor import FFmpegExtractAudioPP
from youtube_dl.postprocessor.common import AudioConversionError
from youtube_dl.postprocessor.ffmpeg import ACODECS
from youtube_dl.utils import PostProcessingError, encodeFilename, encodeArgument, shell_quote, get_subprocess_encoding

__author__ = "LoveIsGrief"


class FFmpegExtractAndCutAudioPP(FFmpegExtractAudioPP):

    def __init__(self, downloader=None, preferredcodec=None, preferredquality=None,
                 nopostoverwrites=False,
                 cut_start=None,
                 cut_end=None,
                 suffix=None
                 ):
        """

        :param downloader:
        :type downloader:
        :param preferredcodec:
        :type preferredcodec:
        :param preferredquality:
        :type preferredquality:
        :param nopostoverwrites:
        :type nopostoverwrites:
        :param cut_start:
        :type cut_start:
        :param cut_end:
        :type cut_end:
        :param suffix: to add to the file if the filename does end up being the same
        :type suffix: str
        """
        super().__init__(downloader, preferredcodec, preferredquality, nopostoverwrites)
        self.cut_start = cut_start
        self.cut_end = cut_end
        self.suffix = suffix

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

    def run(self, information):
        path = information['filepath']

        filecodec = self.get_audio_codec(path)
        if filecodec is None:
            raise PostProcessingError('WARNING: unable to obtain file audio codec with ffprobe')

        more_opts = []
        if self._preferredcodec == 'best' or self._preferredcodec == filecodec or (self._preferredcodec == 'm4a' and filecodec == 'aac'):
            if filecodec == 'aac' and self._preferredcodec in ['m4a', 'best']:
                # Lossless, but in another container
                acodec = 'copy'
                extension = 'm4a'
                more_opts = ['-bsf:a', 'aac_adtstoasc']
            elif filecodec in ['aac', 'flac', 'mp3', 'vorbis', 'opus']:
                # Lossless if possible
                acodec = 'copy'
                extension = filecodec
                if filecodec == 'aac':
                    more_opts = ['-f', 'adts']
                if filecodec == 'vorbis':
                    extension = 'ogg'
            else:
                # MP3 otherwise.
                acodec = 'libmp3lame'
                extension = 'mp3'
                more_opts = []
                if self._preferredquality is not None:
                    if int(self._preferredquality) < 10:
                        more_opts += ['-q:a', self._preferredquality]
                    else:
                        more_opts += ['-b:a', self._preferredquality + 'k']
        else:
            # We convert the audio (lossy if codec is lossy)
            acodec = ACODECS[self._preferredcodec]
            extension = self._preferredcodec
            more_opts = []
            if self._preferredquality is not None:
                # The opus codec doesn't support the -aq option
                if int(self._preferredquality) < 10 and extension != 'opus':
                    more_opts += ['-q:a', self._preferredquality]
                else:
                    more_opts += ['-b:a', self._preferredquality + 'k']
            if self._preferredcodec == 'aac':
                more_opts += ['-f', 'adts']
            if self._preferredcodec == 'm4a':
                more_opts += ['-bsf:a', 'aac_adtstoasc']
            if self._preferredcodec == 'vorbis':
                extension = 'ogg'
            if self._preferredcodec == 'wav':
                extension = 'wav'
                more_opts += ['-f', 'wav']

        prefix, sep, ext = path.rpartition('.')  # not os.path.splitext, since the latter does not work on unicode in all setups
        new_path = prefix + sep + extension

        # Allow creating a new file if a suffix is provided
        if new_path == path and self.suffix:
            new_path = prefix + self.suffix + sep + extension

        information['filepath'] = new_path
        information['ext'] = extension

        # If we download foo.mp3 and convert it to... foo.mp3, then don't delete foo.mp3, silly.
        if (new_path == path or
                (self._nopostoverwrites and os.path.exists(encodeFilename(new_path)))):
            self._downloader.to_screen('[ffmpeg] Post-process file %s exists, skipping' % new_path)
            return [], information

        try:
            self._downloader.to_screen('[ffmpeg] Destination: ' + new_path)
            self.run_ffmpeg(path, new_path, acodec, more_opts)
        except AudioConversionError as e:
            raise PostProcessingError(
                'audio conversion failed: ' + e.msg)
        except Exception:
            raise PostProcessingError('error running ' + self.basename)

        # Try to update the date time for extracted audio file.
        if information.get('filetime') is not None:
            self.try_utime(
                new_path, time.time(), information['filetime'],
                errnote='Cannot update utime of audio file')

        return [path], information

