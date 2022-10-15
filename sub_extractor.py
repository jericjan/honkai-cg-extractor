"module for extracting the subtitles of a CG file"

import re
import codecs


class NoSubsFound(Exception):
    "raised when no subtitles are found on a CG file"


class StartEndError(Exception):
    "raised when there is an issue with finding the start and end of the subs in a .usm file"


class Line:
    "class for containing language, start time, and duration of 1 line of a subtitle"

    def __init__(self, hex_str, ascii_str):
        self.hex_str = hex_str
        self.ascii_str = ascii_str
        self.lang = False
        self.start = False
        self.duration = False
        self.end = False

    def set_lang(self, lang):
        "sets the language of the subtitle line"
        self.lang = lang

    def set_start(self, start):
        "sets the start time of the subtitle line"
        start = start.split(" ")
        start.reverse()
        start = "".join(start)
        start = int(start, 16)
        self.start = start

    def set_duration(self, duration):
        "sets the duration and end time of the subtitle line"
        duration = duration.split(" ")
        duration.reverse()
        duration = "".join(duration)
        duration = int(duration, 16)
        self.duration = duration
        self.end = self.start + self.duration


def extract_sub(file):
    """
    extracts the subtitles. this is what you want to run.
    Please provide a pathlib.Path variable here.
    """
    print("Extracting subs")
    no_ext_name = file.parent / file.stem
    filesize = file.stat().st_size
    SBT_indexes = []
    times_read = 0
    with open(file, "rb") as f:

        while True:
            num_bytes = 8192
            buf = f.read(num_bytes)
            if buf:
                hex_str = buf.hex()
                subs = " ".join(re.findall(".{1,2}", hex_str))
                indexes = [m.start(0) for m in re.finditer("40 53 42 54", subs)]
                indexes = [
                    int((index / 3) + (times_read * num_bytes))
                    for index in indexes
                    if ((index / 3) % 16) == 0
                ]
                SBT_indexes.extend(indexes)
                times_read += 1
                print(f"{(f.tell() / filesize)*100:.2f}% read", end="\r")
            else:
                break

    master_regged = []

    with open(file, "rb") as f:
        for index in SBT_indexes:
            f.seek(index, 0)
            chunk = f.read(1024).hex()
            subs = " ".join(re.findall(".{1,2}", chunk))
            regged = re.findall(r"(?<=40 53 42 54).+?(?=40 53)", subs)
            if regged:
                master_regged.append(regged[0])

    lines_list = []
    if len(master_regged) == 0:
        raise NoSubsFound(
            "No subtitles were found. This CG may not have any subtitles."
        )
    for x in master_regged:
        x = x.replace(" ", "")
        split_at = 96
        hex_str, ascii_str = x[:split_at], x[split_at:]
        ascii_string = codecs.decode(ascii_str, "hex")
        ascii_txt = ascii_string.decode("utf-8", "surrogateescape")
        hexes = re.findall(".{1,2}", hex_str)
        exceptions = [7, 28]
        fixed_hexes = []
        for idx, hex_bit in enumerate(hexes):
            if hex_bit == "00" and idx not in exceptions:
                hex_bit = "█"
            fixed_hexes.append(hex_bit)
        hex_str = " ".join(fixed_hexes)
        hex_str.upper()
        # print([x for x in hex_str.split() if x != "█"])
        hex_str = [x for x in [x.strip() for x in hex_str.split("█")] if x]
        lines_list.append(Line(hex_str, ascii_txt))
    print(f"{len(lines_list)} lines")
    start_end = []
    for idx, line in enumerate(lines_list):
        line = line.ascii_str.strip("\x00")
        if line.endswith("=="):
            start_end.append(idx)
    if len(start_end) != 2:
        raise StartEndError(
            "Encountered an issue with finding the start and end of the subtitles"
        )
    start, end = start_end
    lines_list = lines_list[start + 1 : end]
    langs = {}
    for x in lines_list:
        try:
            hex_str = x.hex_str
            text = x.ascii_str
            x.set_lang(hex_str[5])
            x.set_start(hex_str[7])
            x.set_duration(hex_str[8])
            hex_str = "|".join(hex_str)
            if x.lang in langs:
                langs[x.lang].append(x)
            else:
                langs[x.lang] = [x]
            print(f"{hex_str.ljust(50)} --> {text.ljust(50)}")
        except IndexError:
            print(f"{hex_str} ERROR!!!")

    def milli_to_time(milliseconds):
        seconds = milliseconds // 1000
        milliseconds = milliseconds % 1000
        seconds = seconds % (24 * 3600)
        hour = seconds // 3600
        seconds %= 3600
        minutes = seconds // 60
        seconds %= 60
        return f"{hour:02}:{minutes:02}:{seconds:02},{milliseconds:03}"

    for lang, lines in langs.items():

        lang_dict = {"01": "en", "06": "id", "03": "th", "02": "vi", "00": "cn"}
        if lang in lang_dict:
            lang = lang_dict[lang]
            print(f"{lang} subs found")
        else:
            print(f"found unknown sub with code {lang}")
        sub_name = f"{no_ext_name}.{lang}.srt"
        with open(sub_name, "w", encoding="utf-8") as f:
            nul = "\x00"
            f.write(
                "\n".join(
                    [
                        f"{idx+1}\n{milli_to_time(line.start)} --> {milli_to_time(line.end)}\n{line.ascii_str.strip(nul)}\n"
                        for idx, line in enumerate(lines)
                    ]
                )
            )

    # lines_list.sort(key=lambda line: line.lang)
    # for x in lines_list:
    # print(x.ascii_str)
    # print(text)
    # print('\n'.join(regged))
    # for sub in subs:
    # bytes_object = bytes(sub, encoding='unicode_escape')
    # ascii_string = codecs.decode(bytes_object, "hex")
    # print(a)
