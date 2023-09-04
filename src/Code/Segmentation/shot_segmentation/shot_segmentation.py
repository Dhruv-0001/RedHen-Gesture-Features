# Import necessary functions and classes from the scenedetect library.
from scenedetect import detect, ContentDetector
from scenedetect.video_splitter import split_video_ffmpeg

# Step 1: Detect scenes in the input video file using the ContentDetector.
# ContentDetector() is used to detect scene transitions based on content changes.
scene_list = detect('/path/to/the/input/video.mp4', ContentDetector())

# Step 2: Write scene information to an output text file ('output.txt').
with open('output.txt', 'w') as f:
    for i, scene in enumerate(scene_list):
        # Print scene information to the output file.
        print('    Scene %2d: Start %s / Frame %d, End %s / Frame %d' % (
            i+1,
            scene[0].get_timecode(), scene[0].get_frames(),
            scene[1].get_timecode(), scene[1].get_frames(),), file=f)

# Step 3: Split the video into scenes using FFmpeg and the detected scene list.
# This creates separate video files for each scene.
split_video_ffmpeg('/path/to/the/input/video.mp4', scene_list)
