import re
import os

# filename = "The.Big.Bang.Theory.S10E11.720p.HDTV.X264-DIMENSION.HI.srt"
# search_word = ["possum", "wheezy", "pedestrian", "sprinkle"]


class ParseSegmentException(Exception):
    """
    This exception is raised if the file segment is not parsed correctly. We assume that subtitle
    file is split by '\n', if this is not the case, this exception may be raise.
    """


class SubtitleFileNotAllowed(Exception):
    """
    This exception is raised if the subtitle file is not valid. Usually because the file ext is
     not in the allowed list
    """


class Subtitle:

    def __init__(self, directory):
        self.directory = directory

    def extension_allowed(self, filename):
        if "." in filename:
            extension = filename.split(".")[-1]
            return extension.lower() in ["srt", "ass", "ssa"]
        raise SubtitleFileNotAllowed("{} is not valid, please check".format(filename))

    def list_files(self):
        files = os.listdir(self.directory)
        for filename in files:
            if self.extension_allowed(filename):
                yield filename

    def get_segment(self):
        for filename in self.list_files():
            with open(filename, mode="r", encoding="utf-8") as f:
                segment = []
                for line in f:
                    if line != "\n":
                        segment.append(line.strip())
                    else:
                        yield segment
                        segment = []

    def get_all_sentences(self):
        punctuation = (".", "?")
        sentence = ''
        for segment in self.get_segment():
            _, _, string = self.parse_segment(segment)
            sentence += " "
            sentence += string
            if string.endswith(punctuation):
                yield sentence
                sentence = ''

    def parse_segment(self, segment):
        try:
            num = segment[0]
            time = segment[1]
            string = " ".join(segment[2:])
            return num, time, string
        except IndexError:
            raise ParseSegmentException


    def get_word_sentence(self, word):
        match_list = []
        for sentence in self.get_all_sentences():
            match = re.search(word, sentence)
            if match is not None:
                match_list.append(sentence)
        return "\n **************\n".join(match_list)

    def move(self, directory):
        """move all the subtitle files to the specify directory"""
        pass

