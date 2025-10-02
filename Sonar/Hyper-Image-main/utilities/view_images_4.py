import cv2
import numpy as np
import os
from sklearn.decomposition import PCA
from torch.ao.quantization.backend_config.backend_config import INPUT_DTYPE_DICT_KEY


def get_clips(image_dir):
    """
    Separates the images into clips based on the file name.
    :param image_dir: Path to the directory containing the images.
    :return: clips: Dictionary with the images separated by the clip keys.
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


def make_hyper_image_stack(N, image_paths, data_dir):
    M = len(image_paths) // 2
    hyper_im = None
    for j in range(N):
        idx = M - N // 2 + j
        if idx < 0 or idx >= len(image_paths):
            continue  # Skip invalid indices
        im_path = os.path.join(data_dir, image_paths[idx])
        im = cv2.imread(im_path, cv2.IMREAD_GRAYSCALE)
        if hyper_im is None:
            hyper_im = np.zeros((im.shape[0], im.shape[1], N), dtype=np.float32)  # Use float for precision
        hyper_im[:, :, j] = im / 255.0  # Normalize to range [0, 1]
    return hyper_im


def make_hyper_image_diff(N, image_paths, data_dir):
    """
    Creates a hyper-image where each frame is the difference from the central frame.
    """
    hyper_im = make_hyper_image_stack(N, image_paths, data_dir)
    diff_im = np.zeros_like(hyper_im, dtype=np.float32)
    for j in range(N):
        if j == N // 2:
            continue
            diff_im[:, :, j] = hyper_im[:, :, j]  # Keep the central frame
        else:
            diff_im[:, :, j] = hyper_im[:, :, j] - hyper_im[:, :, N // 2]
    return diff_im


def HI_PCA(hyper_im):
    height, width, channels = hyper_im.shape
    reshaped_hyper_im = hyper_im.reshape(-1, channels)  # Shape: (Height*Width, N)

    # Apply PCA
    pca = PCA(n_components=3)
    reduced_data = pca.fit_transform(reshaped_hyper_im)  # Shape: (Height*Width, 3)

    # Reshape back to the original image dimensions
    reduced_hyper_im = reduced_data.reshape(height, width, 3)  # Shape: (Height, Width, 3)

    # Normalize the output to [0, 255] for visualization
    reduced_hyper_im = cv2.normalize(reduced_hyper_im, None, 0, 255, cv2.NORM_MINMAX)
    reduced_hyper_im = reduced_hyper_im.astype(np.uint8)
    return reduced_hyper_im


def HI_RGB(hyper_im):
    N = hyper_im.shape[2]
    reduced_hyper_im = np.zeros((*hyper_im.shape[:2], 3), dtype=np.float32)

    if N == 1:
        return hyper_im

    for i in range(N):
        f = i / (N-1)
        im = hyper_im[:, :, i]
        reduced_hyper_im[:, :, 2] += f * im / N
        reduced_hyper_im[:, :, 1] += (1 - f) * im / N
        reduced_hyper_im[:, :, 0] += 0.5 * im / N

    # Normalize the output to [0, 255]
    reduced_hyper_im = cv2.normalize(reduced_hyper_im, None, 0, 255, cv2.NORM_MINMAX)
    reduced_hyper_im = reduced_hyper_im.astype(np.uint8)
    return reduced_hyper_im


# Directory containing your images
data_dir = '/Users/carlosnoyes/Data Storage/Hyper-Image/cfc_train_2/images'

clips = get_clips(data_dir)
keys = list(clips.keys())

viz_mode = 'RGB'
HI_mode = 'diff'

K=0
N=3

while True:
    key = keys[K]
    image_paths = clips[key]

    hyper_im = None

    if HI_mode == 'diff':
        hyper_im = make_hyper_image_diff(N, image_paths, data_dir)
    elif HI_mode == 'stack':
        hyper_im = make_hyper_image_stack(N, image_paths, data_dir)

    if viz_mode == 'RGB':
        im_reduce = HI_RGB(hyper_im)
    elif viz_mode == 'PCA':
        im_reduce = HI_PCA(hyper_im)

    # Display the reduced 3-channel image
    cv2.imshow(f'{viz_mode} - Clip: {K}, N={N}', im_reduce)
    print(f"Current Clip: {K} ({keys[K]}), Frames (N): {N}")
    print("Press 'Esc' to exit, 'Left/Right' to change clip, 'Up/Down")
    # Wait for user input
    press = cv2.waitKey(0)
    if press == 27:  # Esc key
        break
    elif press == 2:  # Left arrow
        K = max(0, K - 1)
    elif press == 3:  # Right arrow
        K = min(len(keys) - 1, K + 1)
    elif press == 0:  # Up arrow
        N += 2
    elif press == 1:  # Down arrow
        N = max(1, N - 2)

    cv2.destroyAllWindows()
