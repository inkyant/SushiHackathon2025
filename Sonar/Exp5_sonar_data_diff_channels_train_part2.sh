#! /bin/bash

# trains a yolo model on various versions of sonar data images, namely the separated out channels from the original sonar images, which were a combination of channels A, B, C

SCRIPT="automated_jobs/run_job.py"
JOB="train"
EXP="experiment4" # name is experiment 4 because this originally was experiment 4, since experiments 1-5 used to be named 0-4

#job for original sonar images, all 3 channels included (A,B,C as rbg), this is done in the part 1 shell script


#job for Channel A separated- consecutive frame differences aka channel 0
TRAINDATA="azureml:hyper-images-channel_0:3"
BASE_DATA_DIR="channel_0/"
MODEL="azureml:yolov8m-vas:1"
python3 $SCRIPT \
    --job $JOB \
    --job-name exp4-Chan0-train-try5 \
    --exp-name $EXP \
    --train-data $TRAINDATA \
    --epochs 50 \
    --pre-model $MODEL \
    --base-data-dir $BASE_DATA_DIR \
    --train-dirs "cfc_train" \
    --val-dirs "cfc_val" \

#job for Channel B separated- mean subtracted image
TRAINDATA="azureml:hyper-images-channel_1:3"
BASE_DATA_DIR="channel_1/"
MODEL="azureml:yolov8m-vas:1"
python3 $SCRIPT \
    --job $JOB \
    --job-name exp4-Chan1-train-try5 \
    --exp-name $EXP \
    --train-data $TRAINDATA \
    --pre-model $MODEL \
    --base-data-dir $BASE_DATA_DIR \
    --train-dirs "cfc_train" \
    --val-dirs "cfc_val" \

#job Channel C raw sonar image is done in the part 1 shell file 


#job for hyperimage with 3 layers- version 1, is done in the part 1 shell file 


# #job for hyperimage with 3 layers- version 2, is done in the part 1 shell file 


