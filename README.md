# Joy Division - Unknown Pleasures 3D painting


SVG from: http://cococubed.asu.edu/pix_pages/joy_division_unknown_pleasures.shtml

Download link: http://cococubed.asu.edu/images/unknown_pleasures/cp1919_unknown_pleasures_white.svg

# Prep

Build docker container that has pymesh and sklearn (used for K-means in step 3)

`docker build -t pymesh-unknown-pleasures .`

NOTE! The docker container is based on `pymesh/pymesh` and image id `967a56ffb4e7` was used when developing these scripts

# Run

`docker run -it --rm -v $PWD:/models pymesh-unknown-pleasures`

## Run in steps

Before running steps, ensure the directory `tilted/` exists

1. `docker run -it --rm -v $PWD:/models pymesh-unknown-pleasures python /models/tilt_process.py` - read `original/drawing-3.svg` and produces files in `tilted/` (one stl per squiggle and intersect2.stl)
2. `docker run -it --rm -v $PWD:/models pymesh-unknown-pleasures python /models/next_gen.py` - combines squiggles to `unknown_pleasures_positive.stl`
3. `docker run -it --rm -v $PWD:/models pymesh-unknown-pleasures python /models/next_gen_moulds.py` - produce inner and outer moulds from the positive (`unknown_pleasures_inner_mould.stl` and `unknown_pleasures_outer_mould.stl`)
