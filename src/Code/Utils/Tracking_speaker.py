import os
import json
import math

def calculate_distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def track_persons(json_folder, threshold=5):
    json_files = [file for file in os.listdir(json_folder) if file.endswith('.json')]
    person_id_counter = 1
    persons_data = {}

    for frame_file in sorted(json_files):
        frame_path = os.path.join(json_folder, frame_file)
        with open(frame_path, 'r') as f:
            frame_data = json.load(f)

        # Extract neck keypoints (assuming it's the 1st keypoint for each person)
        neck_keypoints = [person['pose_keypoints_2d'][3:5] for person in frame_data['people']]

        for person_idx, neck_keypoint in enumerate(neck_keypoints):
            closest_person_id = None
            min_distance = threshold

            for person_id, person_data in persons_data.items():
                if person_data['tracked'] == False:
                    distance = calculate_distance(neck_keypoint[0], neck_keypoint[1],
                                                  person_data['last_neck'][0], person_data['last_neck'][1])
                    if distance < min_distance:
                        min_distance = distance
                        closest_person_id = person_id

            if closest_person_id is not None:
                persons_data[closest_person_id]['tracked'] = True
                persons_data[closest_person_id]['last_neck'] = neck_keypoint
            else:
                new_person_id = person_id_counter
                person_id_counter += 1
                persons_data[new_person_id] = {'tracked': True, 'last_neck': neck_keypoint}
                closest_person_id = new_person_id

            frame_data['people'][person_idx]['person_id'] = [closest_person_id]

        # Reset the tracking status for the next frame
        for person_id, person_data in persons_data.items():
            person_data['tracked'] = False

        # Save the modified JSON back to the file
        with open(frame_path, 'w') as f:
            json.dump(frame_data, f)

if __name__ == "__main__":
    # Replace 'json_folder_path' with the path to your folder containing JSON files.
    json_folder_path = 'D:/GSoC/sample'
    track_persons(json_folder_path)

