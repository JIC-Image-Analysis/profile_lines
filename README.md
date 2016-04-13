# Profile lines

Measure intensity from one image based on a set of lines drawn in another.

## Running the code

To run the code, first create the data and output directories:

    mkdir {data,output}
    
Then copy the data to be analysed into the data directory. Then, start the docker container with:

    bash runcontainer.sh
    
This assumes that the data and output directories exist, and that you're running it from the project root directory. You can then run the analysis on a pair of files with, e.g.:

    cd /output
    python /code/scripts/profile_lines.py /data/kymograph_file.png /data/lines_file.png
    
The script currently writes its output to the working directory. In the container, this will be ``/output``, outside the container it will be the output directory you created earlier (``output/`` from the root of the project).

## Analysis

To plot a single output CSV:

    Rscript analysis/plot-line.R output/series_0.csv s0.png

