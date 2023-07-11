from scenedetect import detect, ContentDetector
from scenedetect.video_splitter import split_video_ffmpeg

scene_list = detect('D:/GSoC/Bethenny_Frankel_01.mp4', ContentDetector())

with open('output.txt', 'w') as f:
    for i, scene in enumerate(scene_list):
            print('    Scene %2d: Start %s / Frame %d, End %s / Frame %d' % (
                i+1,
                scene[0].get_timecode(), scene[0].get_frames(),
                scene[1].get_timecode(), scene[1].get_frames(),), file=f)
    
split_video_ffmpeg('D:/GSoC/Bethenny_Frankel_01.mp4', scene_list)


# import os
# from scenedetect import detect, ContentDetector
# from scenedetect.video_splitter import split_video_ffmpeg

# input_file = 'full dataset 30 videos yao and suwei/30_videos/2014-11-11_0000_US_KNBC_The_Ellen_DeGeneres_Show_1930-2276.mp4'
# output_directory = 'output_folder'

# if not os.path.exists(output_directory):
#     os.makedirs(output_directory)

# scene_list = detect(input_file, ContentDetector())

# split_video_ffmpeg(input_file, scene_list, output_directory=output_directory)

