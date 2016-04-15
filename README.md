# Profile lines

Measure intensity from one image based on a set of lines drawn in another.

## Running the code

To run the code, first create the data and output directories:

    mkdir {data,output}
    
Then copy the data to be analysed into the data directory. Then, start the
docker container with:

    bash runcontainer.sh
    
This assumes that the data and output directories exist, and that you're
running it from the project root directory. You can then run the analysis on a
pair of files with, e.g.:

    cd /output
    python /code/profile_lines.py /data/kymograph_file.png /data/lines_file.png
    
The script currently writes its output to the working directory. In the
container, this will be ``/output``, outside the container it will be the
output directory you created earlier (``output/`` from the root of the
project).

## Options

It is possible to specify the degree to which the skeletonized line gets
dilated using the ``-d``/``--dilation`` option.

Two methods for reducing the y-axis have been implemented: max and mean. The
desired option can be specified using the ``-r``/``--reduce-method`` option.

For more help use the ``-h``/``--help`` option.

## Analysis

To plot a single output CSV:

    Rscript analysis/individual-line-plot.R output/series_00.csv s0.png

To plot all output:

    Rscript analysis/all-series-plot.R output/all_series.csv all.png
