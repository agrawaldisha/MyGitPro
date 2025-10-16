# ----------------------------------------------------------------------
# 1. SETUP: INSTALL DEPENDENCIES
# ----------------------------------------------------------------------

# Install tesseract (the OCR engine) system-wide
!apt-get install -y tesseract-ocr

# Install Python libraries (yt-dlp for download, OpenCV for frames, pytesseract for OCR, pandas for output)
!pip install pytesseract opencv-python pandas yt-dlp tqdm Levenshtein

import cv2
import pytesseract
import pandas as pd
import time
import os
import re
from yt_dlp import YoutubeDL
from tqdm import tqdm
from Levenshtein import distance as levenshtein_distance

# Set the path for tesseract, necessary for Colab environment
pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'

print("Setup complete. Starting video processing...")
print("--------------------------------------------------")

# ----------------------------------------------------------------------
# 2. CONFIGURATION
# ----------------------------------------------------------------------
# *** YOUR YOUTUBE URL IS SET HERE ***
YOUTUBE_URL = ""

OUTPUT_FILENAME = "downloaded_video.mp4"
# Sample rate: Check for text changes every 1 second
SAMPLE_RATE_SECONDS = 1
# Threshold for text change: 
# The Levenshtein distance measures the number of single-character edits 
# required to change one word into the other. 
# A high difference means a significant text change (i.e., a new slide).
TEXT_CHANGE_THRESHOLD = 0.5 
OUTPUT_CSV = "video_text_data.csv"
OUTPUT_JSON = "video_text_data.json"

# ----------------------------------------------------------------------
# 3. HELPER FUNCTIONS
# ----------------------------------------------------------------------

def normalize_text(text):
    """Clean and normalize text for reliable comparison."""
    # Remove all non-alphanumeric characters (except spaces) and convert to lowercase
    text = re.sub(r'[^a-z0-9\s]', '', text.lower())
    # Remove extra spaces
    return " ".join(text.split()).strip()

def calculate_similarity(text1, text2):
    """Calculates the normalized Levenshtein distance between two strings."""
    if not text1 or not text2:
        return 1.0 # Treat empty text as completely different
    
    # Calculate Levenshtein distance
    dist = levenshtein_distance(text1, text2)
    # Normalize distance by the length of the longer string
    max_len = max(len(text1), len(text2))
    return dist / max_len if max_len > 0 else 1.0

# ----------------------------------------------------------------------
# 4. DOWNLOAD THE VIDEO (FIX APPLIED HERE)
# ----------------------------------------------------------------------

ydl_opts = {
    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
    'outtmpl': OUTPUT_FILENAME,
    'quiet': True,
    'noplaylist': True,
    # REMOVED: 'max_filesize': '500m' -> This caused the 'int' and 'str' comparison error.
}

try:
    with YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(YOUTUBE_URL, download=True)
        video_title = info_dict.get('title', 'Unknown Title')
        video_duration = info_dict.get('duration', 0)
        print(f"Video downloaded: '{video_title}'")
        print(f"Duration: {video_duration} seconds.")

except Exception as e:
    # Added clean-up here just in case a partial file was created
    if os.path.exists(OUTPUT_FILENAME):
        os.remove(OUTPUT_FILENAME)
        
    print(f"Error downloading video: {e}")
    # Exit with a non-zero status code to indicate failure
    exit(1)

# ----------------------------------------------------------------------
# 5. DYNAMIC VIDEO PROCESSING AND OCR
# ----------------------------------------------------------------------

# Open the video file
cap = cv2.VideoCapture(OUTPUT_FILENAME)
if not cap.isOpened():
    # This block should now be unreachable if the download was successful
    print(f"Error: Could not open video file {OUTPUT_FILENAME}")
    os.remove(OUTPUT_FILENAME)
    exit(1)

# Get video properties
fps = cap.get(cv2.CAP_PROP_FPS)
if fps == 0:
    print("Error: Could not read video FPS.")
    cap.release()
    os.remove(OUTPUT_FILENAME)
    exit(1)

# Ensure video_duration is an integer for range function
video_duration = int(video_duration) 
frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
total_seconds = video_duration # Use the duration from info_dict which is more reliable

# Create a list of frames to sample based on the SAMPLE_RATE_SECONDS
# We check every 'SAMPLE_RATE_SECONDS' starting from 1 second mark
frames_to_sample = [int(i * fps) for i in range(1, total_seconds, SAMPLE_RATE_SECONDS)]

results = []
last_text_saved = ""

print(f"Scanning the video at {SAMPLE_RATE_SECONDS}-second intervals...")
    
# Process each required frame
for frame_index in tqdm(frames_to_sample, desc="Processing Frames"):
    # Set the frame position
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
    
    # Read the frame
    ret, frame = cap.read()
    
    if ret:
        # Convert the frame to grayscale for better OCR performance
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Use Tesseract to extract text
        # '--psm 6' is good for a single uniform block of text
        raw_text = pytesseract.image_to_string(gray_frame, config='--psm 6')
        
        # Normalize the current text for comparison
        current_text_normalized = normalize_text(raw_text)
        
        # Check if the text is significantly different from the last saved text
        similarity = calculate_similarity(last_text_saved, current_text_normalized)

        # If the extracted text is long enough AND the difference is high (meaning a new slide)
        if len(current_text_normalized) > 20 and similarity > TEXT_CHANGE_THRESHOLD:
            
            # Calculate the time in HH:MM:SS format
            time_seconds = frame_index / fps
            time_str = time.strftime('%H:%M:%S', time.gmtime(time_seconds))
            
            # Store the result
            results.append({
                "time_stamp": time_str,
                "text_content": raw_text.strip().replace('\n', ' ')
            })
            
            # Update the last saved text
            last_text_saved = current_text_normalized

cap.release()

print("\nOCR extraction complete.")

# ----------------------------------------------------------------------
# 6. EXPORT DATA TO CSV (EXCEL) AND JSON
# ----------------------------------------------------------------------

if results:
    # Create a DataFrame
    df = pd.DataFrame(results)
    
    # Export to CSV (for Excel)
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"✅ Data exported to Excel-ready CSV: {OUTPUT_CSV}")

    # Export to JSON
    df.to_json(OUTPUT_JSON, orient='records', indent=4)
    print(f"✅ Data exported to JSON: {OUTPUT_JSON}")
else:
    print("❌ No significant text changes (slides) were detected in the video.")
    
# Clean up downloaded video file
if os.path.exists(OUTPUT_FILENAME):
    os.remove(OUTPUT_FILENAME)
    print(f"Clean up complete. Video file '{OUTPUT_FILENAME}' removed.")
    
print("\nProcessing finished! Look for the .csv and .json files in the Colab file explorer (folder icon on the left) to download your data.")
