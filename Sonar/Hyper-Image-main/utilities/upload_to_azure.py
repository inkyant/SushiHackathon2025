import os
import subprocess

# Define the folder and YAML files
base_folder = "/Users/carlosnoyes/Data Storage/Hyper-Image/for_azure"
# Change directory to the base folder
os.chdir(base_folder)

yamls = [
    "for_azure-channel_0.yaml",
    "for_azure-channel_1.yaml",
    "for_azure-channel_2.yaml",
    "for_azure-diff.yaml",
    "for_azure-original.yaml",
    "for_azure-stack.yaml"
]

# only the first two yamls because those didn't upload right
yamls = yamls[:2]

# Define Azure resource group and workspace
resource_group = "task-1-video"
workspace_name = "eyesea-yolo-2"

# Function to upload each YAML
def upload_to_azure(yaml_file):
    command = [
        "az", "ml", "data", "create",
        "-f", yaml_file,  # Use yaml_file directly since we are already in the correct directory
        "--resource-group", resource_group,
        "--workspace-name", workspace_name
    ]
    print("Executing command:", " ".join(command))  # Log the command for visibility

    try:
        print(f"Uploading {yaml_file}...")
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print(f"Successfully uploaded {yaml_file}: {result.stdout}")
    except subprocess.CalledProcessError as e:
        print(f"Error uploading {yaml_file}: {e.stderr}")

# Loop through YAML files and upload
for yaml_file in yamls:
    upload_to_azure(yaml_file)
