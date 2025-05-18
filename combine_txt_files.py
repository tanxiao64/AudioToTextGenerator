#!/usr/bin/env python3

import os
import argparse
from pathlib import Path
import logging

"""
step3
"""
input_dir = "/Users/xiao/Documents/mjtt_audio/transcribe_version3/nyc_by_audio_txt/"
combined_file = "/Users/xiao/Documents/mjtt_audio/transcribe_version3/nyc_combined_txt/nyc_combined_text.txt"
processed_file = "/Users/xiao/Documents/mjtt_audio/transcribe_version3/nyc_combined_txt/nyc_processed_text.txt"

def setup_logging():
    """Set up logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def combine_txt_files(input_dir, output_file):
    """
    Combine all .txt files in the input directory into a single output file.
    
    Args:
        input_dir (str): Path to the directory containing text files
        output_file (str): Path to the output file
    """
    try:
        # Convert input directory to Path object
        input_path = Path(input_dir)
        
        # Check if input directory exists
        if not input_path.exists():
            raise FileNotFoundError(f"Input directory '{input_dir}' does not exist")
        
        # Get all .txt files in the directory
        txt_files = list(input_path.glob('*.txt'))
        
        # Sort files by part number
        def get_part_number(filename):
            # Extract the part number from filename like 'ny_11hr_audio_part28_transcription.txt'
            try:
                # Find the part number after 'part' and before '_transcription'
                part_str = filename.name.split('part')[1].split('_transcription')[0]
                return int(part_str)
            except (IndexError, ValueError):
                # If we can't parse the part number, put it at the end
                return float('inf')
        
        txt_files = sorted(txt_files, key=get_part_number)
        
        if not txt_files:
            logging.warning(f"No .txt files found in '{input_dir}'")
            return
        
        logging.info(f"Found {len(txt_files)} text files to combine")
        logging.info("Files will be combined in the following order:")
        for file in txt_files:
            logging.info(f"- {file.name}")
        
        # Combine all files
        with open(output_file, 'w', encoding='utf-8') as outfile:
            for txt_file in txt_files:
                logging.info(f"Processing {txt_file.name}")
                try:
                    with open(txt_file, 'r', encoding='utf-8') as infile:
                        # Add a header with the source filename
                        # outfile.write(f"\n{'='*50}\n")
                        # outfile.write(f"Content from: {txt_file.name}\n")
                        # outfile.write(f"{'='*50}\n\n")
                        
                        # Copy the content
                        outfile.write(infile.read())
                        outfile.write('\n')
                except Exception as e:
                    logging.error(f"Error processing {txt_file.name}: {str(e)}")
        
        logging.info(f"Successfully combined files into '{output_file}'")
        
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        raise

def process_combined_text(input_file, output_file):
    """
    Process the combined text file by:
    1. Splitting by hashtags (#), handling both simple splits and "#title#content" format
    2. Removing all blank spaces and newline characters
    3. Filtering out parts containing "美景听听"
    4. Putting each part on a single line
    5. Separating parts with '---'
    
    Args:
        input_file (str): Path to the input combined file
        output_file (str): Path to the output processed file
    """
    try:
        with open(input_file, 'r', encoding='utf-8') as infile:
            content = infile.read()
        
        # First split by hashtags
        raw_parts = content.split('#')
        
        # Process parts to handle "#title#content" format
        parts = []
        i = 0
        while i < len(raw_parts):
            # Skip empty parts
            if not raw_parts[i].strip():
                i += 1
                continue
                
            # If this part looks like a title (short, no spaces) and next part exists
            if (i + 1 < len(raw_parts) and 
                len(raw_parts[i].strip()) < 50):  # reasonable title length
                # Combine title and content
                combined = raw_parts[i].strip() + ':' + raw_parts[i + 1].strip()
                parts.append(combined)
                i += 2
            else:
                # Regular part, just add it
                parts.append(raw_parts[i].strip())
                i += 1
        
        # Process each part: remove blanks and newlines, filter out unwanted content
        processed_parts = []
        for part in parts:
            # Remove all whitespace and newlines
            cleaned_part = ''.join(part.split())
            # Only add non-empty parts that don't contain "美景听听"
            if cleaned_part and "美景听听" not in cleaned_part and "美景聽聽" not in cleaned_part:
                processed_parts.append(cleaned_part)
        
        # Write the processed content
        with open(output_file, 'w', encoding='utf-8') as outfile:
            outfile.write('\n---\n'.join(processed_parts))
        
        logging.info(f"Successfully processed text into '{output_file}'")
        logging.info(f"Total parts processed: {len(processed_parts)}")
        
    except Exception as e:
        logging.error(f"An error occurred during text processing: {str(e)}")
        raise

def main():
    
    setup_logging()
    
    # First combine the files
    combine_txt_files(input_dir, combined_file)
    
    # Then process the combined text
    process_combined_text(combined_file, processed_file)

if __name__ == '__main__':
    main() 