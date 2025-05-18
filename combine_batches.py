import os
import glob
import re
"""
step5: combine all the batch files into a single file
"""
# Directory with the batch files
input_dir = "/Users/xiao/Documents/mjtt_audio/transcribe_version3/nyc_combined_english_txt"
batch_pattern = "*_batch_*.txt"

# Output file
output_file = "/Users/xiao/Documents/mjtt_audio/transcribe_version3/nyc_combined_english_final.txt"

def get_batch_number(filename):
    """Extract the batch number from the filename."""
    # Match any pattern ending with _batch_XXX.txt where XXX is a number
    match = re.search(r'_batch_(\d+)\.txt$', filename)
    if match:
        return int(match.group(1))
    return 0

def combine_batches():
    """Combine all batch files into a single file."""
    # Get all batch files
    batch_files = glob.glob(os.path.join(input_dir, batch_pattern))
    
    if not batch_files:
        print(f"No batch files found matching pattern '{batch_pattern}' in '{input_dir}'")
        return
    
    # Sort the files by batch number to maintain original order
    batch_files.sort(key=get_batch_number)
    
    print(f"Found {len(batch_files)} batch files to combine.")
    print("Files will be processed in this order:")
    for i, file in enumerate(batch_files):
        print(f"  {i+1}. {os.path.basename(file)} (batch #{get_batch_number(file)})")
    
    # Initialize the combined content
    combined_content = []
    total_sections = 0
    
    # Process each batch file
    for batch_file in batch_files:
        with open(batch_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split the content into sections
        sections = content.split('\n---\n')
        sections = [section for section in sections if section.strip()]
        
        # Add to the combined content
        combined_content.extend(sections)
        total_sections += len(sections)
        
        print(f"Processed {os.path.basename(batch_file)}: {len(sections)} sections")
    
    # Write the combined content to the output file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n---\n'.join(combined_content))
    
    print(f"Combination complete! Combined {total_sections} sections into: {output_file}")

if __name__ == "__main__":
    combine_batches() 