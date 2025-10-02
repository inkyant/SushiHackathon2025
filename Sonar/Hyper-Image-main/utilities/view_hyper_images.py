import cv2
import numpy as np
import os

saved_image_directory = 'saved_images'

base_directory = '/Users/carlosnoyes/Data Storage/Hyper-Image/cfc_train'

sub_directories = [f for f in os.listdir(base_directory) if os.path.isdir(os.path.join(base_directory, f))]
sub_directories = [f for f in sub_directories if 'Stratum1' in f]

sort = True
if sort:
    sub_directories.sort()
else:
    np.random.seed(1)
    np.random.shuffle(sub_directories)

sub_dir_count = 30
sub_directories = sub_directories[:sub_dir_count]

max_x = 0
max_y = 0

# Find max dimensions
for i in range(len(sub_directories)):
    sub_directory = os.path.join(base_directory, sub_directories[i])
    image_files = sorted([f for f in os.listdir(sub_directory) if f.endswith('.jpg')])
    image_path_0 = os.path.join(sub_directory, image_files[0])
    image_0 = cv2.imread(image_path_0)
    max_x = max(max_x, image_0.shape[1])
    max_y = max(max_y, image_0.shape[0])

# Initialize VideoWriter
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
frame_rate = 10
out = cv2.VideoWriter(os.path.join(saved_image_directory, 'hyper_images.mp4'), fourcc, frame_rate, (max_x, max_y))
out_2 = cv2.VideoWriter(os.path.join(saved_image_directory, 'hyper_images_2.mp4'), fourcc, frame_rate, (max_x, max_y))
out_3 = cv2.VideoWriter(os.path.join(saved_image_directory, 'hyper_images_3.mp4'), fourcc, frame_rate, (max_x, max_y))
out_4 = cv2.VideoWriter(os.path.join(saved_image_directory, 'hyper_images_4.mp4'), fourcc, frame_rate, (max_x, max_y))

# Black frame for out_2
black_frame = np.zeros((max_y, max_x, 3), dtype=np.uint8)

# Process images
for i in range(len(sub_directories)):
    print(sub_directories[i])
    sub_directory = os.path.join(base_directory, sub_directories[i])
    image_files = sorted([f for f in os.listdir(sub_directory) if f.endswith('.jpg')])
    image_paths = [os.path.join(sub_directory, f) for f in image_files]
    number_of_images = len(image_files)
    middle_image_ID = number_of_images // 2

    N = 20  # Number of images around the middle
    for j in range(middle_image_ID - N // 2, middle_image_ID + N // 2):
        if j < 0 or j >= number_of_images:
            continue
        image = cv2.imread(image_paths[j])
        channel_2 = image[:, :, 2].astype(np.uint8)  # Extract red channel
        channel_2 = cv2.resize(channel_2, (max_x, max_y))  # Resize to max dimensions
        grayscale_3_channel = cv2.merge([channel_2, channel_2, channel_2])
        out.write(grayscale_3_channel)

        hyper_image = np.zeros((image.shape), dtype=np.uint8)
        hyper_image[:, :, 0] = cv2.imread(image_paths[j-1])[:, :, 2]
        hyper_image[:, :, 1] = cv2.imread(image_paths[j])[:, :, 2]
        hyper_image[:, :, 2] = cv2.imread(image_paths[j+1])[:, :, 2]
        hyper_image = cv2.resize(hyper_image, (max_x, max_y))
        out_3.write(hyper_image)

        if j == middle_image_ID:
            # Add still frame for 0.8 seconds
            for _ in range(int(frame_rate * 1.8)):
                out_2.write(grayscale_3_channel)
                out_4.write(hyper_image)
            # Add black frame for 0.2 seconds
            for _ in range(int(frame_rate * 0.2)):
                out_2.write(black_frame)
                out_4.write(black_frame)

# Release VideoWriter
out.release()
out_2.release()
out_3.release()
out_4.release()

