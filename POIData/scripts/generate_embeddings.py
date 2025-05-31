#!/usr/bin/env python3
"""
POI Embedding Generator Script for TourGuideAI

This script:
1. Reads POI text data from files
2. Generates OpenAI embeddings for each POI
3. Saves the POIs with embeddings as JSON for the iOS app to consume

Requirements:
- Python 3.7+
- openai library (pip install openai)

Usage:
1. Set your OpenAI API key in the environment: export OPENAI_API_KEY=your_key_here
2. Place your POI text files in the POIData directory 
3. Run: python generate_embeddings.py
4. Copy the output file to your app's Documents directory
"""

import os
import json
import glob
import re
import time
import uuid
from typing import List, Dict, Optional, Any
import argparse
import numpy as np
import gzip

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# Configuration
CONFIG = {
    "embedding_model": "text-embedding-3-small",  # OpenAI embedding model name
    "poi_dir": "POIData",                         # Directory containing POI text files
    "output_file": "poi_embeddings.json",         # Output file for embeddings
    "separator": "---",                           # Separator between POIs in text files
    "delay": 0.1,                                 # Delay between API calls (to avoid rate limits)
}

# Point of Interest data model
class PointOfInterest:
    def __init__(self, content: str, location: Optional[Dict[str, float]] = None, embedding: Optional[List[float]] = None):
        self.id = str(uuid.uuid4())
        self.content = content
        self.latitude = location["latitude"] if location else None
        self.longitude = location["longitude"] if location else None
        self.embedding = embedding
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "content": self.content,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "embedding": self.embedding
        }

def extract_location(text: str) -> Optional[Dict[str, float]]:
    """Extract latitude and longitude from text if present."""
    pattern = r"latitude: ([-\d.]+), longitude: ([-\d.]+)"
    match = re.search(pattern, text)
    if match:
        try:
            return {
                "latitude": float(match.group(1)),
                "longitude": float(match.group(2))
            }
        except ValueError:
            return None
    return None

