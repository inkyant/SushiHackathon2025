import cv2
import numpy as np
import os
from sklearn.decomposition import PCA

# Directory containing your images
data_dir = '/Users/carlosnoyes/Data Storage/Hyper-Image/cfc_train_2/images'

# Get all image files
all_files = os.listdir(data_dir)
all_files = [f for f in all_files if f.endswith('.jpg')]
all_files = sorted(all_files)

# Number of images (channels) to stack
N = 5

# Load images and stack them into a hyper-image
for i in range(N):
    im_path = os.path.join(data_dir, all_files[i])
    im = cv2.imread(im_path, cv2.IMREAD_GRAYSCALE)
    if i == 0:
        hyper_im = np.zeros((im.shape[0], im.shape[1], N), dtype=np.float32)  # Use float for precision
    hyper_im[:, :, i] = im / 255.0  # Normalize to range [0, 1]

# Dimensionality reduction: Weighted linear combination or PCA
if N == 3:
    # Directly use the original 3 channels
    reduced_hyper_im = hyper_im.copy()  # Shape: (Height, Width, 3)
else:
    # Apply PCA to reduce dimensions to 3
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

# Display the reduced 3-channel image
cv2.imshow('Reduced Hyper Image', reduced_hyper_im)
cv2.waitKey(0)
cv2.destroyAllWindows()
