#! /bin/bash

# validates the already trained yolo models on their respective versions of sonar data images, namely the separated out channels from the original sonar images, which were a combination of channels A, B, C

SCRIPT="automated_jobs/run_job.py"
JOB="val"
EXP="experiment4" # name is experiment 4 because this originally was experiment 4, since experiments 1-5 used to be named 0-4

#job OG (A,B,C as rbg)
BASE_DATA_DIR="original/"
TRAINDATA="azureml:hyper-images-original:3"
MODEL="azureml:exp4-og-train-last:1"
python3 $SCRIPT \
    --job $JOB \
    --job-name exp4-OG-val \
    --exp-name $EXP \
    --train-data $TRAINDATA \
    --epochs 50 \
    --pre-model $MODEL \
    --base-data-dir $BASE_DATA_DIR \
    --train-dirs "cfc_train" \
    --val-dirs "cfc_channel_test" \

#job for Channel A separated- consecutive frame differences aka channel 0, done in the part 2 val shell script


#job for Channel B separated- mean subtracted image, done in the part 2 val shell script


#job Channel C raw sonar image
TRAINDATA="azureml:hyper-images-channel_2:1"
BASE_DATA_DIR="channel_2/"
MODEL="azureml:exp4-chan2-train-best:1"
python3 $SCRIPT \
    --job $JOB \
    --job-name exp4-Chan2-val \
    --exp-name $EXP \
    --train-data $TRAINDATA \
    --epochs 50 \
    --pre-model $MODEL \
    --base-data-dir $BASE_DATA_DIR \
    --train-dirs "cfc_train" \
    --val-dirs "cfc_channel_test" \

#job for hyperimage with 3 layers- version 1
TRAINDATA="azureml:hyper-images-stack:4"
BASE_DATA_DIR="stack/"
MODEL="azureml:exp4-hyperver-stack-train-best:1"
python3 $SCRIPT \
    --job $JOB \
    --job-name exp4-HyperVer-stack-val \
    --exp-name $EXP \
    --train-data $TRAINDATA \
    --epochs 50 \
    --pre-model $MODEL \
    --base-data-dir $BASE_DATA_DIR \
    --train-dirs "cfc_train" \
    --val-dirs "cfc_channel_test" \

#job for hyperimage with 3 layers- version 2
TRAINDATA="azureml:hyper-images-diff:1"
BASE_DATA_DIR="diff/"
MODEL="exp4-hyperver-diff-train-last:1"
python3 $SCRIPT \
    --job $JOB \
    --job-name exp4-HyperVer-diff-val \
    --exp-name $EXP \
    --train-data $TRAINDATA \
    --epochs 50 \
    --pre-model $MODEL \
    --base-data-dir $BASE_DATA_DIR \
    --train-dirs "cfc_train" \
    --val-dirs "cfc_channel_test" \