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

