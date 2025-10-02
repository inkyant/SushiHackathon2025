import yaml
import os

def make_yaml(mode, n, yaml_dir='YAMLs'):
    """
    Creates a YAML file with the necessary information for the CFC dataset.

    Parameters:
        mode (str): Mode of operation ('stack', 'diff', 'mean').
        n (int): Number of frames before and after the current frame to consider.
        yaml_dir (str): Directory to save the generated YAML file.

    Returns:
        None
    """
    path = '/Users/carlosnoyes/Data Storage/Hyper-Image'
    images_train = f'cfc_train_{mode}_n{n}'
    images_val = f'cfc_val_{mode}_n{n}'
    images_test = f'cfc_channel_test_{mode}_n{n}'
    nc = 1
    names = ['Fish']

    yaml_dict = {
        'path': path,
        'train': f"{images_train}/images",
        'val': f"{images_val}/images",
        'test': f"{images_test}/images",
        'nc': nc,
        'names': names
    }

    # Validation
    for key in ['train', 'val', 'test']:
        full_path = os.path.join(path, yaml_dict[key])
        assert os.path.isdir(full_path), f"Error: Directory {full_path} does not exist!"

    os.makedirs(yaml_dir, exist_ok=True)

    yaml_path = f"{yaml_dir}/cfc_{mode}_n{n}.yaml"
    with open(yaml_path, 'w') as file:
        yaml.dump(yaml_dict, file)

    print(f"YAML file created: {yaml_path}")


if __name__ == '__main__':
    yaml_dir = '/Users/carlosnoyes/PycharmProjects/ultralytics/carlos_ws/YAMLs'
    modes = ['stack', 'diff', 'mean']
    modes = ['stack']
    ns = [0, 1, 2]

    for mode in modes:
        for n in ns:
            make_yaml(mode, n, yaml_dir=yaml_dir)
