#!/bin/bash

# Configuration
FILENAME="coordinates.csv"
GRID_SIZE=19
SPACING=10

# Write the header
echo "x,y,z" > $FILENAME

# Loop through the grid
for (( i=0; i<$GRID_SIZE; i++ ))
do
    for (( j=0; j<$GRID_SIZE; j++ ))
    do
        # Calculate X and Z positions centered at 0
        # Formula: (index - (max/2)) * spacing
        X=$(echo "scale=2; ($i - ($GRID_SIZE / 2)) * $SPACING" | bc)
        Z=$(echo "scale=2; ($j - ($GRID_SIZE / 2)) * $SPACING" | bc)

        # Generate a Y value (height) using sine/cosine for some hills
        # We use i and j as inputs to the trig functions
        Y=$(echo "scale=4; s($i/2) * 20 + c($j/2) * 15" | bc -l)

        # Append to CSV
        echo "$X,$Y,$Z" >> $FILENAME
    done
done

echo "Successfully generated $FILENAME with $(($GRID_SIZE * $GRID_SIZE)) coordinates."
