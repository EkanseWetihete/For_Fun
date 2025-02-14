import subprocess
from moviepy.editor import VideoFileClip, AudioFileClip
from pydub import AudioSegment
from pydub.effects import normalize, compress_dynamic_range
from tqdm import tqdm
import re

print("Starting program...")

# Define file paths
video_name = "epicea stream"
video_path = "MP4 Videos/" + video_name + ".mp4"
audio_path = "music/extracted_audio_" + video_name + ".wav"
normalized_audio_path = "music/normalized_audio_" + video_name + ".wav"
final_video_path = "MP4 Videos/FLouder_" + video_name + ".mp4"

def main():
    #stuff()
    step3()

# Step 1: Extract audio using ffmpeg
def video_stuff():
    print("Extracting audio from video...")
    try:
        process = subprocess.Popen(["ffmpeg", "-i", video_path, "-q:a", "0", "-map", "a", audio_path],
                                   stderr=subprocess.PIPE, universal_newlines=True)
    
        percentage_pattern = re.compile(r'(\d+)%')
    
        with tqdm(unit="%", total=100) as pbar:
            for line in process.stderr:
                match = percentage_pattern.search(line)
                if match:
                    percentage = int(match.group(1))
                    pbar.n = percentage
                    pbar.last_print_n = percentage
                    pbar.update(0)
    
            process.wait()
            pbar.n = 100
            pbar.last_print_n = 100
            pbar.update(0)
    
        if process.returncode == 0:
            print(f"Converted {video_path} to {audio_path} successfully.")
        else:
            print(f"Error converting {video_path} to {audio_path}")
    
    except subprocess.CalledProcessError as e:
        print(f"Error converting {video_path} to {audio_path}: {e}")
    
    print("Audio extraction completed.")

    
def audio_stuff():
    # Step 2: Load and process the audio
    print("Loading and processing audio...")
    
    audio = AudioSegment.from_wav(audio_path)
    
    # Normalize the audio
    print("Normalizing audio...")
    normalized_audio = normalize(audio)
    print("Normalization completed.")
    compressed_audio = compress_dynamic_range(normalized_audio)
    compressed_audio.export("processed_audio.wav", format="wav")
    
    # Apply low-pass filter to reduce high-frequency noise (adjust frequency as needed)
    chunk_size_ms = 1000  # 1 second chunks
    low_pass_filtered_chunks = []
    
    for i in tqdm(range(0, len(normalized_audio), chunk_size_ms), desc="Applying low-pass filter"):
        chunk = normalized_audio[i:i + chunk_size_ms]
        filtered_chunk = chunk.low_pass_filter(5000)
        low_pass_filtered_chunks.append(filtered_chunk)
    
    low_pass_filtered_audio = sum(low_pass_filtered_chunks)
    print("Low-pass filter applied.")
    
    # Reduce loud segments without using a noise gate
    def reduce_loud_segments(segment, threshold=-12.0, reduction_dB=25.0):
        return segment.apply_gain(-reduction_dB) if segment.dBFS > threshold else segment
    
    # Boost quiet segments
    def boost_quiet_segments(segment, threshold=-20.0, gain_dB=22.0):
        return segment.apply_gain(gain_dB) if segment.dBFS < threshold else segment
    
    # Process audio in chunks
    print("Processing audio in chunks...")
    processed_chunks = []
    
    for i in tqdm(range(0, len(low_pass_filtered_audio), chunk_size_ms), desc="Processing chunks"):
        chunk = low_pass_filtered_audio[i:i + chunk_size_ms]
        chunk = boost_quiet_segments(chunk)
        chunk = reduce_loud_segments(chunk)
        processed_chunks.append(chunk)
    
    processed_audio = sum(processed_chunks)
    print("Audio processing completed.")
    
    # Apply dynamic range compression
    print("Applying dynamic range compression...")
    def compress_audio(audio_segment, threshold=-20.0, ratio=5.0):
        return audio_segment.compress_dynamic_range(threshold=threshold, ratio=ratio)
    
    compressed_chunks = []
    
    for i in tqdm(range(0, len(processed_audio), chunk_size_ms), desc="Compressing audio"):
        chunk = processed_audio[i:i + chunk_size_ms]
        compressed_chunk = compress_audio(chunk)
        compressed_chunks.append(compressed_chunk)
    
    final_audio = sum(compressed_chunks)
    print("Dynamic range compression completed.")
    
    # Export the processed audio
    print("Exporting processed audio...")
    final_audio.export(normalized_audio_path, format="wav")
    print("Audio normalization and compression completed.")
    return
    
def step3():
    # Step 3: Merge processed audio with the original video
    print("Merging processed audio with original video...")
    video = VideoFileClip(video_path)
    normalized_audio = AudioFileClip(normalized_audio_path)
    final_video = video.set_audio(normalized_audio)
    final_video.write_videofile(final_video_path, codec="libx264", audio_codec="aac")
    print("Merging completed. Final video saved.")
    return
    
main()