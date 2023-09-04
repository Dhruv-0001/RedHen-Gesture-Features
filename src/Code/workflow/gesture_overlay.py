import os
import json
import cv2
from moviepy.editor import VideoFileClip, AudioFileClip
import numpy as np
import librosa
import numpy as np
from scipy.signal import find_peaks
from scipy.stats import zscore

file_gesture = "path to gesture file/frames_with_gesture4.npy"
loaded_array = np.load(file_gesture)

json_folder_path = "D:\\GSoC\\1930-2276\\json" # path to json folder
input_video_path = 'D:/GSoC/1930-2276/2014-11-11_0000_US_KNBC_The_Ellen_DeGeneres_Show_1930-2276.mp4' # path to input video
output_video_path = 'D:/GSoC/1930-2276/output-video-gesture5.mp4'  # path to final output video
output_audio_path = 'D:/GSoC/1930-2276/extracted_audio.wav' # path to ectracted audio file

frame_number = 0

cap = cv2.VideoCapture(input_video_path)
# fps = int(cap.get(cv2.CAP_PROP_FPS))
# frame_size = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
fps = 29.97
frame_size = (640,352)

# Define the codec and create VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'mp4v') 
out = cv2.VideoWriter(output_video_path, fourcc, fps, frame_size)

val1=0
val2=0

previous_left_wrist_x_values = [0, 0]
previous_right_wrist_x_values = [0, 0]

Note= False

frame_number = 0
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    json_filename = f'2014-11-11_0000_US_KNBC_The_Ellen_DeGeneres_Show_1930-2276_{frame_number:012d}_keypoints.json'  # Adjust the filename format with the name of the json files
    json_filepath = os.path.join(json_folder_path, json_filename)


    # Read JSON file
    with open(json_filepath, 'r') as json_file:
        data = json.load(json_file)

    # Process each person's keypoints in the frame
    for person in data['people']:
        keypoints = person['pose_keypoints_2d']

        # Compute gesture label, indexing from zero

        right_wrist_y = keypoints[13] 
        right_wrist_x = keypoints[12]

        right_elbow_y = keypoints[10]
        right_elbow_x = keypoints[9]

        left_wrist_y = keypoints[22] 
        left_wrist_x = keypoints[21]

        left_elbow_y = keypoints[19]
        left_elbow_x = keypoints[18]

        neck_y = keypoints[4]
        neck_x = keypoints[3]

        nose_y = keypoints[1]
        nose_x = keypoints[0]

        mouth_y = neck_y - (neck_y - nose_y)/2
        mouth_x = neck_x - (neck_x - nose_x)/2

        Right_Hand_Up = right_elbow_y - right_wrist_y - 12.0
        Left_Hand_Up = left_elbow_y - left_wrist_y - 12.0

        gesture_label1 = ""
        gesture_label2 = ""
        gesture_label3 = ""
        gesture_label4 = ""
        gesture_label5 = ""
        gesture_label6 = ""
        gesture_label7 = ""
        gesture_label8 = ""

        if Right_Hand_Up >=0 and Left_Hand_Up <=0 :
            gesture_label1 += "Right Hand Up "

        if Right_Hand_Up <=0 and Left_Hand_Up >=0  :
            gesture_label2 += "Left Hand Up "

        
        if Right_Hand_Up >=0 and Left_Hand_Up >=0  :
            gesture_label3 += "Both Hand Up "
            gesture_label1 = ""
            gesture_label2 = ""

            

        # if abs(left_wrist_x - right_wrist_x) <= 10.0 and abs(left_wrist_y - right_wrist_y) <= 10.0 :
        #     gesture_label4 += "Both Hands Close"

        
        if abs(left_wrist_x - right_wrist_y) <= 25.0 :
            val1=frame_number


        if abs(left_wrist_x - right_wrist_x) >= 70.0 :
            val2=frame_number
            if val2 - val1 <= 6:
                gesture_label5 += "Expressed"


        if frame_number >= 3:
            if abs(previous_left_wrist_x_values[0] - left_wrist_x) >= 8 :
                gesture_label6 += "Left Arm Moved Horizontally"

        if frame_number >= 3:
            if abs(previous_right_wrist_x_values[0] - right_wrist_x) >= 8 :
                gesture_label7 += "Right Arm Moved Horizontally"

        if frame_number >= 3:
            if abs(previous_right_wrist_x_values[0] - right_wrist_x) >= 8 and abs(previous_left_wrist_x_values[0] - left_wrist_x) >= 8 :
                gesture_label8 += "Right Arm Moved Horizontally"
                gesture_label6 = ""
                gesture_label7 = ""


        previous_left_wrist_x_values.pop(0)  # Remove the oldest value
        previous_left_wrist_x_values.append(left_wrist_x)  # Add the new value

        previous_right_wrist_x_values.pop(0)  
        previous_right_wrist_x_values.append(right_wrist_x)

        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = .65
        font_thickness = 2
        font_color = (255, 255, 255)

        gesture_array =[gesture_label1,gesture_label2,gesture_label3,gesture_label4,gesture_label5,gesture_label6,gesture_label7,gesture_label8]

        if frame_number in loaded_array:
            cv2.putText(frame, 'Hand Gesture Detected', (frame.shape[1] - 350, 20), font, .9, (0, 255, 0), 2, cv2.LINE_AA)
            cv2.putText(frame, 'Type of Gesture', (frame.shape[1] - 350, 45), font, font_scale, (131, 36, 168), font_thickness, cv2.LINE_AA)


            cv2.putText(frame, gesture_label1, (frame.shape[1] - 350, 70), font, font_scale, font_color, font_thickness, cv2.LINE_AA) 
            cv2.putText(frame, gesture_label2, (frame.shape[1] - 350, 90), font, font_scale, font_color, font_thickness, cv2.LINE_AA) 
            cv2.putText(frame, gesture_label3, (frame.shape[1] - 350, 110), font, font_scale, font_color, font_thickness, cv2.LINE_AA) 
            cv2.putText(frame, gesture_label4, (frame.shape[1] - 350, 130), font, font_scale, font_color, font_thickness, cv2.LINE_AA) 
            cv2.putText(frame, gesture_label5, (frame.shape[1] - 350, 150), font, font_scale, font_color, font_thickness, cv2.LINE_AA) 
            cv2.putText(frame, gesture_label6, (frame.shape[1] - 350, 170), font, font_scale, font_color, font_thickness, cv2.LINE_AA) 
            cv2.putText(frame, gesture_label7, (frame.shape[1] - 350, 190), font, font_scale, font_color, font_thickness, cv2.LINE_AA) 
            cv2.putText(frame, gesture_label8, (frame.shape[1] - 350, 210), font, font_scale, font_color, font_thickness, cv2.LINE_AA) 

            if all(gesture == "" for gesture in gesture_array):
                cv2.putText(frame, 'Undefined Gesture', (frame.shape[1] - 350, 250), font, font_scale, (131, 36, 168), font_thickness, cv2.LINE_AA)


        current_time = frame_number / 30.0
        


    out.write(frame)

    frame_number += 1

cap.release()
out.release()
cv2.destroyAllWindows()