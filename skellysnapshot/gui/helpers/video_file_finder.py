import os

def get_video_paths(folder_path):
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv']
    video_paths = []

    for file in os.listdir(folder_path):
        if any(file.endswith(ext) for ext in video_extensions):
            video_paths.append(os.path.join(folder_path, file))

    return video_paths