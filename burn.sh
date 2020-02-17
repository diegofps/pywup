wup burn --cluster \
    --redo \
    --w '$HOME' \
    --o "output" \
    --runs 2 \
    --v P1 1 2 3 \
\
    --e TESTE \
    --va P2 1 10 2 \
    --vg P3 1 10 1.5 \
    --c './test.py $P1 $P2 $P3'

wup parse \
    --i ./output \
    --o ./output/parse.csv \
    --p FULL "Full product: @float@" \
    --p BIGGEST "Biggest: @float@" \
    --p MINIMUM "Minimum: @float@" \
    --p SUM "Sum: @float@"

