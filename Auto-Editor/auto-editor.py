# -*- coding: utf-8 -*-
import subprocess
import re
import sys
from tqdm import tqdm
import os

"""
Auto video editor program. 
It definitelly needs improvements but if you have a well adjusted audio, it could potentially save a lot of time editing long videos.
It can convert videos to different formats (Mainly tested with .mp4 and .flv so, it might need some additional functionality for other formats).
"Reconvert = true" is meant for optimizing a video by removing audio tracks and making a smaller video size.
Audio and motion is meant for video editing, how often it should cut a video whenever an audio or movement is detected.
Mergin is how much time before a cut should be kept before making a cut.

Recommended to test it with 5 min long videos first!
"""

def main():
    #editor = editing(input_location="", margin=2, audio=0.45, motion=0.01)
    editor = editing(video_name="Okabe voice act - perfection 3", margin=1.2, audio=0.4, motion=0.02, video_format=".mp4")
    editor.reconverter()
    
    #editor.edit_video(video_name="1", video_format=".mp4", amount="all")#, reconvert = False)
    
    # Additional examples
    # editing.edit_video(video_name="testingVid", input_location="FLV Videos/")
    # editing.edit_video(video_name="omega", input_location="D:/Videos/big vids/")
    # editing.edit_video(video_name="segment_1", input_location="output_segments/", video_format=".mp4")
    # editing.edit_video(video_name="2024-10-29 20-02-42", input_location="C:/Games/Other/vid/", video_format=".mp4")
    # editing.edit_video(video_name="1", input_location="MP4 Videos/", video_format=".mp4")   
    
    
    
    
    print("Done!")
    

