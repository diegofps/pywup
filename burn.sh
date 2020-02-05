wup cluster burn --cluster \
    --w '$HOME' \
    --o "$HOME/teste_output" \
    --runs 2 \
    --v P1 1 2 3 \
\
    --e TESTE \
    --va P2 1 10 2 \
    --vg P3 1 10 1.5 \
    --c './test.py $P1 $P2 $P3'

