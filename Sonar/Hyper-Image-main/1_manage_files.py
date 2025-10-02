###################################################################################################################
# This script prepares for hyper-image conversion by renaming files, and saving labels in YOLO format.
# It also separates the channels of the images and labels for each test set.
# This script should be run before running 2_make_hyper_image.py.
# Ensure that the config.json file is in the same directory as this script, and that it contains the base_dir key.
###################################################################################################################

import os
import json
import shutil
import cv2
from tqdm import tqdm

# Load configuration
def load_config():
    with open('config.json', 'r') as config_file:
        return json.load(config_file)

config = load_config()
BASE_DIR = config.get("base_dir", "")

def clear_subdirectories(directory):
    """
    Delete all subdirectories and their contents in the specified directory.
    """
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        if os.path.isdir(item_path):
            shutil.rmtree(item_path)
            print(f"Deleted subdirectory and contents: {item_path}")

def rename_files(test_name):
    directory = os.path.join(BASE_DIR, test_name)

    # Clear any existing subdirectories in the target directory
    clear_subdirectories(directory)

    new_dir = os.path.join(directory, 'images')
    os.makedirs(new_dir, exist_ok=True)

    # Get the list of files in the directory
    files = [file for file in os.listdir(directory) if file.endswith('.jpg')]

    for file in tqdm(files, desc=f"Renaming files for {test_name}"):
        # Extract and pad the last number in the file name
        base_name, ext = os.path.splitext(file)
        frame_number = base_name.split('_')[-1].zfill(3)
        new_filename = f"{'_'.join(base_name.split('_')[:-1])}_{frame_number}{ext}"
        new_file_path = os.path.join(new_dir, new_filename)
        old_file_path = os.path.join(directory, file)

        try:
            os.rename(old_file_path, new_file_path)
        except OSError as e:
            print(f"Error moving {old_file_path} to {new_file_path}: {e}")
            continue

    print(f"Files renamed and organized for {test_name}.")

def save_labels(test_name):
    labels_dir = os.path.join(BASE_DIR, test_name, "labels")
    json_file = os.path.join(BASE_DIR, test_name + '.json')

    # Create the labels directory if it does not exist
    os.makedirs(labels_dir, exist_ok=True)

    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"JSON file {json_file} not found.")
        return

    # Create a mapping of file names to image IDs and their dimensions
    annotations_map = {}
    for annotation in data['annotations']:
        image_id = annotation['image_id']
        if image_id not in annotations_map:
            annotations_map[image_id] = []
        annotations_map[image_id].append(annotation)

    for image in tqdm(data['images'], desc=f"Saving labels for {test_name}"):
        image_id = image['id']
        img_width = image['width']
        img_height = image['height']

        # Pad frame number in base name
        base_name_parts = os.path.splitext(image['file_name'])[0].split('_')
        base_name_parts[-1] = base_name_parts[-1].zfill(3)
        padded_base_name = '_'.join(base_name_parts)

        label_file_path = os.path.join(labels_dir, f"{padded_base_name}.txt")
        with open(label_file_path, 'w') as label_file:
            if image_id in annotations_map:
                for annotation in annotations_map[image_id]:
                    class_id = annotation['category_id']
                    bbox = annotation['bbox']

                    # Convert bbox to YOLO format
                    x_center = (bbox[0] + bbox[2] / 2) / img_width
                    y_center = (bbox[1] + bbox[3] / 2) / img_height
                    width = bbox[2] / img_width
                    height = bbox[3] / img_height

                    label_file.write(f"{class_id-1} {x_center} {y_center} {width} {height}\n")

    print(f"Labels saved in YOLO format in {labels_dir} for {test_name}.")

def separate_channels(test_name):
    directory = os.path.join(BASE_DIR, test_name, 'images')
    new_dirs = [os.path.join(BASE_DIR, test_name + '_' + str(i), 'images') for i in range(3)]
    for new_dir in new_dirs:
        os.makedirs(new_dir, exist_ok=True)

    image_files = [f for f in os.listdir(directory) if f.endswith('.jpg')]

    for image_file in tqdm(image_files, desc=f"Separating channels for {test_name}"):
        src_image_path = os.path.join(directory, image_file)
        image = cv2.imread(src_image_path)

        if image is None:
            print(f"Warning: Failed to load image {src_image_path}. Skipping.")
            continue

        base_filename = os.path.splitext(image_file)[0]
        for channel in range(3):
            channel_image = image[:, :, channel]
            save_image_path = os.path.join(new_dirs[channel], f"{base_filename}.jpg")
            cv2.imwrite(save_image_path, channel_image, [int(cv2.IMWRITE_JPEG_QUALITY), 95])

    print(f"Channels separated for {test_name}.")

def copy_labels(test_name):
    label_dir = os.path.join(BASE_DIR,test_name, "labels")
    new_label_dirs = [os.path.join(BASE_DIR, test_name + '_' + str(i), 'labels') for i in range(3)]

    for new_label_dir in new_label_dirs:
        os.makedirs(new_label_dir, exist_ok=True)

        for label_file in tqdm(os.listdir(label_dir), desc=f"Copying labels to {new_label_dir}"):
            src_path = os.path.join(label_dir, label_file)
            dest_path = os.path.join(new_label_dir, label_file)
            shutil.copy(src_path, dest_path)

if __name__ == '__main__':
    test_names = ['cfc_channel_test', 'cfc_val', 'cfc_train']

    for test_name in test_names:
        print(f"Processing renaming for {test_name}...")
        rename_files(test_name)

        print(f"Processing label generation for {test_name}...")
        save_labels(test_name)

        print(f"Processing channel separation for {test_name}...")
        separate_channels(test_name)

        print(f"Processing label copying for {test_name}...")
        copy_labels(test_name)
