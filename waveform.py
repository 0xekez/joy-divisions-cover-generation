from scipy.io import wavfile
import numpy as np
from PIL import Image, ImageDraw

from noise_gen import add_noise
from params import params
from images_to_video import images_to_video, add_audio

import time
start_time = time.time()


def get_amplitudes(file):
    '''
    gets audio data from file
    IN: filename
    OUT: sample rate (bits/sec) [int], first channel amplitudes [list of ints]
    '''
    rate, data = wavfile.read(file)

    # normalize values between 0 and params['scale_val']
    norm_data = np.copy(data)
    norm_data = norm_data/(norm_data.max()/params['scale_val'])

    list = np.ndarray.tolist(norm_data.astype(int))
    print("GOT\t{}".format(file))
    return rate, list if isinstance(list[0], int) else [l[0] for l in list]


def split_array(a, items_split):
    '''
    returns max num of lists of size items_split from input list
    IN: array to be split, number of items in each split
    OUT: list of splits [list of lists]
    WARNING: throws out scragglers if items_split doesnt go evenly into input
    '''
    n_splits = len(a)//items_split
    splits = []
    for _ in range(n_splits):
        splits.append(a[len(splits)*items_split:(len(splits)+1)*items_split])
    return splits


def zero_at_b(a, b):
    '''
    makes b 0 of input list a
    IN: list to be adjusted, value to be new zero
    OUT: adjusted list
    '''
    return [c-b for c in a]


def add_wave(amps, y_offset, image, draw, x_shift, indexes, x_cords):
    '''
    adds a wave to given image. build from given data with given offsets
    IN: amplitude data, y offset, image, draw obj for image, x offset,
        places to index amps, unadjusted x cords for drawing
    NOTE: indexes and x_cords are passed only to make program faster
    '''
    # add noise
    mean = np.mean(amps)
    amps = add_noise(amps, mean)
    amps = zero_at_b(amps, mean)

    for i, x in zip(indexes, x_cords):

        line_start_x = x + x_shift
        line_start_y = y_offset + amps[i]
        line_end_x = x + params['spacers'] + x_shift
        line_end_y = y_offset + amps[i+1]

        polygon_bottom_y = y_offset+params['scale_val']

        draw.polygon(
                        (
                            (line_start_x, line_start_y),
                            (line_end_x, line_end_y),
                            (line_end_x, polygon_bottom_y),
                            (line_start_x, polygon_bottom_y)
                        ),
                        fill=0,
                        outline=0)
        draw.line(
                    (line_start_x, line_start_y, line_end_x, line_end_y),
                    fill=255,
                    width=params['line_width']
                  )

    return image


def build_album_cover(amps, loc, im_width, im_height, indexes, x_cords):
    '''
    builds an ablum cover image that is later used as a frame
    IN: amplitude data, what number frame, width of image, height of image,
        indexes for passing to add_wave, x_cords for same reason
    OUT: the save location of the frame
    '''
    splits = split_array(amps, params['data_line'])

    n_waves = len(splits)
    offset = params['offset']

    im = Image.new('1', (im_width, im_height))
    draw = ImageDraw.Draw(im)

    x_shift = im_width//4
    y_shift = (im_height-(offset*n_waves))//2

    for i in range(n_waves):
        im = add_wave(splits[i], offset*(i)+y_shift, im, draw, x_shift, indexes, x_cords)

    save = params['save_loc'].split('.')
    save = save[0]+str(loc)+'.'+save[-1]

    im.save(save)
    return save


rate, amps = get_amplitudes(params['file'])
frame_rate = params['fps']

# both are ints so using // should return an int
rate_div_fps = rate//frame_rate

# the number of items (frames) in iteration_list is determined by
# items < len(amps)/rate_div_fps or len(amps)//rate_div_fps
n_frames = len(amps)//rate_div_fps
iteration_list = [i*rate_div_fps for i in range(n_frames)]

print("BUILDING {} IMAGES".format(n_frames))

# precalculate some things for build_album_cover
n_data_needed = params['data_line']*params['n_lines']
im_width = (params['spacers']+1)*(2*(params['noise_frac']*params['data_line'])+params['data_line'])*2
im_height = int(im_width/0.85)

# precalculate the indexes and x cords for drawing for add_wave
indexes = range(0, (params['data_line']*(2*params['noise_frac']+1)-1))
x_cords = [i*(params['spacers']+1) for i in indexes]

filenames = []

for i, loc in zip(iteration_list, range(n_frames)):
    filenames.append(build_album_cover(amps[i:i+n_data_needed], loc, im_width, im_height, indexes, x_cords))
    print("BUILT:\t{}/{}".format(loc, n_frames))

out_file = params['vid_save']

out_file = images_to_video(filenames, out_file, frame_rate)
add_audio(out_file, params['file'])

print("EXEC TIME:\t{} seconds".format(time.time() - start_time))
