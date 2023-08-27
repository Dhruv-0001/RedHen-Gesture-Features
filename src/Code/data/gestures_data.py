from typing import Dict, List, Tuple
import pandas as pd
import numpy as np
from config import REQUIRED_KEYPOINTS
from pose.openpose_base import BODY_25_JOINTS


def get_hand_movement_times(filepath: str) -> List[Tuple]:
    """
    Load CSV file and extract hand movement time ranges. Must have columns 'Begin Time - msec' and 'End Time - msec'.
    """
    df = pd.read_csv(filepath)
    columns = list(df.columns)
    b_ind = columns.index('Begin Time - msec')
    e_ind = columns.index('End Time - msec')
    beg_end_times = list(zip(df.iloc[:, b_ind], df.iloc[:, e_ind]))
    return beg_end_times


def generate_dummy_keypoints() -> Dict:
    """
    Generate dummy keypoints for frames with less than Max Persons. Dense layers require all frames to have same dimensions.
    """
    dummy = {}
    for joint in BODY_25_JOINTS:
        dummy[joint] = [-1.0, -1.0, -1.0]
    return dummy


def arrange_train_data(keypoints: Dict, beg_end_times: List[Tuple], fps: float, MAX_PERSONS: int) -> Dict:
    """
    Arrange data into frames. Add gestures present or not based on time ranges. Generate each frame and also, add dummy when necessary.
    """
    data = {}
    for key in keypoints.keys():
        persons = list(keypoints[key].keys())
        persons.remove("start_frame")
        persons.remove("end_frame")
        count_persons = len(persons)
        gestures_xy = []
        start_frame, end_frame = keypoints[key]["start_frame"], keypoints[key]["end_frame"]
        start_time_ms = start_frame/fps*1000
        end_time_ms = end_frame/fps*1000
        for per_ind in range(1, count_persons+1):
            per_str = str(per_ind)
            gestures_xy.append(keypoints[key][per_str]["person_keypoints"])
        # dummy to always have MAX_PERSONS (training to be done in matrices (Required_keypoints x Max_persons x window))
        dummy = generate_dummy_keypoints()
        dummy_frames_list = []
        for _ in range(start_frame, end_frame+1):
            dummy_frames_list.append(dummy)

        for i in range(MAX_PERSONS - count_persons):
            gestures_xy.append(dummy_frames_list)

        frame_division_gestures = list(zip(*gestures_xy))
        frames_dict = {}
        for i, frame in enumerate(frame_division_gestures):
            frames_dict[str(start_frame + i)] = {
                "frames": frame,
                "gesture": False
            }
        data[key] = frames_dict

        for be_time in beg_end_times:
            if be_time[0] > end_time_ms or be_time[1] < start_time_ms:
                continue
            elif be_time[0] < start_time_ms and be_time[1] < end_time_ms:
                bt = start_time_ms
                et = be_time[1]
            elif be_time[0] > start_time_ms and be_time[1] < end_time_ms:
                bt = be_time[0]
                et = be_time[1]
            elif be_time[0] < start_time_ms and be_time[1] > end_time_ms:
                bt = start_time_ms
                et = end_time_ms
            elif be_time[0] > start_time_ms and be_time[1] > end_time_ms:
                bt = be_time[0]
                et = end_time_ms
            # Now using bt and et, find the frame indices with gesture
            begin_at_frame_ind = int(bt*fps/1000+0.5)
            no_of_frames = int((et-bt)*fps/1000+0.5)
            end_at_frame_ind = begin_at_frame_ind + no_of_frames
            if end_at_frame_ind > int((list(data[key].keys()))[-1]):
                end_at_frame_ind = int((list(data[key].keys()))[-1])

            for frame_no in range(begin_at_frame_ind, end_at_frame_ind+1):
                data[key][str(frame_no)]["gesture"] = True

    return data


def arrange_detect_data(keypoints: Dict, MAX_PERSONS: int) -> Dict:
    """
    Same as train data. But not gesture in this case
    """
    data = {}
    for key in keypoints.keys():
        persons = list(keypoints[key].keys())
        persons.remove("start_frame")
        persons.remove("end_frame")
        count_persons = len(persons)
        gestures_xy = []
        start_frame, end_frame = keypoints[key]["start_frame"], keypoints[key]["end_frame"]
        for per_ind in range(1, count_persons+1):
            per_str = str(per_ind)
            gestures_xy.append(keypoints[key][per_str]["person_keypoints"])
        # dummy to always have MAX_PERSONS (training to be done in matrices (Required_keypoints x Max_persons x window))
        dummy = generate_dummy_keypoints()
        dummy_frames_list = []
        for _ in range(start_frame, end_frame+1):
            dummy_frames_list.append(dummy)

        for i in range(MAX_PERSONS - count_persons):
            gestures_xy.append(dummy_frames_list)

        frame_division_gestures = list(zip(*gestures_xy))
        frames_dict = {}
        for i, frame in enumerate(frame_division_gestures):
            frames_dict[str(start_frame + i)] = {
                "frames": frame,
                "gesture": False
            }
        data[key] = frames_dict

    return data


def generate_npy_data_train(data: Dict, WINDOW_SIZE: int, ):
    """
    Arrange into windows. Form Numpy data.
    """
    npy_data = []
    for key in data.keys():
        for frame in list(data[key].keys())[:-WINDOW_SIZE+1]:
            windows = []
            target = str(int(frame)+WINDOW_SIZE-1)
            for i in range(WINDOW_SIZE):
                window = []
                frame_no = str(int(frame)+i)
                for person in data[key][frame_no]["frames"]:
                    person_keypoints = []
                    for keypoints in REQUIRED_KEYPOINTS:
                        person_keypoints.extend(person[keypoints][:2])
                    window.append(np.array(person_keypoints, dtype=np.float16))
                windows.append(np.array(window, dtype=np.float16))
            npy_data.append([int(target), np.array(windows, dtype=np.float16),
                            int(data[key][target]["gesture"])])
    npy_data = np.array(npy_data, dtype=object)
    return npy_data


def generate_npy_data_detect(data: Dict, WINDOW_SIZE: int, ):
    """
    Arrange into windows. Form Numpy data. No gesture data.
    """
    npy_data = []
    for key in data.keys():
        for frame in list(data[key].keys())[:-WINDOW_SIZE+1]:
            windows = []
            target = str(int(frame)+WINDOW_SIZE-1)
            for i in range(WINDOW_SIZE):
                window = []
                frame_no = str(int(frame)+i)
                for person in data[key][frame_no]["frames"]:
                    person_keypoints = []
                    for keypoints in REQUIRED_KEYPOINTS:
                        person_keypoints.extend(person[keypoints][:2])
                    window.append(np.array(person_keypoints, dtype=np.float16))
                windows.append(np.array(window, dtype=np.float16))
            npy_data.append([int(target), np.array(windows, dtype=np.float16)])
    npy_data = np.array(npy_data, dtype=object)
    return npy_data