###################################################################################################################
# This script combines multiple frames into hyper-images and saves them as JPG files to be used with YOLOv8.
# Before running this script, 1_manage_files.py must be run to organize the images and labels.
# Ensure that the config.json file is in the same directory as this script, and that it contains the base_dir key.
###################################################################################################################

import os
import cv2
import numpy as np
import shutil
import json
from tqdm import tqdm

# Load configuration
def load_config():
    with open('config.json', 'r') as config_file:
        return json.load(config_file)

config = load_config()
BASE_DIR = config.get("base_dir", "")

def get_clips(image_dir):
    """
    Separates the images into clips based on the file name
    :param image_dir: Path to the directory containing the images
    :return: clips: Dictionary with the images separated by the clip keys
    """
    clips = {}
    image_files = sorted([f for f in os.listdir(image_dir) if f.endswith('.jpg')])
    for image_file in image_files:
        split = image_file.split('_')
        key = '_'.join(split[:-1])
        if key not in clips:
            clips[key] = []
        clips[key].append(image_file)
    return clips

def make_hyper_image(image_paths, mode, n):
    """
    Combines multiple frames into a hyper image. Assumes all the images are single-channel grayscale.

    Parameters:
        image_paths (list): Paths of all the images in the sequence.
        mode (str): Mode of operation ('stack', 'diff', 'mean').
        n (int): Total number of frames to combine (must be odd).

    Returns:
        List of hyper images as tuples (filename, hyper_image).
    """
    assert n % 2 == 1, "n must be an odd number."
    half_n = n // 2  # Frames on each side of the center frame

    total_frames = len(image_paths)

    hyper_images = []
    mean_image = None
    if mode == 'mean':
        mean_image = None
        for image_path in image_paths:
            image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE).astype(np.float32) / 255.0
            if image is None:
                print(f"Warning: Failed to load image {image_path}. Skipping this sequence.")
                break
            if mean_image is None:
                mean_image = image / total_frames
            else:
                mean_image += image / total_frames

    for i in range(half_n, total_frames - half_n):
        frames = []
        for j in range(i - half_n, i + half_n + 1):
            image_path = image_paths[j]
            image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE).astype(np.float32) / 255.0

            if image is None:
                print(f"Warning: Failed to load image {image_path}. Skipping this sequence.")
                break

            frames.append(image)

        if len(frames) != n:
            continue

        if mode == 'stack':
            hyper_image = np.stack(frames, axis=-1)
        elif mode == 'diff':
            central_frame = frames[half_n]
            differences = [(frame - central_frame) / 2 + 0.5 for frame in frames]
            differences[half_n] = central_frame
            hyper_image = np.stack(differences, axis=-1)
        elif mode == 'mean':
            differences = [(frame - mean_image) / 2 + 0.5 for frame in frames]
            differences[half_n] = frames[half_n]
            hyper_image = np.stack(differences, axis=-1)
        else:
            raise ValueError("Invalid mode. Choose from 'stack', 'diff', 'mean'.")

        hyper_images.append((image_paths[i].split('/')[-1], hyper_image))

    return hyper_images

def save_hyper_image_jpg(save_dir, hyper_images):
    """
    Renders hyper images by overlaying channels with distinct colors and saves them as JPGs.

    Parameters:
        save_dir (str): Directory to save rendered images.
        hyper_images (list): List of tuples containing filenames and hyper images.

    Returns:
        None
    """
    os.makedirs(save_dir, exist_ok=True)

    for filename, hyper_image in hyper_images:
        base_filename = os.path.splitext(filename)[0]

        f = hyper_image.shape[-1]

        if f == 1:
            central_frame = (hyper_image[:, :, 0] * 255).astype(np.uint8)
            rendered_image = cv2.cvtColor(central_frame, cv2.COLOR_GRAY2BGR)
        elif f == 3:
            rendered_image = cv2.cvtColor((hyper_image * 255).astype(np.uint8), cv2.COLOR_RGB2BGR)
        else:
            central_frame = (hyper_image[:, :, f // 2] * 255).astype(np.uint8)
            rendered_image = cv2.cvtColor(central_frame, cv2.COLOR_GRAY2BGR)

        save_path = os.path.join(save_dir, f"{base_filename}.jpg")
        cv2.imwrite(save_path, rendered_image, [int(cv2.IMWRITE_JPEG_QUALITY), 95])

def copy_labels(label_dir, save_dir, image_files):
    """
    Copies corresponding label files to the new directory.

    Parameters:
        label_dir (str): Path to the original labels' directory.
        save_dir (str): Path to the destination labels directory.
        image_files (list): List of image filenames (without extensions).

    Returns:
        None
    """
    os.makedirs(save_dir, exist_ok=True)
    for image_file in image_files:
        label_file = os.path.splitext(image_file)[0] + ".txt"
        src_path = os.path.join(label_dir, label_file)
        dest_path = os.path.join(save_dir, label_file)
        if os.path.exists(src_path):
            shutil.copy(src_path, dest_path)
        else:
            print(f"Warning: Label file {label_file} does not exist.")

def save_hyper_image_npy(save_dir, hyper_images):
    """
    Saves hyper images as numpy arrays.

    Parameters:
        save_dir (str): Directory to save numpy arrays.
        hyper_images (list): List of tuples containing filenames and hyper images.

    Returns:
        None
    """
    os.makedirs(save_dir, exist_ok=True)
    for filename, hyper_image in hyper_images:
        base_filename = os.path.splitext(filename)[0]
        save_path = os.path.join(save_dir, f"{base_filename}.npy")
        np.save(save_path, hyper_image)

if __name__ == '__main__':
    directories = ['cfc_train_2', 'cfc_val_2', 'cfc_channel_test_2']
    modes = ['stack', 'diff', 'mean']
    ns = [3]

    for directory in directories:
        image_dir = os.path.join(BASE_DIR, directory, "images")
        label_dir = os.path.join(BASE_DIR, directory, "labels")
        clips = get_clips(image_dir)

        for mode in modes:
            for n in ns:
                new_image_dir = os.path.join(BASE_DIR, f"{directory}_{mode}_{n}", "images")
                new_label_dir = os.path.join(BASE_DIR, f"{directory}_{mode}_{n}", "labels")

                for key, clip in tqdm(clips.items(), desc=f"Processing {directory = }, {mode = }, {n = }"):
                    image_paths = [os.path.join(image_dir, f) for f in clip]

                    hyper_images = make_hyper_image(image_paths, mode, n)
                    save_hyper_image_jpg(new_image_dir, hyper_images)

                    image_files = [image[0] for image in hyper_images]
                    copy_labels(label_dir, new_label_dir, image_files)
