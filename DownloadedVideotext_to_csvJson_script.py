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

# *** IMPORTANT: RENAME YOUR UPLOADED FILE TO MATCH THIS NAME ***
OUTPUT_FILENAME = "/GCP - Professional Data Engineer Certification Exam updated Questions & Answers -Part 1 - Anything2Cloud (1080p, h264) (1).mp4" 

# Note: YOUTUBE_URL is no longer used, but kept for context if you switch back.
# YOUTUBE_URL = "https://www.youtube.com/watch?v=qmA4dm9XF-0&list=PLSC_1aEzNDQsWdq1q6oz4E9ibzniFqiDm&index=3" 

# Sample rate: Check for text changes every 1 second
SAMPLE_RATE_SECONDS = 1
# Threshold for text change: 
TEXT_CHANGE_THRESHOLD = 0.5 
OUTPUT_CSV = "video_text_data_video3.csv"
OUTPUT_JSON = "video_text_data_video3.json"

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
        return 1.0 
    
    dist = levenshtein_distance(text1, text2)
    max_len = max(len(text1), len(text2))
    return dist / max_len if max_len > 0 else 1.0

# ----------------------------------------------------------------------
# 4. DOWNLOAD THE VIDEO (SKIPPED - USING UPLOADED FILE)
# ----------------------------------------------------------------------

# --- SKIPPING DOWNLOAD SECTION ---
# The video file is assumed to be uploaded and available as OUTPUT_FILENAME.
# You must ensure the file is named "downloaded_video.mp4" in the Colab file explorer.
# --- SKIPPING DOWNLOAD SECTION ---

# ----------------------------------------------------------------------
# 5. DYNAMIC VIDEO PROCESSING AND OCR
# ----------------------------------------------------------------------

# Open the video file
# Note: This is the first step that uses your uploaded file.
cap = cv2.VideoCapture(OUTPUT_FILENAME)

# Check if the file was opened successfully
if not cap.isOpened():
    print(f"FATAL ERROR: Could not open the file '{OUTPUT_FILENAME}'.")
    print("Please ensure you have uploaded the file and it is named exactly 'downloaded_video.mp4'.")
    # No need to remove file if it wasn't opened/created by us
    exit(1)

# Get video properties
fps = cap.get(cv2.CAP_PROP_FPS)
frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
total_seconds = int(frame_count / fps) # Estimate duration from frame count

if fps == 0:
    print("Error: Could not read video FPS. Video file might be corrupted.")
    cap.release()
    exit(1)

print(f"Video file opened successfully. Total duration: {total_seconds} seconds.")

# Create a list of frames to sample based on the SAMPLE_RATE_SECONDS
frames_to_sample = [int(i * fps) for i in range(1, total_seconds, SAMPLE_RATE_SECONDS)]

results = []
last_text_saved = ""

print(f"Scanning the video at {SAMPLE_RATE_SECONDS}-second intervals...")
    
# Process each required frame
for frame_index in tqdm(frames_to_sample, desc="Processing Frames"):
    
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
    ret, frame = cap.read()
    
    if ret:
        # Convert the frame to grayscale for better OCR performance
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Use Tesseract to extract text
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
    
# Clean up: Since you manually uploaded the file, we skip deleting it.
# If you want to delete it after processing, uncomment the lines below.
# if os.path.exists(OUTPUT_FILENAME):
#     os.remove(OUTPUT_FILENAME)
#     print(f"Clean up complete. Uploaded video file '{OUTPUT_FILENAME}' removed.")
    
print("\nProcessing finished! Look for the .csv and .json files in the Colab file explorer to download your data.")