def parse_poi_file(file_path: str) -> List[PointOfInterest]:
    """Parse POI data from a text file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split by separator
        sections = [s.strip() for s in content.split(CONFIG["separator"]) if s.strip()]
        
        pois = []
        for section in sections:
            if not section:
                continue
                
            # Extract location data if present
            location = extract_location(section)
            
            # Create POI object (without embedding for now)
            poi = PointOfInterest(content=section, location=location)
            pois.append(poi)
            
        print(f"Parsed {len(pois)} POIs from {os.path.basename(file_path)}")
        return pois
    
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return []

def generate_embedding(text: str, client: OpenAI) -> List[float]:
    """Generate embedding for a text using OpenAI API."""
    try:
        response = client.embeddings.create(
            input=text,
            model=CONFIG["embedding_model"]
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Error generating embedding: {e}")
        return []

def generate_embeddings_for_pois(pois: List[PointOfInterest]) -> List[PointOfInterest]:
    """Generate embeddings for each POI."""
    client = OpenAI()
    
    processed_pois = []
    for i, poi in enumerate(pois):
        if i % 5 == 0:
            print(f"Processing POI {i+1}/{len(pois)}")
        
        try:
            # Generate embedding
            embedding = generate_embedding(poi.content, client)
            
            # Create new POI with embedding
            processed_poi = PointOfInterest(
                content=poi.content,
                location={"latitude": poi.latitude, "longitude": poi.longitude} if poi.latitude and poi.longitude else None,
                embedding=embedding
            )
            processed_pois.append(processed_poi)
            
            # Sleep to avoid API rate limits
            time.sleep(CONFIG["delay"])
            
            if (i+1) % 10 == 0:
                print(f"Completed {i+1}/{len(pois)} POIs")
                
        except Exception as e:
            print(f"Error processing POI: {e}")
            # Add POI without embedding
            processed_pois.append(poi)
    
    return processed_pois

def optimize_embedding(embedding: List[float], decimals: int = 2) -> List[float]:
    """Quantize embedding values to reduce size while maintaining accuracy."""
    return [round(x, decimals) for x in embedding]

def compress_json(data: str) -> bytes:
    """Compress JSON string using gzip."""
    return gzip.compress(data.encode('utf-8'))

def save_embeddings_to_json(pois: List[PointOfInterest], output_path: str, compress: bool = False, decimals: int = 2) -> bool:
    """Save POIs with embeddings to a JSON file with optional compression."""
    try:
        # Optimize the data structure and quantize embeddings
        pois_data = []
        for poi in pois:
            optimized_poi = {
                "i": poi.id,  # shorter key names
                "c": poi.content,
                "e": optimize_embedding(poi.embedding, decimals) if poi.embedding else None
            }
            # Only include location if it exists
            if poi.latitude is not None and poi.longitude is not None:
                optimized_poi["l"] = [poi.latitude, poi.longitude]
            pois_data.append(optimized_poi)

        # Convert to JSON
        json_str = json.dumps(pois_data, ensure_ascii=False, separators=(',', ':'))  # Remove whitespace

        if compress:
            # Save compressed file
            compressed_data = compress_json(json_str)
            output_path_gz = output_path + '.gz'
            with open(output_path_gz, 'wb') as f:
                f.write(compressed_data)
            print(f"Successfully saved compressed embeddings to {output_path_gz}")
            print(f"Compressed file size: {len(compressed_data) / 1024:.2f} KB")
        else:
            # Save uncompressed file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(json_str)
            print(f"Successfully saved embeddings to {output_path}")
            print(f"File size: {len(json_str) / 1024:.2f} KB")
        
        return True
    except Exception as e:
        print(f"Error saving embeddings: {e}")
        return False

def main():
    # parser = argparse.ArgumentParser(description="Generate embeddings for POI data")
    # parser.add_argument("--poi-dir", help="Directory containing POI text files", default=CONFIG["poi_dir"])
    # parser.add_argument("--output", help="Output JSON file", default=CONFIG["output_file"])
    # args = parser.parse_args()
    poi_dir = "/Users/xiao/workspace/tourGuideAi/tourGuideAi/POIData/data/"
    output_file_path = "/Users/xiao/workspace/tourGuideAi/tourGuideAi/POIData/output/nyc_batch_019_embeddings.json"

    # Check for OpenAI API key
    if not os.environ.get("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set")
        print("Set it with: export OPENAI_API_KEY=your_key_here")
        return
    
    print("=== POI Embedding Generator ===")
    
    # Get POI text files
    if not os.path.exists(poi_dir):
        print(f"Error: POI directory {poi_dir} not found")
        return
    
    poi_files = glob.glob(os.path.join(poi_dir, "*.txt"))
    if not poi_files:
        print(f"Error: No text files found in {poi_dir}")
        return
    
    print(f"Found {len(poi_files)} POI data files")
    
    # Parse all POI files
    all_pois = []
    for file_path in poi_files:
        pois = parse_poi_file(file_path)
        all_pois.extend(pois)
    
    if not all_pois:
        print("Error: No POIs found in the data files")
        return
    
    print(f"Parsed a total of {len(all_pois)} POIs")
    
    # Generate embeddings
    print("Generating embeddings (this may take a while)...")
    processed_pois = generate_embeddings_for_pois(all_pois)
    
    # Save embeddings to JSON (both compressed and uncompressed versions)
    success = save_embeddings_to_json(processed_pois, output_file_path, compress=False, decimals=8)
    
    if success:
        print("\n=== Embedding Generation Complete ===")
        print(f"Generated embeddings for {len(processed_pois)} POIs")
        print("\nNext Steps:")
        print("1. Copy the .gz file to your iOS app's Documents directory")
        print("2. In your app, decompress the file before use")
        print("3. Update your app's loading code to handle the optimized format")
    else:
        print("Embedding generation failed")

if __name__ == "__main__":
    main() 