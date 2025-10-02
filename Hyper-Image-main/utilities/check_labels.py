import glob

label_files = glob.glob('/Users/carlosnoyes/Data Storage/Hyper-Image/cfc_train_stack_n1/labels/*.txt')

for label_file in label_files[:5]:  # Check first 5 files
    print(f"Checking {label_file}:")
    with open(label_file) as f:
        for line in f:
            parts = line.strip().split()
            assert len(parts) == 5, f"Incorrect format in {label_file}: {line}"
            class_id, x_center, y_center, width, height = map(float, parts)
            assert class_id == 0, f"Invalid class_id {class_id} in {label_file}"  # Single-class dataset
            assert 0 <= x_center <= 1, f"x_center out of range in {label_file}: {x_center}"
            assert 0 <= y_center <= 1, f"y_center out of range in {label_file}: {y_center}"
            assert 0 <= width <= 1, f"width out of range in {label_file}: {width}"
            assert 0 <= height <= 1, f"height out of range in {label_file}: {height}"

print("All checked labels are correctly formatted.")
