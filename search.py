import re

filename = "The.Big.Bang.Theory.S10E11.720p.HDTV.X264-DIMENSION.HI.srt"
search_word = ["possum", "wheezy", "pedestrian", "sprinkle"]


class Parse:

    def __init__(self, filename):
        self.filename = filename

    def get_segment(self):
        with open(self.filename, mode="r", encoding="utf-8") as f:
            segment = []
            for line in f:
                if line != "\n":
                    segment.append(line.strip())
                else:
                    yield segment
                    segment = []

    def get_full_sentence(self):
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
        num = segment[0]
        time = segment[1]
        string = " ".join(segment[2:])
        return num, time, string


def get_re_str(search_word):
    return "|".join(search_word)


parse = Parse(filename=filename)
for sentence in parse.get_full_sentence():
    re_str = get_re_str(search_word)
    match = re.search(re_str, sentence)
    if match is not None:
        print(match.group(), sentence)
