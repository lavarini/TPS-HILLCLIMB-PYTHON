#!/bin/sh

for i in u159 u574 u1060 u1432 u1817 u2152 u2319; do
    echo hillclimb $i
    python tsp.py -o results/hillclimb-${i}.png -n 10000 -m reversed_sections -a hillclimb fonts/${i}.txt >> results/${i}.txt
    sleep 0.1
done
