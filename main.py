from subprocess import Popen, PIPE
import shutil
import os
from shlex import join as shlexjoin
import glob
import argparse
from sub_extractor import extract_sub, NoSubsFound
parser = argparse.ArgumentParser()
parser.add_argument('files', metavar='FILES', type=str, nargs='*', default='none',
                    help='.usm files to be converted')
parser.add_argument('-a','--audio', action='store_true')                    
parser.add_argument('-s','--subs', action='store_true')
args = vars(parser.parse_args())


def run_sub(coms):    
    with Popen(coms, stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True) as proc:
        stdout, stderr = proc.communicate()
        if proc.returncode == 1:
            print(stderr.decode("utf-8"))   
       
def get_full_path(rel_path):
    return os.path.join(os.getcwd(),rel_path)

def ask_yes_no(question):    
    while True:
        with_audio = input(f"{question} (y/n)\n").lower()
        if with_audio == "y":
            return True
        elif with_audio == "n":
            return False
        else:
            print("Try again")  
            
def main():            
    if not os.path.exists("CGs/"):
        os.mkdir("CGs")
    if args['files'] != "none":        
        opened_files = args['files']
        print(f"{len(opened_files)} CGs provided")
    else:
        ofw_path = get_full_path("OpenedFilesView\\OpenedFilesView.exe")
        run_sub([ofw_path, "/scomma", "opened_files.txt", "/wildcardfilter", "*.usm"])
        with open("opened_files.txt",encoding="utf-8") as f:
            opened_files = f.read()
        opened_files = opened_files.split("\n")    
        opened_files = [x for x in opened_files if x ]
        opened_files = [file.split(",")[1] for file in opened_files]    
        print(f"{len(opened_files)} CGs found")
                              
    if opened_files:
        with_audio = ask_yes_no("Do you want to include audio?")
        with_subs = ask_yes_no("Do you want to also export the subtitles?")
        file_paths = opened_files
        for file in file_paths:    
            dest_path = os.path.join(os.getcwd(),"CGs\\")
            shutil.copy(file,dest_path)
            usm_file = os.path.join(dest_path,os.path.basename(file))
            just_name = os.path.splitext(usm_file)[0]
            print(f"Demuxing {os.path.basename(file)}")
            demuxer_path = get_full_path("UsmDemuxer/UsmDemuxer.exe")
            run_sub([demuxer_path,usm_file])
            print(f"Demux done.")
            if with_subs:
                try:
                    extract_sub(usm_file)
                except NoSubsFound as e:
                    print(e)
            os.remove(usm_file)        
            vid_file = glob.glob(f"{just_name}*.m2v")[0]
            audio_file_exists = True
            try:
                aud_file = glob.glob(f"{just_name}*.hca")[0]
            except IndexError:
                print("No audio file found.")
                audio_file_exists = False
            mkv_file = f"{just_name}.mkv"
            mp4_file = f"{just_name}.mp4"
            if with_audio:       
                print("Converting audio to AAC...")
                run_sub(["ffmpeg", "-i", aud_file, "-y", "temp.aac"])
                print("Adding audio to video...")
                run_sub(["ffmpeg", "-i", vid_file, "-i", "temp.aac", "-map","0:v:0","-map","1:a:0","-y","-c","copy",mp4_file]) 
                os.remove("temp.aac")
            else:            
                print("Losslessly converting to MP4")
                run_sub(["ffmpeg", "-i", vid_file, "-c","copy","-y",mp4_file])   
            os.remove(vid_file)
            if audio_file_exists:
                os.remove(aud_file)
            if os.path.exists("opened_files.txt"):
                os.remove("opened_files.txt")
        print("Done!")
        print(f'Check your "{dest_path}" folder for the CGs')
        input()
    else:
        print("There are no opened .usm files. Exiting...")

if __name__ == "__main__":
    main()