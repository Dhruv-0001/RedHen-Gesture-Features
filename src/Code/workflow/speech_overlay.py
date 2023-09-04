import cv2
import numpy as np
import librosa
import json

# Function to classify pitch
def classify_pitch(pitch_mean):
    if pitch_mean > 225:
        return "High"
    elif pitch_mean < 100:
        return "Low"
    else:
        return "Medium"

# Specify the frame rate
frame_rate = 29.97  # Adjust this value according to your video's frame rate

# Load video file
video_file = "set/path/to/input/video/input_video.mp4"
cap = cv2.VideoCapture(video_file)

# Get video properties
# frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_width = 640
frame_height = 352

# Load the JSON data
json_file = "set/path/to/json-from-subtitle-segmentation/segmented_subtitles.json"
with open(json_file, "r") as f:
    data = json.load(f)

subtitle_json = "set/path/to/json-from-subtitle-segmentation/segmented_subtitles.json"
with open(subtitle_json, "r") as json_file:
    subtitle_data = json.load(json_file)["results"]["channels"][0]["alternatives"][0]["words"]

# Create speaker change timings
speaker_changes = []
current_speaker = subtitle_data[0]["speaker"]
for word_data in subtitle_data:
    if word_data["speaker"] != current_speaker:
        current_speaker = word_data["speaker"]
        speaker_changes.append((word_data["start"], current_speaker))

# Initialize an index to keep track of the word data
current_word_index = 0

# Load the audio file
audio_file = "path/to/extracted-audio/extracted_audio.wav"
y, sr = librosa.load(audio_file, sr=None)

# Initialize an index to keep track of audio frame position
audio_frame_index = 0

# Define the codec and create a VideoWriter object to save the output
fourcc = cv2.VideoWriter_fourcc(*'mp4v') 
output_video = cv2.VideoWriter('path/to/final-video/final.mp4', fourcc, frame_rate, (frame_width, frame_height))

while True:
    ret, frame = cap.read()

    if not ret:
        break

    # Convert frame to grayscale for audio analysis
    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Calculate audio-related parameters for the current audio frame
    frame_duration = 1.0 / frame_rate
    frame_start_time = audio_frame_index * frame_duration
    frame_end_time = frame_start_time + frame_duration
    frame_audio = y[int(frame_start_time * sr):int(frame_end_time * sr)]

    # Check if frame_audio is not empty to prevent division by zero
    if len(frame_audio) > 0:
        # Calculate speech rate for the current frame
        y_pitch, _ = librosa.piptrack(y=frame_audio, sr=sr)
        pitch = y_pitch.mean(axis=0)
        threshold_ratio = 0.2
        voiced_frames = np.where(pitch > threshold_ratio)[0]
        speech_rate = len(voiced_frames) / (len(frame_audio) / sr)
    else:
        speech_rate = 0.0

    # Calculate pitch variation for the current frame
    pitch_variation = np.std(pitch)

    # Calculate intensity of speech for the current frame
    intensity = np.sqrt(np.mean(frame_gray ** 2))

    # Classify pitch for the current frame
    pitch_classification = classify_pitch(pitch.mean())

    # Overlay parameter values on the frame
    overlay_text1 = f"Speech Rate: {speech_rate:.2f}, Pitch Variation: {pitch_variation:.2f}"
    overlay_text2 = f"Intensity: {intensity:.2f}, Pitch Classification: {pitch_classification}"
    cv2.putText(frame, overlay_text1, (20, frame_height - 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)
    cv2.putText(frame, overlay_text2, (20, frame_height - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)

    if current_word_index < len(data["results"]["channels"][0]["alternatives"][0]["words"]):
        # Get the current word data
        word_data = data["results"]["channels"][0]["alternatives"][0]["words"][current_word_index]

        # Extract the word, start, and end time
        word = word_data["word"]
        start_time = float(word_data["start"])
        end_time = float(word_data["end"])

        # Calculate the frame indices corresponding to start and end times
        start_frame = int(start_time * frame_rate)
        end_frame = int(end_time * frame_rate)

        # Check if the current frame falls within the time range of the word
        current_frame = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
        if current_frame >= start_frame and current_frame <= end_frame:
            # Overlay the word on the frame
            cv2.putText(frame, word, (20, frame_height - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)

    # Check if we have moved to the next word
    if current_frame >= end_frame:
        current_word_index += 1

    current_time = current_frame / frame_rate

    # Find the corresponding speaker ID
    speaker_id = speaker_changes[-1][1] if speaker_changes else 0
    for change_time, speaker in speaker_changes:
        if current_time < change_time:
            speaker_id = speaker
            break

    cv2.putText(frame, f"Speaker ID: {speaker_id}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    output_video.write(frame)

    audio_frame_index += 1

# Release video capture and writer objects
cap.release()
output_video.release()