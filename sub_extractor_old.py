import re
import codecs
import os

class Line():
    def __init__(self, hex_str,ascii_str,lang=None, start=None, duration=None):
        self.hex_str = hex_str
        self.ascii_str = ascii_str
        self.lang = False
        self.start = False
        self.duration = False
        
    def set_lang(self, lang):
        self.lang = lang
        
    def set_start(self, start):
        start = start.split(" ")
        start.reverse()
        start = "".join(start)
        start = int(start, 16)
        self.start = start
        
    def set_duration(self,duration):
        duration = duration.split(" ")
        duration.reverse()
        duration = "".join(duration)
        duration = int(duration, 16)    
        self.duration = duration
        self.end = self.start + self.duration

def extract_sub(file):
    print("Extracting subs")
    dir_name = os.path.dirname(file)
    no_ext_name = os.path.splitext(file)[0]
    filesize = os.stat(file).st_size
    SBT_indexes = []
    times_read = 0
    with open(file, 'rb') as f:
        
        while True:
            num_bytes = 8192
            buf = f.read(num_bytes)
            if buf:
                hex_str = buf.hex()        
                subs = ' '.join(re.findall('.{1,2}', hex_str))
                indexes = [m.start(0) for m in re.finditer("40 53 42 54", subs)]
                indexes = [int((index/3)+(times_read*num_bytes)) for index in indexes if ((index/3) % 16) == 0]
                SBT_indexes.extend(indexes)
                times_read += 1 
                print(f"{(f.tell() / filesize)*100:.2f}% read" , end='\r')
            else:
                break
                       
    print(SBT_indexes)          

    master_regged = []

    with open(file, 'rb') as f:
        for index in SBT_indexes:        
            f.seek(index,0)        
            chunk = f.read(1024).hex()
            subs = ' '.join(re.findall('.{1,2}', chunk))
            regged = re.findall(r"(?<=40 53 42 54).+?(?=40)",subs)
            if regged:
                master_regged.append(regged[0])
            
    lines_list = []
    for x in master_regged:
        x = x.replace(" ","")
        split_at = 96
        hex_str, ascii_str = x[:split_at], x[split_at:]    
        ascii_string = codecs.decode(ascii_str, "hex")
        ascii_txt = ascii_string.decode('utf-8','surrogateescape')
        hexes = re.findall('.{1,2}', hex_str)
        exceptions = [7,28]
        fixed_hexes = []
        for idx, hex_bit in enumerate(hexes):
            if hex_bit == "00" and idx not in exceptions:            
                hex_bit = "█"            
            fixed_hexes.append(hex_bit)
        hex_str = ' '.join(fixed_hexes) 
        hex_str.upper()    
        #print([x for x in hex_str.split() if x != "█"])
        hex_str = [x for x in [x.strip() for x in hex_str.split("█")] if x ]        
        lines_list.append(Line(hex_str,ascii_txt))
    print(f"{len(lines_list)} lines")    
    start_end = []    
    for idx, line in enumerate(lines_list):        
        line = line.ascii_str.strip('\x00')
        if line.endswith("=="):
            start_end.append(idx)
    start, end = start_end        
    lines_list = lines_list[start+1:end]
    langs = {}
    for x in lines_list:
        hex_str = x.hex_str
        text = x.ascii_str    
        x.set_lang(hex_str[5])
        x.set_start(hex_str[7])
        x.set_duration(hex_str[8])
        hex_str = '|'.join(hex_str)
        try:
            langs[x.lang].append(x)
        except:
            langs[x.lang] = [x]
        print(f"{hex_str.ljust(50)} --> {text.ljust(50)}")
        
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
        print(f"language: {lang}")
        sub_name = f"{no_ext_name}.{lang}.srt"
        with open(sub_name,"w",encoding="utf-8") as f:
            f.write('\n'.join([f"{idx+1}\n{milli_to_time(line.start)} --> {milli_to_time(line.end)}\n{line.ascii_str}\n" for idx, line in enumerate(lines)]))        
        

    # lines_list.sort(key=lambda line: line.lang)    
    # for x in lines_list:
        # print(x.ascii_str)
        #print(text)
    #print('\n'.join(regged))
    # for sub in subs:
        # bytes_object = bytes(sub, encoding='unicode_escape')
        # ascii_string = codecs.decode(bytes_object, "hex")
        # print(a)
        
if __name__ == "__main__":
    extract_sub("C:\\Users\\USER\\Desktop\\JJ\\python\\honkai CG extractor\\CGs\\2.7_CG11_mux_1.usm")