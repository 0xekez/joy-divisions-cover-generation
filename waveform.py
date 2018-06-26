from scipy.io import wavfile
import numpy as np
import sys
from PIL import Image, ImageDraw

from noise_gen import add_noise
from params import params
from images_to_video import images_to_video, add_audio

import time
start_time = time.time()

# returns first channel
def get_amplitudes(file):
    rate, data = wavfile.read(file)

    # normalize values between 0 and 200
    norm_data = np.copy(data)
    norm_data = norm_data/(norm_data.max()/125)

    list = np.ndarray.tolist(norm_data.astype(int))
    print("GOT\t{}".format(file))
    return rate, list if isinstance(list[0], int) else [l[0] for l in list]


# returns new array with spacer Nones betwen each element
def space_array(array, spacers):
    b = []
    spacer = [None for _ in range(spacers)]
    for item in array:
        b.extend([item]+spacer)
    return b


# splits array into smaller arrays of size items_split
# throws out scragglers at the end if array can't be evenly split
def split_array(a, items_split):
    n_splits = len(a)//items_split
    splits = []
    for _ in range(n_splits):
        splits.append(a[len(splits)*items_split:(len(splits)+1)*items_split])
    return splits


def zero_at_b(a, b):
    return [c-b for c in a]


# add a wave to an image, with a given offset from the top
def add_wave(amps, spacers, offset, image, draw, x_shift, y_shift):
    # add noise
    mean = np.mean(amps)
    amps = add_noise(amps, mean)
    amps = zero_at_b(amps, mean)
    # space out amps
    spaced_amps = space_array(amps, spacers)

    max_y_amps = max(amps)+params['offset']

    for x in range(len(spaced_amps)-spacers-1):
        if spaced_amps[x]:

            line_start_x = x + x_shift
            line_start_y = offset + spaced_amps[x] + y_shift
            line_end_x = x + spacers + 1 + x_shift
            line_end_y = offset + spaced_amps[x + spacers + 1] + y_shift

            polygon_bottom_y = 3*offset+max_y_amps + y_shift

            draw.polygon((
                            (line_start_x, line_start_y),
                            (line_end_x, line_end_y),
                            (line_end_x, polygon_bottom_y),
                            (line_start_x, polygon_bottom_y)),
                            fill=0, outline=0)
            draw.line((line_start_x, line_start_y, line_end_x, line_end_y),
                        fill=255, width=params['line_width'])

    return image


def build_album_cover(amps, start, n_data_needed, im_width, im_height):

    amps = amps[start: start+n_data_needed]

    splits = split_array(amps, params['data_line'])

    n_waves = len(splits)
    offset = params['offset']

    im = Image.new('1', (im_width, im_height))
    draw = ImageDraw.Draw(im)

    x_shift = im_width//4
    y_shift = (im_height-(offset*n_waves))//2

    for i in range(n_waves):
        im = add_wave(splits[i], params['spacers'], offset*(i), im, draw, x_shift, y_shift)

    save = params['save_loc'].split('.')
    save = save[0]+str(start)+'.'+save[-1]

    im.save(save)
    return save


file = params['file'] if len(sys.argv) < 2 else sys.argv[1]
rate, amps = get_amplitudes(file)
frame_rate = params['fps']
# both are ints so using // should return an int
rate_div_fps = rate//frame_rate
# the number of items (frames) in iteration_list is determined by
# items < len(amps)/rate_div_fps or len(amps)//rate_div_fps
# so..
n_frames = len(amps)//rate_div_fps
iteration_list = [i*rate_div_fps for i in range(n_frames)]

print("BUILDING {} IMAGES".format(n_frames))

# precalculate some things for build_album_cover
n_data_needed = params['data_line']*params['n_lines']
im_width = (params['spacers']+1)*(2*(params['noise_frac']*params['data_line'])+params['data_line'])*2
im_height = int(im_width/0.85)

filenames = []

for i, loc in zip(iteration_list, range(n_frames)):
    filenames.append(build_album_cover(amps, i, n_data_needed, im_width, im_height))
    print("BUILT:\t{}/{}".format(loc, n_frames))

out_file = params['vid_save']

out_file = images_to_video(filenames, out_file, frame_rate)
add_audio(out_file, params['file'])

print("EXEC TIME:\t{} seconds".format(time.time() - start_time))
