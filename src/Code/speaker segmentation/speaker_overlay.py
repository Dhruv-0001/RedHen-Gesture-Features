import cv2
import json
from moviepy.editor import VideoFileClip

# Load JSON subtitle data
subtitle_json = "D:/GSoC/Output/Phrase/subtitle.json"
with open(subtitle_json, "r") as json_file:
    subtitle_data = json.load(json_file)["results"]["channels"][0]["alternatives"][0]["words"]

# Create speaker change timings
speaker_changes = []
current_speaker = subtitle_data[0]["speaker"]
for word_data in subtitle_data:
    if word_data["speaker"] != current_speaker:
        current_speaker = word_data["speaker"]
        speaker_changes.append((word_data["start"], current_speaker))

# Open the video capture
video = "D:/GSoC/Output/Gesture/Gesture.mp4"
cap = cv2.VideoCapture(video)

# Define the codec and create a VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter("new.avi", fourcc, 30, (int(cap.get(3)), int(cap.get(4))))

# Create a video clip using MoviePy
video_clip = VideoFileClip(video)

# Iterate through frames and overlay speaker ID
frame_number = 0
for frame in video_clip.iter_frames(fps=30, dtype="uint8"):
    # Get the time for the current frame
    current_time = frame_number / 30.0
    
    # Find the corresponding speaker ID
    speaker_id = speaker_changes[-1][1] if speaker_changes else 0
    for change_time, speaker in speaker_changes:
        if current_time < change_time:
            speaker_id = speaker
            break
    
    cv2.putText(frame, f"Speaker ID: {speaker_id}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    # Write the frame to the output video
    out.write(frame)
    
    frame_number += 1

# Release the capture and writer objects
cap.release()
out.release()


print('done!')