from scenedetect import detect, ContentDetector
from scenedetect.video_splitter import split_video_ffmpeg

# It creates a list of segmented scenes
scene_list = detect('/path to input video/input_video.mp4', ContentDetector())


with open('output.txt', 'w') as f:
    for i, scene in enumerate(scene_list):
            print('    Scene %2d: Start %s / Frame %d, End %s / Frame %d' % (
                i+1,
                scene[0].get_timecode(), scene[0].get_frames(),
                scene[1].get_timecode(), scene[1].get_frames(),), file=f)
    
split_video_ffmpeg('/path to output file/output.mp4', scene_list)


