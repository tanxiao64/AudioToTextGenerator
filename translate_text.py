import os
import google.generativeai as genai
from typing import List, Tuple
import time
from dotenv import load_dotenv

"""
step4
"""
# Load environment variables from .env file
load_dotenv()

# Input and output file paths
input_file = "/Users/xiao/Documents/mjtt_audio/transcribe_version3/nyc_combined_txt/nyc_processed_text.txt"
  
# Base output directory and filename
output_dir = "/Users/xiao/Documents/mjtt_audio/transcribe_version3/nyc_combined_english_txt"
output_base = "nyc_batch"

def read_text_file(file_path: str) -> str:
    """Read the content of the text file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def split_into_sections(content: str) -> List[str]:
    """Split the content into sections based on '---' delimiter."""
    return [section.strip() for section in content.split('---') if section.strip()]

def estimate_token_count(text: str) -> int:
    """Roughly estimate token count from text."""
    return len(text) // 2

def create_batches(sections: List[str], token_limit: int = 5000) -> List[List[str]]:
    """
    Group sections into batches to optimize API calls.
    Each batch should be under the token_limit.
    """
    batches = []
    current_batch = []
    current_tokens = 0
    
    for section in sections:
        section_tokens = estimate_token_count(section)
        
        # If adding this section exceeds the token limit and we already have sections in the batch
        if current_tokens + section_tokens > token_limit and current_batch:
            batches.append(current_batch)
            current_batch = [section]
            current_tokens = section_tokens
        else:
            current_batch.append(section)
            current_tokens += section_tokens
    
    # Add the last batch if it's not empty
    if current_batch:
        batches.append(current_batch)
    
    return batches

def translate_batch(model, batch: List[str]) -> List[str]:
    """
    Translate a batch of sections while preserving section boundaries.
    Returns a list of translated sections.
    """
    # Create a unique separator that's unlikely to appear in the text
    section_separator = "[SECTION_BREAK]"
    
    # Join sections with the separator for batch processing
    batch_text = f"{section_separator}\n".join(batch)
    
    try:
        prompt = f"""You are a professional translator.

TASK: Translate the Chinese text to English. This is VERY IMPORTANT.

The text contains multiple sections separated by [SECTION_BREAK].

Specific Translation Requirements:
1. TRANSLATE FROM CHINESE TO ENGLISH. Do not keep any Chinese characters in your response.
2. Translate EVERY SINGLE WORD from Chinese to English.
3. Maintain all [SECTION_BREAK] separators exactly as they appear.
4. Do not add or remove any section breaks.
5. If you see Chinese text, you MUST translate it to English.

TEXT TO TRANSLATE (CHINESE → ENGLISH):
{batch_text}

IMPORTANT: Your response must be ENTIRELY in English.
"""
        response = model.generate_content(prompt)
        translation = response.text.strip()
        
        # Remove any explanatory text the model might have added
        if translation.startswith("Translation:"):
            translation = translation[len("Translation:"):].strip()
        
        # Debug: Print a sample of the translation to check if it's in English
        sample_translation = translation[:100] + "..." if len(translation) > 100 else translation
        print(f"Sample translation: {sample_translation}")
        
        # Split the translation back into sections
        translated_sections = translation.split(f"{section_separator}")
        
        # Clean up each section
        translated_sections = [section.strip() for section in translated_sections]
        
        # Ensure we have the same number of sections as in the batch
        if len(translated_sections) != len(batch):
            print(f"Warning: Number of translated sections ({len(translated_sections)}) doesn't match input ({len(batch)})")
            # # If we have fewer sections than expected, we need to pad the list
            # if len(translated_sections) < len(batch):
            #     translated_sections.extend(["[Translation Error]"] * (len(batch) - len(translated_sections)))
            # # If we have more sections than expected, truncate the list
            # else:
            #     translated_sections = translated_sections[:len(batch)]
        
        return translated_sections
    except Exception as e:
        print(f"Error during batch translation: {e}")
        # Return error placeholder for each section in the batch
        return ["[Translation Error]"] * len(batch)

def main():
    # Check for API key
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("Please set your Google API key as an environment variable 'GOOGLE_API_KEY'")
        return

    # Configure the Gemini API
    genai.configure(api_key=api_key)
    
    # Create the Gemini model
    generation_config = {
        "temperature": 0.2,  # Lower temperature for more consistent translations
    }
    
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash", 
        generation_config=generation_config
    )
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Read and process the text
    content = read_text_file(input_file)
    sections = split_into_sections(content)
    total_sections = len(sections)
    
    print(f"Found {total_sections} sections. Creating batches for efficient processing...")
    
    # Create batches of sections
    batches = create_batches(sections)
    total_batches = len(batches)
    
    print(f"Created {total_batches} batches for processing.")
    
    sections_completed = 0
    
    for i, batch in enumerate(batches):
        batch_num = i + 1
        batch_output_file = os.path.join(output_dir, f"{output_base}_{batch_num:03d}.txt")
        
        print(f"Translating batch {batch_num} of {total_batches} ({len(batch)} sections)...")
        
        # Translate the batch
        translated_batch = translate_batch(
            model,
            batch
        )
        
        # Save the translated batch to a separate file
        with open(batch_output_file, 'w', encoding='utf-8') as f:
            f.write('\n---\n'.join(translated_batch))
        
        sections_completed += len(translated_batch)
        print(f"Saved batch {batch_num} to file: {batch_output_file}")
        print(f"Progress: {sections_completed}/{total_sections} sections completed.")
        
        # Add a small delay to avoid potential rate limiting
        if i < total_batches - 1:
            print(f"Sleeping for 10 seconds...")
            time.sleep(10)
    
    print(f"Translation completed! All batches saved to separate files in: {output_dir}")

if __name__ == "__main__":
    main() 