class editing:
    def __init__(self, video_name="", input_location="Videos/", video_format=".mp4", output_location="", margin=1.75, audio=0.4, motion=0.02):
        self.video_name = video_name
        self.input_location = input_location
        self.video_format = video_format
        self.output_location = output_location
        self.margin = margin
        self.audio = audio
        self.motion = motion
        self.last_format = ""
        
        if (input_location == ""):
            self.input_location = "Videos/"
    
    def print_decorator(func): # Makes an empty print for each function
        def wrapper(*args, **kwargs):
            print()
            return func(*args, **kwargs)
        return wrapper
    
    @print_decorator
    def edit_video(self, video_name, video_format, amount="Single", reconvert = True): #video name and format input is needed
        self.video_name = video_name
        self.video_format = video_format
        
        margin = self.margin
        audio = self.audio
        motion = self.motion
        
        self.create_directory()
        
        if (amount == "all"):
            self.edit_all()
            return
        
        converted_file = ""
        
        if (reconvert == True):
            self.reconverter()
            converted_file = "Converted/" + video_name + "_Converted" + self.video_format
        else:
            converted_file = self.input_location + "Videos/" + video_name + self.video_format
            
        
        return
        
        # Construct auto-editor command
        output_file = self.output_location + "Edited/" + video_name.replace("_Converted","") + "_Edited.mp4"
        command = [
            "auto-editor", converted_file,
            "--margin", f"{margin}s",
            "--video-bitrate", "8000k", # Change this if you want lower or higher quality! (8000k is good for 1080p videos)
            "--edit", f"(or audio:{audio} motion:{motion})",
            "-c:a", "copy", 
            "--output", output_file,
        ]
        
        print("Preparations complete!")
        
        # Run the auto-editor command with a progress bar
        try:
            print("Executing video editor...")
            with tqdm(unit="%", total=100) as pbar:
                process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                percentage_pattern = re.compile(r'(\d+\.\d+)%')
                
                for line in process.stdout:
                    match = percentage_pattern.search(line)
                    if match:
                        percentage = float(match.group(1))
                        pbar.n = percentage
                        pbar.last_print_n = percentage
                        pbar.update(0)
                
                for line in process.stderr:
                    sys.stderr.write(line)
                
                process.wait()
                pbar.n = 100
                pbar.last_print_n = 100
                pbar.update(0)

            if process.returncode == 0:
                print(f"Edited video saved as {output_file} successfully.")
            else:
                print(f"Error editing video: {process.stderr.read()}")

        except subprocess.CalledProcessError as e:
            print(f"Error editing video: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            
    @print_decorator
    def edit_all(self):
        base_path = self.input_location
        video_format = self.video_format
        
        for file_name in os.listdir(base_path):
            if file_name.endswith(video_format):
                print(os.path.splitext(file_name)[0])
                file_name = os.path.splitext(file_name)[0]
                
                
                print("video name: " + file_name + ", input location: " + base_path + ", video format: " + video_format)
                self.edit_video(video_name=file_name, video_format=video_format)
        
    @print_decorator
    def convert_video(self, format_to=".flv", input_file=""):
        if (input_file == ""):
            input_file = self.input_location + self.video_name + self.video_format
        else:
            input_file = input_file + self.video_name + self.video_format
        
        converted_file = self.output_location + "Converted/" + self.video_name + "_Converted" + format_to
        
        if "_Converted" in self.video_name: # To make sure, naming is correct for reconverter.
            converted_file = converted_file.replace("_Converted", "")
            if converted_file.endswith(format_to):
                converted_file = converted_file[:-len(format_to)]
                converted_file = converted_file + "_Converted" + format_to
            
        if (not os.path.isfile(input_file)):
            print("File in a given path does not exist.")
            print("Given path:" + input_file)
            return
        
        convert_command = [
            "ffmpeg", "-i", input_file, 
            "-c:v", "h264_nvenc",  # Using NVIDIA NVENC for faster encoding
            "-c:a", "aac",
            "-b:a", "192k", 
            "-b:v", "8000k",
            "-map", "0:v:0",  # Video track -- change if you have more than 1 video view
            "-map", "0:a:0",  # Audio track
            converted_file
        ]
        try:
            print(f"Converting {input_file} to {converted_file}...")
            process = subprocess.Popen(convert_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)
            
            print("Conversion might take longer than intended, please wait.")
            with tqdm(unit="%", total=100, desc="Conversion Progress") as pbar:
                while True:
                    line = process.stderr.readline()
                    if line == '' and process.poll() is not None:
                        break
                    if line:
                        # Use the size of the converted file to calculate the percentage
                        percentage_match = re.search(r'frame=\s*\d+', line)
                        if percentage_match:
                            frame_str = percentage_match.group().split('=')[1].strip()
                            try:
                                frame = int(frame_str)
                                percentage = min(100, round(frame / 1950, 2))  # Adjust this calculation as needed for better accuracy
                                pbar.n = percentage
                                pbar.refresh()  # Refresh the tqdm progress bar
                            except ValueError:
                                pass
                    
                    pbar.update(0)  # Force an update to keep the progress bar active
        
                process.wait()
                pbar.n = 100
                pbar.refresh()
        
            if process.returncode == 0:
                print(f"Converted {input_file} to {converted_file} successfully.")
            else:
                print(f"Error converting {input_file} to {converted_file}: {process.stderr.read()}")
                return
        except subprocess.CalledProcessError as e:
            print(f"Error converting {input_file} to {converted_file}: {e}")
            return
    
    @print_decorator
    def reconverter(self): # It changes file size to way smaller by removing unecesarry audio tracks.
        print("Converting to .flv")
        self.convert_video(format_to=".flv")
        
        print(f"Converting to {self.video_format}")
        self.video_name = self.video_name + "_Converted"
        
        video_format = self.video_format  # Temporarily changing format
        self.video_format = ".flv"
        
        self.convert_video(format_to=video_format, input_file = "Converted/")
        self.video_format = video_format # Changing back format
        
    
    @print_decorator
    def create_directory(self):
        print("Creating directory...")
        try:
            os.makedirs(self.output_location + "Converted", exist_ok=True)
            print("Directory 'Converted' created successfully.")
            os.makedirs(self.output_location + "Edited", exist_ok=True)
            print("Directory 'Edited' created successfully.")
        except PermissionError:
            print(f"Error: Permission denied to create the directory '{self.output_location}'.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            
    

main()
