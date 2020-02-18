wup burn \
    --redo \
    --w '$HOME' \
    --o "output" \
    --runs 2 \
    --v P1 1 2 3 \
\
    --e TESTE \
    --va P2 1 10 2 \
    --vg P3 1 10 1.5 \
    --c '/home/diego/Sources/pywup/test.py $P1 $P2 $P3'

wup parse \
    --i ./output \
    --o ./output/teste.csv \
    --e TESTE \
    --p FULL "Full product: (@float@)" \
    --p BIGGEST "Biggest: (@float@)" \
    --p MINIMUM "Minimum: (@float@)" \
    --p SUM "Sum: (@float@)"

=================================================================================================

wup burn \
    --redo \
    --check \
    --w '/home/wup/Sources/teste' \
    --o "output_teste" \
    --runs 1 \
    --v DS Dog \
\
    --e ZTracker \
    --va GRIDSIZE 5 21 2 \
    --va MAXTRAINS 5 45 2 \
    --va THRESHOLD 0.5 1.0 0.05 \
    --va NUMDISCS 4 20 2 \
    --va STEPSIZE1 0.04 0.3 0.04 \
    --va STEPSIZE2 0.04 0.3 0.04 \
    --va MAXRAMS 50 200 50 \
    --va TIMEWINDOW 10 100 10 \
    --va L1 0.1 1.01 0.1 \
    --va L2 0.1 1.01 0.1 \
    --va AREA1 0.0005 0.0051 0.0005 \
    --va AREA2 0.0005 0.0051 0.0005 \
    --va NUMLAYERS 10 50 10 \
    --v LEARNWINDOW 1 2 3 4 5 \
    --va RAMBITS 2 8 1 \
    --va RAMBITS 2 8 1 \
    --va REPLICATE 1 6 1 \
    --va MINCONFIDENCE 0.0 0.5 0.1 \
    --c './main6 -model z \
        -ds $DS \
        -gridSize $GRIDSIZE \
        -cdMaxTrains $MAXTRAINS \
        -cdThreshold $THRESHOLD \
        -cdNumDiscs $NUMDISCS \
        -ztStepSize $STEPSIZE1 $STEPSIZE2 \
        -ztScanSize $SCANSIZE1 $SCANSIZE2 \
        -ztMaxRams $MAXRAMS \
        -ztTimeWindow $TIMEWINDOW \
        -ztL1 $L1 \
        -ztL2 $L2 \
        -ztArea $AREA1 $AREA2 \
        -ztNumLayers $NUMLAYERS \
        -ztScalePen $SCALEPEN \
        -ztLearnWindow $LEARNWINDOW \
        -ztRamBits $RAMBITS \
        -ztReplicate $REPLICATE \
        -ztMinConfidence $MINCONFIDENCE'

DATASETS="`(cd /home/wup/Sources/teste/data/otg100 && ls -d */ | sed -r 's:/::' | tr '\n' ' ')`"

wup burn --cluster \
    --redo \
    --w '/home/wup/Sources/teste' \
    --o "output_teste" \
    --runs 10 \
    --v DS $DATASETS \
\
    --e ZTracker1 \
    --v GRIDSIZE 7 10 13 15 \
    --va STEPSIZE1 0.04 0.21 0.04 \
    --va STEPSIZE2 0.04 0.21 0.04 \
    --va SCANSIZE1 0.5 1.31 0.2 \
    --va SCANSIZE2 0.3 0.91 0.2 \
    --c './main6 -model z \
        -ds $DS \
        -gridSize $GRIDSIZE \
        -cdMaxTrains 30 \
        -cdThreshold 0.8 \
        -cdNumDiscs 10 \
        -ztStepSize $STEPSIZE1 $STEPSIZE2 \
        -ztScanSize $SCANSIZE1 $SCANSIZE2 \
        -ztTimeWindow 50 \
        -ztL1 0.8 \
        -ztL2 0.6 \
        -ztArea 0.002 0.2 \
        -ztNumLayers 30 \
        -ztScalePen 0.0 \
        -ztLearnWindow 1 \
        -ztRamBits 6 \
        -ztReplicate 2 \
        -ztMinConfidence 0.0' \
\
    --e ZTracker2 \
    --v LEARNWINDOW 1 2 3 \
    --va RAMBITS 4 6 1 \
    --va REPLICATE 1 3 1 \
    --c './main6 -model z \
        -ds $DS \
        -gridSize 15 \
        -cdMaxTrains 30 \
        -cdThreshold 0.8 \
        -cdNumDiscs 10 \
        -ztStepSize 0.08 0.08 \
        -ztScanSize 0.8 0.5 \
        -ztTimeWindow 50 \
        -ztL1 0.8 \
        -ztL2 0.6 \
        -ztArea 0.002 0.2 \
        -ztNumLayers 30 \
        -ztScalePen 0.0 \
        -ztLearnWindow $LEARNWINDOW \
        -ztRamBits $RAMBITS \
        -ztReplicate $REPLICATE \
        -ztMinConfidence 0.0'

/usr/bin/time wup burn \
    --redo \
    --summary \
    --w '/home/wup/Sources/teste' \
    --o "output_teste" \
    --runs 10 \
    --v DS $DATASETS \
\
    --e ZTracker \
    --c './main6 -model z \
        -ds Dog \
        -gridSize 15 \
        -cdMaxTrains 30 \
        -cdThreshold 0.8 \
        -cdNumDiscs 10 \
        -ztStepSize 0.08 0.08 \
        -ztScanSize 0.8 0.5 \
        -ztMaxRams 40 \
        -ztTimeWindow 50 \
        -ztL1 0.8 \
        -ztL2 0.6 \
        -ztArea 0.002 0.2 \
        -ztNumLayers 30 \
        -ztScalePen 0.0 \
        -ztLearnWindow 1 \
        -ztRamBits 6 \
        -ztReplicate 2 \
        -ztMinConfidence 0'

================================================================================

./main6 -model z \
    -ds Dog \
    -gridSize 15 \
    -cdMaxTrains 30 \
    -cdThreshold 0.8 \
    -cdNumDiscs 10 \
    -ztStepSize 0.08 0.08 \
    -ztScanSize 0.8 0.5 \
    -ztMaxRams 40 \
    -ztTimeWindow 50 \
    -ztL1 0.8 \
    -ztL2 0.6 \
    -ztArea 0.002 0.2 \
    -ztNumLayers 30 \
    -ztScalePen 0.0 \
    -ztLearnWindow 1 \
    -ztRamBits 6 \
    -ztReplicate 2 \
    -ztMinConfidence 0

