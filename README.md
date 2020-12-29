# Joy Division - Unknown Pleasures 3D painting


SVG from: http://cococubed.asu.edu/pix_pages/joy_division_unknown_pleasures.shtml

Download link: http://cococubed.asu.edu/images/unknown_pleasures/cp1919_unknown_pleasures_white.svg



# Steps

1. tilt_process.py (??) - read `original/drawing-3.svg` and produces files in `tilted/` (one stl per squiggle and intersect2.stl)
2. `docker run -it --rm -v `pwd`:/models pymesh/pymesh python /models/next_gen.py` - combines squiggles to `next_gen_output.stl`
3. `docker run -it --rm -v `pwd`:/models pymesh-sklearn python /models/next_gen_extrude.py ` - extrude previous output to `next_gen_output_extruded.stl`

