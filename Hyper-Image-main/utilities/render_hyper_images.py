import os
import cv2
import numpy as np


def render_hyper_image(hyper_image, render_scale=1):
    """
    Render a hyper image as a single RGB composite image, using 32-bit float precision until final conversion.

    Parameters:
        hyper_image (np.ndarray): Hyper image with shape (height, width, channels), values in [0, 1].

    Returns:
        Rendered hyper image as RGB composite in 8-bit format for display.
    """
    n = (hyper_image.shape[-1] - 1) // 2
    # Middle channel is the original frame (grayscale), convert it to RGB
    image = np.stack([hyper_image[:, :, n]] * 3, axis=-1)  # Replicate middle channel to RGB channels

    # Add the first n frames to the red channel
    for i in range(2 * n + 1):
        if i == n:
            continue
        factor = i / (2 * n)
        add_channel = (hyper_image[:, :, i] - 0.5) * 2  # Scale back to original
        image[:, :, 0] += add_channel * factor / n * render_scale # Add to red channel, scale by factor and divide by n
        image[:, :, 2] += add_channel * (1 - factor) / n * render_scale   # Add to blue channel, scale by 1-factor and divide by n

    # Clip the values to [0, 1], then convert to 8-bit [0, 255] for display or saving
    image = np.clip(image, 0, 1) * 255
    return image.astype(np.uint8)


def save_hyper_video(save_dir, hyper_images, fps=10, video_name="hyper_video.mp4", blank_frames=0, render_scale=1):
    """
    Saves a video from the rendered hyper images, with optional blank frames at the beginning and end.

    Parameters:
        save_dir (str): Directory to save the video.
        hyper_images (list): List of tuples containing filenames and hyper images.
        fps (int): Frames per second for the video.
        video_name (str): Name of the output video file.
        blank_frames (int): Number of blank frames to add at the beginning and end.
    """
    os.makedirs(save_dir, exist_ok=True)
    video_path = os.path.join(save_dir, video_name)

    # Determine the frame size from the first rendered image
    first_image = render_hyper_image(hyper_images[0][1])
    height, width, _ = first_image.shape

    # Initialize the VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")  # 'mp4v' codec for .mp4 files
    video_writer = cv2.VideoWriter(video_path, fourcc, fps, (width, height))

    # Create a blank (black) frame
    blank_frame = np.zeros((height, width, 3), dtype=np.uint8)

    # Add blank frames at the beginning
    for _ in range(blank_frames):
        video_writer.write(blank_frame)

    # Process each hyper image and add to video
    for filename, hyper_image in hyper_images:
        rendered_image = render_hyper_image(hyper_image, render_scale=render_scale)
        video_writer.write(cv2.cvtColor(rendered_image, cv2.COLOR_RGB2BGR))  # Convert RGB to BGR for OpenCV

    # Add blank frames at the end
    for _ in range(blank_frames):
        video_writer.write(blank_frame)

    # Release the video writer object
    video_writer.release()
    print(f"Video saved at {video_path}")


def concat_hyper_videos(save_dir, hyper_videos_paths, video_name="concatenated_hyper_video.mp4"):
    """
    Concatenates multiple hyper videos side-by-side into a single video.

    Parameters:
        save_dir (str): Directory to save the concatenated video.
        hyper_videos_paths (list): List of video paths to concatenate side-by-side.
        video_name (str): Name of the output video file.
    """
    # Ensure there's more than one video to concatenate
    if len(hyper_videos_paths) < 2:
        raise ValueError("Need at least two videos to concatenate side-by-side.")

    # Read the first video to get the frame size and fps
    cap = cv2.VideoCapture(hyper_videos_paths[0])
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()

    # Initialize the VideoWriter object with the combined width
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    video_path = os.path.join(save_dir, video_name)
    combined_width = width * len(hyper_videos_paths)
    video_writer = cv2.VideoWriter(video_path, fourcc, fps, (combined_width, height))

    # Open all video captures simultaneously
    caps = [cv2.VideoCapture(path) for path in hyper_videos_paths]

    # Read and concatenate frames side-by-side until any video ends
    while True:
        frames = []
        for cap in caps:
            ret, frame = cap.read()
            if not ret:
                # Stop if any video ends
                break
            frames.append(frame)

        if len(frames) != len(hyper_videos_paths):
            break

        # Concatenate frames horizontally
        combined_frame = np.hstack(frames)
        video_writer.write(combined_frame)

    # Release all captures and the video writer
    for cap in caps:
        cap.release()
    video_writer.release()

    print(f"Concatenated video saved at {video_path}")

