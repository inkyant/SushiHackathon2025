# Hyper-Images for YOLOv8

This repository facilitates working with the Caltech Fish Counting dataset for training and testing yolo models with hyper-images. Below are the detailed steps for installation and data preparation.

## Dataset Information

#### Images
- [CFC Kenai (source) train images (16 GB)](https://data.caltech.edu/records/bseww-80110/files/cfc_train.zip?download=1)
- [CFC Kenai (source) validation images (4.1 GB)](https://data.caltech.edu/records/bseww-80110/files/cfc_val.zip?download=1)
- [CFC Channel (target) test images (2.8 GB)](https://data.caltech.edu/records/bseww-80110/files/cfc_channel_test.zip?download=1)

#### Labels
- [CFC Kenai (source) train labels](https://data.caltech.edu/records/bseww-80110/files/cfc_train.json?download=1)
- [CFC Kenai (source) validation labels](https://data.caltech.edu/records/bseww-80110/files/cfc_val.json?download=1)
- [CFC Channel (target) test labels](https://data.caltech.edu/records/bseww-80110/files/cfc_channel_test.json?download=1)

#### New links can be found here if the above links are not working: [Caltech Fish Counting - CFC-DAOD](https://github.com/visipedia/caltech-fish-counting/tree/main/CFC-DAOD)

The images are given in the 'Baseline++' format. Where,
- r-chanel is the raw image, 
- g-channel is data with the mean image filtered out.
- b-channel is the difference between to consecutive frames, and

## Installation
1. **Unzip the Dataset** - Extract the downloaded images.
2. **Update the Config json** - Save the path to the data folder in the `config.json` file.
 
  Example:
  ```json
  {
  "base_dir": "path/to/data/folder"
  }
  ```

 After downloading and extracting your directory structure should look like this:
 ```
    path/to/data/folder
    ├── cfc_channel_test.json   # Labels for the data
    ├── cfc_channel_test.zip    # Image data zipped
    ├── cfc_channel_test        # Image data unzipped in the 'Baseline++' format
    │   ├── 2018-08-16-JD228_Channel_Stratum1_Set1_CH_2018-08-16_060006_532_732_0.jpg
    │   ├── 2018-08-16-JD228_Channel_Stratum1_Set1_CH_2018-08-16_060006_532_732_1.jpg
    │   └── ...
    │
    ├── cfc_train.json          # Labels for the data
    ├── cfc_train.zip           # Image data zipped
    ├── cfc_train               # Image data unzipped in the 'Baseline++' format
    │   ├── 2018-05-26-JD146_LeftFar_Stratum1_Set1_LO_2018-05-26_080004_285_885_0.jpg
    │   ├── 2018-05-26-JD146_LeftFar_Stratum1_Set1_LO_2018-05-26_080004_285_885_1.jpg
    │   └── ...
    │
    ├── cfc_val.json            # Labels for the data
    ├── cfc_val.zip             # Image data zipped
    └── cfc_val                 # Image data unzipped in the 'Baseline++' format
        ├── 2018-06-03-JD154_LeftFar_Stratum1_Set1_LO_2018-06-03_020004_3240_3840_0.jpg
        ├── 2018-06-03-JD154_LeftFar_Stratum1_Set1_LO_2018-06-03_020004_3240_3840_1.jpg
        └── ...

```


## Libraries Used

This repository relies on the following Python libraries:
- `cv2` (OpenCV)
- `numpy`

Make sure these libraries are installed in your environment before proceeding.

## Usage

After setting up the dataset and modifying the base directory paths, run the following scripts in order:
1. **1_manage_files.py** - This script will prepare the data for hyper-image generation.
2. **2_make_hyper_image.py** - This script will generate hyper-images from the data.


## After Running 1_manage_files.py
The file structure should look like this:
```
    path/to/data/folder
    ├── cfc_channel_test.json
    ├── cfc_channel_test.zip
    ├── cfc_channel_test    
    │   ├── images
    │   │   ├── 2018-08-16-JD228_Channel_Stratum1_Set1_CH_2018-08-16_060006_532_732_000.jpg     # numbers are now padded with zeros
    │   │   ├── 2018-08-16-JD228_Channel_Stratum1_Set1_CH_2018-08-16_060006_532_732_001.jpg     # numbers are now padded with zeros
    │   │   └── ...
    │   ├── labels
    │   │   ├── 2018-08-16-JD228_Channel_Stratum1_Set1_CH_2018-08-16_060006_532_732_000.txt     # numbers are now padded with zeros
    │   │   ├── 2018-08-16-JD228_Channel_Stratum1_Set1_CH_2018-08-16_060006_532_732_001.txt     # numbers are now padded with zeros
    │   │   └── ...
    ├── cfc_channel_test_0  # b-channel images (difference between consecutive frames)
    ├── cfc_channel_test_1  # g-channel images (mean image filtered out)
    ├── cfc_channel_test_2  # r-channel images (raw images)
    │
    ├── cfc_train.json
    ├── cfc_train.zip
    ├── cfc_train     
    ├── cfc_train_0         # b-channel images (difference between consecutive frames)
    ├── cfc_train_1         # g-channel images (mean image filtered out)
    ├── cfc_train_2         # r-channel images (raw images)
    │
    ├── cfc_val.json
    ├── cfc_val.zip
    ├── cfc_val      
    ├── cfc_val_0           # b-channel images (difference between consecutive frames)
    ├── cfc_val_1           # g-channel images (mean image filtered out)
    └── cfc_val_2           # r-channel images (raw images)
```

## After Running 2_make_hyper_image.py
The file structure should look like this:
```
    path/to/data/folder
    ├── cfc_channel_test.json
    ├── cfc_channel_test.zip
    ├── cfc_channel_test
    ├── cfc_channel_test_0
    ├── cfc_channel_test_1
    ├── cfc_channel_test_2
    ├── cfc_channel_test_2_diff_3  # Difference hyper-image with 3 frames
    ├── cfc_channel_test_2_mean_3  # Mean hyper-image with 3 frames
    ├── cfc_channel_test_2_stack_3  # Stack hyper-image with 3 frames
    │
    ├── cfc_train.json
    ├── cfc_train.zip
    ├── cfc_train
    ├── cfc_train_0
    ├── cfc_train_1
    ├── cfc_train_2
    ├── cfc_train_2_diff_3  # Difference hyper-image with 3 frames
    ├── cfc_train_2_mean_3  # Mean hyper-image with 3 frames
    ├── cfc_train_2_stack_3  # Stack hyper-image with 3 frames
    │
    ├── cfc_val.json
    ├── cfc_val.zip
    ├── cfc_val
    ├── cfc_val_0
    ├── cfc_val_1
    ├── cfc_val_2
    ├── cfc_val_2_diff_3  # Difference hyper-image with 3 frames
    ├── cfc_val_2_mean_3  # Mean hyper-image with 3 frames
    └── cfc_val_2_stack_3  # Stack hyper-image with 3 frames
```

## Data for YOLO
The data generated can be used for training and testing YOLO models. 
The hyper-images are saved in the `*_stack_3` folders. 
The hyper-images are saved in the format `*.jpg` and the labels are saved in the format `*.txt`. 
The labels are in the format `class x_center y_center width height`.

- `cfc_train*` can be used for training 
- `cfc_val*` can be used for validation
- `cfc_channel_test*` can be used for testing


- `*''` refers to the data as downloaded in the 'Baseline++' format (interesting as a reference)
- `*_0` refers to the difference between two frames data channel (interesting as a reference)
- `*_1` refers to the mean-removed data channel (interesting as a reference)
- `*_2` refers to the raw data (use this as a baseline to compare with hyper-images)
- `*_2_diff_3` refers to the difference hyper-image with 3 frames
- `*_2_mean_3` refers to the mean hyper-image with 3 frames
- `*_2_stack_3` refers to the stack hyper-image with 3 frames

any of the above can be used for training and testing YOLO models.