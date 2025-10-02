import os

base_path = '/Users/carlosnoyes/Data Storage/Hyper-Image'
subsets = ['cfc_train_stack_n0', 'cfc_val_stack_n0', 'cfc_channel_test_stack_n0']

for subset in subsets:
    images_dir = os.path.join(base_path, subset, 'images')
    labels_dir = os.path.join(base_path, subset, 'labels')

    if not os.path.isdir(labels_dir):
        print(f"[ERROR] Missing labels directory: {labels_dir}")
        continue

    image_files = sorted([f for f in os.listdir(images_dir) if f.endswith(('.jpg', '.png', '.npy'))])
    label_files = sorted([f for f in os.listdir(labels_dir) if f.endswith('.txt')])

    print(f"{images_dir} contains {len(image_files)} images.")
    print(f"{labels_dir} contains {len(label_files)} labels.")

    if len(image_files) != len(label_files):
        print(f"[ERROR] Mismatch in image and label counts for {subset}: {len(image_files)} images vs {len(label_files)} labels.")
    else:
        print(f"[OK] Image and label counts match for {subset}.")
