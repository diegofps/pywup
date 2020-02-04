wup cluster burn \
    --runs 1 \
    --o "./experiment" \
    --v DS_NAME $DATASETS \
    --w "~/Tracker/ACM-..." \
\
    --e GOTURN \
    --c '...' \
\
    --e RCF \
    --c '...' \
\
    --e WISARD \
    --c '(cd ../dory && make $DS_NAME ...)' \
\
    --e MOSSE \
    --c '(...)'


wup parse \
    --i "./experiment" \
    --o "./experiment.csv" \
    --p INTERSECTION "$INTERSECTION" \
    --p FPS "$FPS" \
    --p TRACK_TIME "$TRACK_TIME" \
    --p LOAD_N_TRACK_TIME "$LOAD_N_TRACK_TIME" \
\
    --e GOTURN \
    --p INTERSECTION "$INTERSECTION_GOTURN" \
    --p FPS "$FPS_GOTURN" \
    --p TRACK_TIME "$TRACK_TIME_GOTURN" \
    --p LOAD_N_TRACK_TIME "$LOAD_N_TRACK_TIME_GOTURN"
