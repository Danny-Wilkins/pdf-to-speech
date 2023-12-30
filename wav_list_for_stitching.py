import os
import subprocess
import glob

dir = directory = os.getcwd().replace('\\', '/')

# os.chdir(dir)

wav_list = glob.glob(f"{dir}\*.wav")

with open("wav_list.txt", "w") as wav_list_file:
    for wav in wav_list:
        wav_list_file.write("file '" + wav + "'\n")

subprocess.run("ffmpeg -f concat -safe 0 -i wav_list.txt -c copy output.wav", shell=True, check=True)

print("done")