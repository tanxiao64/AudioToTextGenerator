import os
import google.generativeai as genai
from pathlib import Path
import mimetypes
import argparse
from dotenv import load_dotenv


"""
step2
"""

load_dotenv()

def setup_gemini(api_key):
    """Set up the Gemini API with the provided API key."""
    genai.configure(api_key=api_key)

def transcribe_audio(audio_path, output_path):
    """
    Transcribe an audio file using Gemini API and save the transcription.
    
    Args:
        audio_path (str): Path to the audio file
        output_path (str): Full path where to save the transcription
    """
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Initialize the model
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    # Get the MIME type of the audio file
    mime_type = mimetypes.guess_type(audio_path)[0]
    if not mime_type or not mime_type.startswith('audio/'):
        mime_type = 'audio/mpeg'  # default to mp3 if can't determine
    
    # Read the audio file
    with open(audio_path, 'rb') as audio_file:
        audio_data = audio_file.read()
    
    # Create the audio blob
    audio_blob = {
        "mime_type": mime_type,
        "data": audio_data
    }
    
    # Create the prompt for transcription
    prompt = """You are a professional audio transcription expert specializing in Mandarin Chinese tour guide content. Your task is to transcribe the provided audio with high accuracy and natural language flow.

Key Requirements:
1. Content Organization:
   - Use hashtags (#) to separate distinct topics or contexts
   - Each section must be self-contained and maintain complete context
   - Avoid splitting sections that reference previous content (e.g., sections starting with "this" or "it")
   - Keep sections between 80-1500 words for optimal readability

2. Language and Style:
   - Output in simplified Chinese characters
   - Maintain a professional yet engaging tour guide tone
   - Preserve cultural nuances and local expressions
   - Include relevant pauses and emphasis markers where appropriate

3. Content Focus:
   - Focus exclusively on speech content
   - Ignore background noise and non-speech audio
   - Preserve important tour guide information (locations, historical facts, cultural references)
   - Maintain accuracy of numbers, dates, and proper nouns

4. Quality Standards:
   - Ensure grammatical correctness
   - Maintain consistent terminology throughout
   - Preserve the original speaker's intent and meaning
   - Format text for easy reading and comprehension

Please transcribe the audio following these guidelines while maintaining the authenticity and professionalism of the tour guide's delivery."""
    
    # Generate the transcription
    response = model.generate_content([prompt, audio_blob])
    
    # Save the transcription
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(response.text)
    
    print(f"Transcription saved to: {output_path}")
    return output_path

def process_directory(input_dir, output_dir):
    """
    Process all audio files in a directory and transcribe them.
    
    Args:
        input_dir (str): Directory containing audio files
        output_dir (str): Directory to save transcriptions
    """
    # Supported audio formats
    audio_extensions = {'.mp3', '.wav', '.m4a', '.ogg', '.flac'}
    
    # Get all files in the directory
    audio_files = []
    for file in os.listdir(input_dir):
        file_path = os.path.join(input_dir, file)
        if os.path.isfile(file_path) and Path(file).suffix.lower() in audio_extensions:
            audio_files.append(file_path)
    
    if not audio_files:
        print(f"No audio files found in {input_dir}")
        return
    
    print(f"Found {len(audio_files)} audio files to process")
    
    # Process each audio file
    for audio_path in audio_files:
        try:
            print(f"\nProcessing: {audio_path}")
            # Construct output path for batch processing
            audio_filename = Path(audio_path).stem
            output_path = os.path.join(output_dir, f"{audio_filename}_transcription.txt")
            transcribe_audio(audio_path, output_path)
        except Exception as e:
            print(f"Error processing {audio_path}: {str(e)}")
            continue

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Transcribe audio files using Gemini API')
    parser.add_argument('input_path', help='Path to audio file or directory')
    parser.add_argument('-o', '--output', required=True,
                      help='For single file: full output file path (e.g., /path/to/output.txt). For directory: output directory path')
    args = parser.parse_args()
    
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("Please set your Google API key as an environment variable 'GOOGLE_API_KEY'")
        return
    
    # Set up Gemini
    setup_gemini(api_key)
    
    if not os.path.exists(args.input_path):
        print("Error: Input path not found")
        return
    
    try:
        if os.path.isdir(args.input_path):
            # Process directory
            process_directory(args.input_path, args.output)
        else:
            # Process single file with exact output path
            output_path = transcribe_audio(args.input_path, args.output)
            print(f"Successfully transcribed audio to: {output_path}")
    except Exception as e:
        print(f"Error during processing: {str(e)}")

if __name__ == "__main__":
    main() 