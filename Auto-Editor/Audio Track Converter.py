import subprocess
import os

"""
Working audio track extractor. You need to give an output and input (video) file to proceeed.
This is only extracting selected audio tracks from a video or a list of videos.
Recording Software like OBS uses seperate tracks to record audio. (Needs aditional configuration)
For ex.: You can have an audio of you talking and a game audio seperately.

Added audio normalizer too, just in case if you need it and sometimes forget to use it in video editor softwares.
"""

def main(): 
    video_file = 'C:/Users/Snake/.spyder-py3/Video Editor/MP4 Videos/ai2u/segment_1.mp4'
    output_dir = 'output_audio_tracks' # It is converted to .mka and .wav but .wav is a final normalized version.

    # List of track indices to extract
    track_indices = [1, 2, 3, 4]

    for track_index in track_indices:
        extract_audio_track(video_file, track_index, output_dir, normalize=True)


def extract_audio_track(video_file, track_index, output_dir, normalize=False):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Define the intermediate .mka file path
    intermediate_file = os.path.join(output_dir, f'audio_track_{track_index}.mka')
    # Define the final output file path
    output_file = os.path.join(output_dir, f'audio_track_{track_index}.wav')

    # Extract the audio track to .mka format
    extract_command = [
        'ffmpeg',
        '-i', video_file,
        '-map', f'0:{track_index}',
        '-c', 'copy',
        intermediate_file
    ]

    try:
        print(f'Running command: {" ".join(extract_command)}')
        result = subprocess.run(extract_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            print(f'Error extracting audio track {track_index}:')
            print(result.stderr)
            return
    except Exception as e:
        print(f'An error occurred: {e}')
        return

    # Normalize the audio if requested
    if normalize:
        normalize_command = [
            'ffmpeg',
            '-i', intermediate_file,
            '-filter:a', 'loudnorm',
            output_file
        ]
    else:
        normalize_command = [
            'ffmpeg',
            '-i', intermediate_file,
            output_file
        ]

    try:
        print(f'Running command: {" ".join(normalize_command)}')
        result = subprocess.run(normalize_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            print(f'Converted and normalized audio track {track_index} to {output_file}')
        else:
            print(f'Error converting and normalizing audio track {track_index}:')
            print(result.stderr)
    except Exception as e:
        print(f'An error occurred: {e}')

main()