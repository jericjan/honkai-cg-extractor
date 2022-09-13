from subprocess import Popen, PIPE
import shutil
import os
from shlex import join as shlexjoin
import glob

def run_sub(coms):    
    with Popen(coms, stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True) as proc:
        stdout, stderr = proc.communicate()
        if proc.returncode == 1:
            print(stderr.decode("utf-8"))   
       
def get_full_path(rel_path):
    return os.path.join(os.getcwd(),rel_path)

if not os.path.exists("CGs/"):
    os.mkdir("CGs")

ofw_path = get_full_path("OpenedFilesView\\OpenedFilesView.exe")
run_sub([ofw_path, "/scomma", "opened_files.txt", "/wildcardfilter", "*.usm"])
with open("opened_files.txt",encoding="utf-8") as f:
    opened_files = f.read()
opened_files = opened_files.split("\n")    
opened_files = [x for x in opened_files if x ]
print(f"{len(opened_files)} CGs found")

def ask_audio():    
    while True:
        with_audio = input("Do you want to include audio? (y/n)\n").lower()
        if with_audio == "y":
            return True
        elif with_audio == "n":
            return False
        else:
            print("Try again")            
            
     
if opened_files:
    with_audio = ask_audio()
    file_paths = [file.split(",")[1] for file in opened_files]    
    for file in file_paths:    
        dest_path = os.path.join(os.getcwd(),"CGs\\")
        shutil.copy(file,dest_path)
        usm_file = os.path.join(dest_path,os.path.basename(file))
        just_name = os.path.splitext(usm_file)[0]
        print(f"Demuxing {os.path.basename(file)}")
        demuxer_path = get_full_path("UsmDemuxer/UsmDemuxer.exe")
        run_sub([demuxer_path,usm_file])
        os.remove(usm_file)        
        vid_file = glob.glob(f"{just_name}*.m2v")[0]
        aud_file = glob.glob(f"{just_name}*.hca")[0]
        mkv_file = f"{just_name}.mkv"
        mp4_file = f"{just_name}.mp4"
        if with_audio:            
            run_sub(["ffmpeg", "-i", vid_file, "-i", aud_file, "-map","0:v:0","-map","1:a:0","-y",mkv_file]) 
        else:            
            run_sub(["ffmpeg", "-i", vid_file, "-c","copy","-y",mp4_file])   
        os.remove(vid_file)
        os.remove(aud_file)
        os.remove("opened_files.txt")
        print("Done!")
        print(f'Check your "{dest_path}" folder for the CGs')
        input()
else:
    print("There are no opened .usm files. Exiting...")
