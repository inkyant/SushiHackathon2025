#! /bin/bash

# validates the already trained yolo models on their respective versions of sonar data images, namely the separated out channels from the original sonar images, which were a combination of channels A, B, C

SCRIPT="automated_jobs/run_job.py"
JOB="val"
EXP="experiment4" # name is experiment 4 because this originally was experiment 4, since experiments 1-5 used to be named 0-4


#job OG (A,B,C as rbg), job is run in the part 1 val shell script


# job for Channel A separated- consecutive frame differences aka channel 0
BASE_DATA_DIR="channel_0/"
TRAINDATA="azureml:hyper-images-channel_0:3"
MODEL="azureml:exp4-chan0-train-try5-best:1"
python3 $SCRIPT \
    --job $JOB \
    --job-name exp4-Chan0-val-try5-2 \
    --exp-name $EXP \
    --train-data $TRAINDATA \
    --epochs 50 \
    --pre-model $MODEL \
    --base-data-dir $BASE_DATA_DIR \
    --train-dirs "cfc_train" \
    --val-dirs "cfc_channel_test" \

# job for Channel B separated- mean subtracted image
BASE_DATA_DIR="channel_1/"
TRAINDATA="azureml:hyper-images-channel_1:3"
MODEL="azureml:exp4-chan1-train-try5-best:1"
python3 $SCRIPT \
    --job $JOB \
    --job-name exp4-Chan1-val-try5-2 \
    --exp-name $EXP \
    --train-data $TRAINDATA \
    --pre-model $MODEL \
    --base-data-dir $BASE_DATA_DIR \
    --train-dirs "cfc_train" \
    --val-dirs "cfc_channel_test" \

#job Channel C raw sonar image, job is run in the part 1 val shell script


#job for hyperimage with 3 layers- version 1, job is run in the part 1 val shell script


# #job for hyperimage with 3 layers- version 2, job is run in the part 1 val shell script
