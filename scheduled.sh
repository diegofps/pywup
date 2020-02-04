#!/bin/sh

LABEL=$1
CLUSTER=$2

if [ -z "$CLUSTER" ]
then
    echo "Syntax: $0 <LABEL> <CLUSTER_NAME>"
    exit 1
fi

KEY=`uuidgen`
DATASETS="`(cd /home/ngd/Tracker/ACM-Journal/datasets/otb100-equal/wup/goturn/Valkyrie-AIC2U/ && ls -d */ | sed -r 's:/::' | tr '\n' ' ')`"
OUTFILE="./output_runs_parallel/main.log"
OUTDIR="./output_runs_parallel/${KEY}"

echo "OUTDIR = $OUTDIR"

mkdir -p $OUTDIR
wup use --c $CLUSTER

echo "----------------------------------------------------------------------" >> $OUTFILE
echo "Type: SCHEDULED" >> $OUTFILE
echo "UUID: $KEY" >> $OUTFILE
echo "Label: $LABEL" >> $OUTFILE
echo "Cluster: $CLUSTER" >> $OUTFILE
echo "Started at: $(date)" >> $OUTFILE

wup cluster burn --cluster \
    --w '$HOME/Tracker/dory2/fullapp' \
    --o "$OUTDIR/burn" \
    --runs 1 \
    --v DS_NAME $DATASETS \
\
    --e WISARD \
    --c "make r6 ds=\$DS_NAME fps=30 extra='-gridSize 15 -cdMaxTrains 30 -cdThreshold 0.8 -cdNumDiscs 10 -model z -ztRamBits 5 -ztReplicate 2 -ztMinConfidence 0'" > $OUTDIR/log

echo "Ended at: $(date)" >> $OUTFILE

