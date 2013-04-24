#!/usr/bin/env python
import argparse
import glob
import os
import shutil
import sys

from PIL import Image

try: import timing # Optional, http://stackoverflow.com/a/1557906/724176
except: None

# Python/PIL version of eirikmagick.sh

def sanity_check(files):
    num_files = len(files)
    print "Input images:\t", num_files
    if num_files < 2:
        sys.exit("Not enough input images")

def make_image(files):
    outfile = args.outfile
    # Assume all images are the same dimension
    in_width, in_height = Image.open(files[0]).size

    if args.direction == "vertical" or args.direction == "v":
        vertical = True
        horizontal = False
        number_of_slices = in_width
    elif args.direction == "horizontal" or args.direction == "h":
        vertical = False
        horizontal = True
        number_of_slices = in_height

    if args.greedy:
        number_of_slices = len(files)
    elif len(files) > number_of_slices:
        print "WARNING: Too many input files. Only", number_of_slices, "will be used (picked proportionally)."
        # files = files[:number_of_slices]
        chosen = []
        ratio = len(files)/float(number_of_slices)
        for i in range(0, number_of_slices):
            chosen.append(files[int(i*ratio)]) # pick proportionally
        files = chosen # update original list

    print "In width:\t", in_width
    print "In height:\t", in_height

    if args.thickness:
        slice_thickness = args.thickness
    else:
        slice_thickness = number_of_slices / len(files)

    if vertical:
        print "Slice width:\t", slice_thickness
        out_width = slice_thickness*len(files)
        out_height = in_height
        print "Out width:\t", out_width
        upper = 0
        lower = in_height
    elif horizontal:
        print "Slice height:\t", slice_thickness
        out_width = in_width
        out_height = slice_thickness*len(files)
        print "Out height:\t", out_height
        left = 0
        right = in_width
        
    # Reset width and height for greedy eirkismagick; don't want to go off the edge
    if args.mode == "eiriksmagick":
        out_width = in_width
        out_height = in_height

    if args.mode == "fixed":
        if vertical:
            left = (in_width * args.fixedposition/100) - (slice_thickness * args.fixedposition/100)
            right = left + slice_thickness
        elif horizontal:
            upper = (in_height * args.fixedposition/100) - (slice_thickness * args.fixedposition/100)
            lower = upper + slice_thickness

    if args.mode == 'all':
        loops = number_of_slices
    else:
        loops = 1

    img_cache = []
    for j in range(loops):
        print "Creating:\t" + str(j+1) + "/" + str(loops)
        if args.mode == 'all':
            if vertical:
                left = in_width*j/loops - slice_thickness/2
                right = left + slice_thickness
            elif horizontal:
                upper = in_height*j/loops - slice_thickness/2
                lower = upper + slice_thickness
            outfile = args.outfile + "-" + str(j).zfill(6) + ".jpg"

        if os.path.exists(outfile):
            print "File exists, skipping:", outfile
            continue
        
        # Create the new image. The background doesn't have to be white
        white = (255,255,255)
        inew = Image.new('RGB', (out_width, out_height), white)

        if args.mode != "eiriksmagick":
            crop_bbox = (left, upper, right, lower)

        for i, file in enumerate(files):
            sys.stdout.write('\rProcessing file ' + str(i+1) + "/" + str(len(files)))
            if vertical:
                left = i * slice_thickness
                right = left + slice_thickness
            elif horizontal:
                upper = i * slice_thickness
                lower = upper + slice_thickness
            paste_bbox = (left, upper, right, lower)
            if args.mode == "eiriksmagick":
                crop_bbox = paste_bbox
            # print bbox
            # try:
                # # Read in an image and resize appropriately

            # TODO when caching
            # 1. chop image, and only keep remainder in cache
            # 2. can then add more stuff to cache

            if (crop_bbox[2] > in_width) or (crop_bbox[3] > in_height):
                # Don't if crop_box is outside the image
                continue
                
            if len(img_cache) > i:
                # print "load from cache"
                img = img_cache[i].crop(crop_bbox)
            elif loops > 1 and i < args.cache:
                # print "add to cache"
                img_cache.append(Image.open(file))
                # img = img.crop(crop_bbox)
                img = img_cache[i].crop(crop_bbox)
            else:
                # print "don't use cache"
                img = Image.open(file).crop(crop_bbox)

            # except:
                # break
            inew.paste(img, paste_bbox)
            # count += 1
        sys.stdout.write('\r\n')

        print "Saving to", outfile
        inew.save(outfile, quality=100)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Slice input files into an output file. Requires PIL.', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-i', '--inspec', default='*.jpg',
        help='Input file spec')
    parser.add_argument('-o', '--outfile', help='Output file name')
    parser.add_argument('-m', '--mode', default='eiriksmagick', choices=('eiriksmagick', 'fixed', 'all'),
        help="How to slice images. 'fixed' takes slices from a fixed position in each image (e.g. the centre), 'eiriksmagick' takes a different slice from each, moving from left to right (or top to bottom). Both create a single image. 'all' makes lots of image, each with slices from the same place.")
    parser.add_argument('-p', '--fixedposition', type=int, default=50,
        help="When using `--mode fixed`, this is the percentage across the image to take slice.")
    parser.add_argument('-d', '--direction', default='vertical', choices=('vertical', 'v', 'horizontal', 'h'),
        help="Direction to slitify")
    parser.add_argument('-t', '--thickness', type=int,
        help="Slit thickness in pixels. Default is to calculate based on number of input images.")
    parser.add_argument('-g', '--greedy', action='store_true',
        help="Use every input file even if more than the width or height")
    parser.add_argument('-c', '--cache', type=int,
        help="Load this many images into memory, the rest will be read on demand from disk (for: --mode all)")
    args = parser.parse_args()
    print args

    files = glob.glob(args.inspec)
    sanity_check(files)
    if not args.outfile:
        args.outfile = "out-" + args.direction + "-" + args.mode + ".jpg"
    make_image(files)

# End of file