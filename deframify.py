#!/usr/bin/env python
"""
Wrapper around ffmpeg to animate frames into a video.
"""
import argparse
import os

# This uses ffmpeg:
# http://ffmpeg.org/trac/ffmpeg/wiki/Create%20a%20video%20slideshow%20from%20images

# To use mencoder:
# http://www.trevorshp.com/photography/timelapse_videos/timelapse_howto.htm
# call "C:\Program Files\MPlayer\mencoder" mf://*.jpg -mf fps=%framerate%:type=jpeg -noskip -of lavf -lavfopts format=%outformat% -ovc lavc -lavcopts vglobal=1:coder=0:vcodec=libx264:vbitrate=%bitrate% -vf eq2=1.2:0.9:0.0:1.0 -o %outfile%-%framerate%fps.%outformat%

# Example for Windows if no glob:
# ffmpeg -f image2 -i %4d.jpg -r 25 -c:v libx264 ..\outfile.mp4

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Wrapper around ffmpeg to animate frames into a video.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        '-i', '--inspec', metavar='spec',
        default='*.jpg',
        help='Image files to animate')
    parser.add_argument(
        '-r', '--framerate', metavar='fps',
        default=25, type=int,
        help='Framerate')
    parser.add_argument(
        '-o', '--outfile', metavar='filename',
        default='timelapse.mp4',
        help='Output video filename')
    args = parser.parse_args()
    print(args)

    cmd = "ffmpeg -f image2 -pattern_type glob -r " + str(args.framerate) + \
        " -i '" + args.inspec + "' -c:v libx264 " + args.outfile
    print(cmd)
    os.system(cmd)

# End of file
