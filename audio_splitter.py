import os
import subprocess
from datetime import timedelta

"""
step1
"""
input_file = "/Users/xiao/Documents/mjtt_audio/ny_11hr_audio.m4a"

def get_audio_duration(input_file):
    """Get the duration of an audio file in seconds using ffprobe."""
    cmd = [
        'ffprobe', 
        '-v', 'error',
        '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        input_file
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return float(result.stdout.strip())

# 25 minutes limit on the api.
def split_audio(input_file, chunk_duration_minutes=25, overlap_seconds=1):
    """
    Split an audio file into chunks of specified duration with overlap using ffmpeg.
    
    Args:
        input_file (str): Path to the input audio file
        chunk_duration_minutes (int): Duration of each chunk in minutes
        overlap_seconds (int): Overlap duration in seconds
    """
    # Get total duration of the audio file
    total_duration = get_audio_duration(input_file)
    print(f"Total audio duration: {timedelta(seconds=total_duration)}")
    
    # Calculate chunk duration in seconds
    chunk_duration = chunk_duration_minutes * 60
    
    # Calculate number of chunks
    total_chunks = int(total_duration / chunk_duration) + 1
    
    # Create output directory if it doesn't exist
    output_dir = "/Users/xiao/Documents/mjtt_audio/split_audio"
    os.makedirs(output_dir, exist_ok=True)
    
    # Split the audio into chunks
    for i in range(total_chunks):
        start_time = i * chunk_duration
        duration = chunk_duration + overlap_seconds
        
        # Generate output filename
        output_filename = os.path.join(
            output_dir,
            f"{os.path.splitext(os.path.basename(input_file))[0]}_part{i+1}.m4a"
        )
        
        # Use ffmpeg to split the audio
        cmd = [
            'ffmpeg',
            '-i', input_file,
            '-ss', str(start_time),
            '-t', str(duration),
            '-c', 'copy',  # Copy the codec to avoid re-encoding
            '-y',  # Overwrite output files if they exist
            output_filename
        ]
        
        print(f"Processing chunk {i+1}/{total_chunks}: {output_filename}")
        print(f"Start time: {timedelta(seconds=start_time)}, Duration: {timedelta(seconds=duration)}")
        
        subprocess.run(cmd, check=True)
        print(f"Completed chunk {i+1}")

if __name__ == "__main__":
    # Example usage
    split_audio(input_file) 