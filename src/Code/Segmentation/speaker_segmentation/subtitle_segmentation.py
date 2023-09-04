def split_subtitles_by_shots(scene_list_file, annotation_file):
    # Read the scene list file
    with open(scene_list_file, 'r') as f:
        scene_list = f.readlines()

    # Read the annotation file
    with open(annotation_file, 'r') as f:
        subtitles = f.readlines()

    # Remove newline characters from each line in the scene list
    scene_list = [line.strip() for line in scene_list]

    # Initialize variables
    shots = []
    current_shot = []
    shot_index = 0

    # Iterate through the subtitles
    for subtitle in subtitles:
        if ' --> ' in subtitle:
            # Check if the current subtitle time belongs to the next shot
            start_time = subtitle.split(' --> ')[0]
            if start_time in scene_list:
                # Add the previous shot to the shots list
                if current_shot:
                    shots.append(current_shot)
                    current_shot = []

                # Increment the shot index
                shot_index += 1

        # Add the subtitle line to the current shot
        current_shot.append(subtitle)

    # Add the last shot to the shots list
    if current_shot:
        shots.append(current_shot)

    # Write the split subtitles to separate files
    for i, shot in enumerate(shots):
        shot_filename = f"shot_{i + 1}_srt.srt"
        with open(shot_filename, 'w') as f:
            f.writelines(shot)



scene_list_file = 'path to scene list produced during video segmentation/output.txt' 
annotation_file = 'Whisper_AI/Audio_to_Text/output_audio.srt'   

split_subtitles_by_shots(scene_list_file, annotation_file)
