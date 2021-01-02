# Joy Division - Unknown Pleasures 3D painting


SVG from: http://cococubed.asu.edu/pix_pages/joy_division_unknown_pleasures.shtml

Download link: http://cococubed.asu.edu/images/unknown_pleasures/cp1919_unknown_pleasures_white.svg

# Prep

Build docker container that has pymesh and sklearn (used for K-means in step 3)

`docker build -t pymesh-unknown-pleasures .`

# Run

`docker run -it --rm -v $PWD:/models pymesh-unknown-pleasures`

## Run in steps

Before running steps, ensure the directory `tilted/` exists

1. `docker run -it --rm -v $PWD:/models pymesh-unknown-pleasures python /models/tilt_process.py` - read `original/drawing-3.svg` and produces files in `tilted/` (one stl per squiggle and intersect2.stl)
2. `docker run -it --rm -v $PWD:/models pymesh-unknown-pleasures python /models/next_gen.py` - combines squiggles to `next_gen_output.stl`
3. `docker run -it --rm -v $PWD:/models pymesh-unknown-pleasures python /models/next_gen_extrude.py` - extrude previous output to `next_gen_output_extruded.stl`

try to remove the bottom and extrude the top face down



NEXT: create `shell` (=inner flexible mould) for object. To do this, do not attempt to create a shell, but instead create box for the outer mould, then carve out the "slot" for the inner mould and use boolean operators to formulate the "shell"