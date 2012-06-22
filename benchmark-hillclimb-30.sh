#!/bin/sh

echo '' > results/hillclimb500.txt
for i in 1 2 3 4 5 6 7 8 9 10; do
    echo hillclimb $i
    python tsp.py -o results/city30-hillclimb-${i}.png -n 1000 -m reversed_sections -a hillclimb city30.txt >> results/hillclimb30.txt
    sleep 0.1
done